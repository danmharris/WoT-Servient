import pytest
import os
from unittest.mock import patch
from proxy.app import create_app
from proxy import proxy
from common.db import get_db, close_db
from requests.exceptions import Timeout, ConnectionError
import asyncio
from aiocoap.numbers.codes import GET

#TODO: Test that these endpoints actually save into the database
# Retrieve database after request made and check contents

class Response(object):
    def __init__(self, payload):
        self.payload = payload
class Request(object):
    def __init__(self, data):
        self.response = asyncio.Future()
        self.response.set_result(Response(data))

@pytest.fixture
def context():
    with patch('aiocoap.Context', autospec=True) as mock_context:
        mock_context.create_client_context.return_value = asyncio.Future()
        mock_context.create_client_context.return_value.set_result(mock_context())
        yield mock_context

@pytest.fixture
def message():
    with patch('aiocoap.Message', autospec=True) as mock_message:
        yield mock_message

@pytest.fixture
def app():
    db_path = 'test.db'

    app = create_app({
        'TESTING': True,
        'DB': db_path,
        'REDIS': False,
    })

    with app.app_context():
        s = get_db()
        s['123'] = 'http://example.com'
        s['coap'] = 'coap://example.com'
        close_db()

    yield app

    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def requests():
    with patch('requests.get', autospec=True) as mock_requests:
        yield mock_requests

@pytest.fixture
def redis():
    with patch('redis.Redis', autospec=True) as mock_redis:
        mock_redis.return_value.exists.return_value = False
        yield mock_redis

def test_add(client):
    response = client.post('/proxy/add', json={
        'url': 'http://example.com'
    })
    assert response.status_code == 201

def test_details(client):
    response = client.get('/proxy/123/details')

    assert response.status_code == 200
    assert response.get_json() == {
        'url': 'http://example.com'
    }

def test_details_404(client):
    response = client.get('/proxy/456/details')

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Endpoint not found',
    }

def test_request(client, requests, redis):
    response = client.get('/proxy/123')

    redis.assert_called_once()
    assert response.status_code == 200
    requests.assert_called_once()
    redis.return_value.exists.assert_called_once_with('123')
    redis.return_value.hset.assert_called()
    redis.return_value.expire.assert_called_once()

def test_request_in_cache(client, requests, redis):
    redis.return_value.exists.return_value = True
    response = client.get('/proxy/123')

    assert response.status_code == 200
    requests.assert_not_called()
    redis.return_value.hget.assert_called()

def test_request_404(client):
    response = client.get('/proxy/456')

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Endpoint not found',
    }

def test_request_504(client, requests, redis):
    requests.side_effect = Timeout()
    response = client.get('/proxy/123')

    assert response.status_code == 504
    assert response.get_json() == {
        'message': 'Cannot reach thing'
    }

def test_coap_request(client, context, message, redis):
    context.return_value.request.side_effect = [Request(b'output')]
    response = client.get('/proxy/coap')

    assert response.status_code == 200
    assert response.data == b'output'
    message.assert_called_with(code=GET, uri='coap://example.com')

def test_update(client):
    response = client.put('/proxy/123', json={
        'url': 'http://test.xyz'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'Updated'
    }

def test_update_404(client):
    response = client.put('/proxy/456', json={
        'url': 'http://test.xyz'
    })

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Endpoint not found',
    }
