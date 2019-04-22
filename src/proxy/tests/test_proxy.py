"""Pytests for proxy module"""
# pylint: disable=redefined-outer-name, unused-import, unused-argument
# Disabled this checker as it conflicts with pytest fixtures
import asyncio
import os
from unittest.mock import patch
import pytest
from requests.exceptions import Timeout
from aiocoap.numbers.codes import GET
from proxy.app import create_app
from proxy import proxy
from common.db import get_db, close_db
from common.coap_fixtures import Request, context, message

@pytest.fixture
def app():
    """Fixture of the Flask API with sample configuration"""
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
    """API testing client"""
    return app.test_client()

@pytest.fixture
def requests():
    """Mock for requests library"""
    with patch('requests.get', autospec=True) as mock_requests:
        yield mock_requests

@pytest.fixture
def redis():
    """Mock for redis connection handler"""
    with patch('redis.Redis', autospec=True) as mock_redis:
        mock_redis.return_value.exists.return_value = False
        yield mock_redis

def test_add(client):
    """Tests adding a new endpoint"""
    response = client.post('/proxy/add', json={
        'url': 'http://example.com'
    })
    assert response.status_code == 201

    get_response = client.get('/proxy/{}/details'.format(response.get_json()['uuid']))
    assert get_response.status_code == 200
    assert get_response.get_json() == {
        'url': 'http://example.com'
    }

def test_details(client):
    """Tests getting details for an endpoint"""
    response = client.get('/proxy/123/details')

    assert response.status_code == 200
    assert response.get_json() == {
        'url': 'http://example.com'
    }

def test_details_404(client):
    """Tests trying to get details for unknown endpoint"""
    response = client.get('/proxy/456/details')

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Endpoint not found',
    }

def test_request(client, requests, redis):
    """Tests performing an HTTP proxy"""
    response = client.get('/proxy/123')

    redis.assert_called_once()
    assert response.status_code == 200
    requests.assert_called_once()
    redis.return_value.exists.assert_called_once_with('123')
    redis.return_value.hset.assert_called()
    redis.return_value.expire.assert_called_once()

def test_request_in_cache(client, requests, redis):
    """Tests performing a cache lookup"""
    redis.return_value.exists.return_value = True
    response = client.get('/proxy/123')

    assert response.status_code == 200
    requests.assert_not_called()
    redis.return_value.hget.assert_called()

def test_request_404(client):
    """Tests attempting to proxy an unknown endpoint"""
    response = client.get('/proxy/456')

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Endpoint not found',
    }

def test_request_504(client, requests, redis):
    """Tests handling of failed proxy"""
    requests.side_effect = Timeout()
    response = client.get('/proxy/123')

    assert response.status_code == 504
    assert response.get_json() == {
        'message': 'Cannot reach thing'
    }

def test_coap_request(client, context, message, redis):
    """Tests performing a CoAP proxy"""
    context.return_value.request.side_effect = [Request(b'output')]
    response = client.get('/proxy/coap')

    assert response.status_code == 200
    assert response.data == b'output'
    message.assert_called_with(code=GET, uri='coap://example.com')

def test_update(client):
    """Tests updating an endpoint"""
    response = client.put('/proxy/123', json={
        'url': 'http://test.xyz'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'Updated'
    }

    update_response = client.get('/proxy/123/details')
    assert update_response.get_json() == {
        'url': 'http://test.xyz'
    }

def test_update_404(client):
    """Tests attempting to update endpoint that doesnt exist"""
    response = client.put('/proxy/456', json={
        'url': 'http://test.xyz'
    })

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Endpoint not found',
    }
