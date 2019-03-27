from thing_directory.app import create_app
from .data import data
from common.db import get_db, close_db
import pytest
import tempfile
import shelve
import os
from unittest.mock import patch
import requests
from flask import Response
from common.coap_fixtures import Request, context, message
from aiocoap.numbers.codes import GET

@pytest.fixture
def app():
    db_path = 'test.db'

    app = create_app({
        'TESTING': True,
        'DB': db_path,
        'PROXY': 'http://localhost',
    })

    with app.app_context():
        s = get_db()
        for key in data:
            s[key] = data[key]
        close_db()

    yield app

    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_things(client):
    """ Test the /things GET request """
    response = client.get('/things')
    assert response.status_code == 200
    assert response.get_json() == data

def test_thing_uuid(client):
    """ Test /things/<uuid> GET request where the UUID exists """
    response = client.get('/things/123')
    assert response.status_code == 200
    assert response.get_json() == data['123']

def test_thing_uuid_404(client):
    """ Test /things/<uuid> GET request where the UUID doesn't exist """
    response = client.get('/things/abc')
    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Thing not found',
    }

def test_query_groups(client):
    """ Test /things/query GET request with match """
    response = client.get('/things/query?groups=group1')
    assert response.status_code == 200
    print(response.get_json())
    assert response.get_json() == {
        '456': {
            'name': 'test2',
            'groups': ['group1']
        }
    }

def test_query_groups_none(client):
    """ Test /things/query with no match """
    response = client.get('/things/query?groups=group2')
    assert response.status_code == 200
    assert response.get_json() == {}

def test_register(client):
    """ Test /things/register POST endpoint """
    with patch('requests.post', autospec=True) as mock_requests:
        mock_requests.return_value.json.return_value = {'uuid': '123456'}
        response = client.post('/things/register',
            json={
                'schema': {
                    'name': 'test3'
                },
                'properties': {
                    'status': {
                        'forms': [{
                            'href': 'http://example.com'
                        }]
                    }
                }
            },
            headers={
                'Authorization': 'bearer token',
            })
        assert response.status_code == 201
        mock_requests.assert_called_once_with('http://localhost/proxy/add', json={
            'url': 'http://example.com'
        }, headers={'Authorization': 'bearer token'})

        get_response = client.get('/things/{}'.format(response.get_json()['uuids'][0]))
        assert get_response.get_json() == {
            'schema': {
                'name': 'test3'
            },
            'properties': {
                'status': {
                    'forms': [{
                        'href': 'http://localhost/proxy/123456'
                    }]
                }
            }
        }

def test_register_observable(client):
    """ Test /things/register with an endpoint that should not be proxied """
    with patch('requests.post', autospec=True) as mock_requests:
        mock_requests.return_value.json.return_value = {'uuid': '123456'}
        response = client.post('/things/register',
            json={
                'schema': {
                    'name': 'test3'
                },
                'properties': {
                    'status': {
                        'observable': True,
                        'forms': [{
                            'href': 'coap://example.com'
                        }]
                    }
                }
            })
        assert response.status_code == 201
        mock_requests.assert_not_called()

        get_response = client.get('/things/{}'.format(response.get_json()['uuids'][0]))
        assert get_response.get_json() == {
            'schema': {
                'name': 'test3'
            },
            'properties': {
                'status': {
                    'observable': True,
                    'forms': [{
                        'href': 'coap://example.com'
                    }]
                }
            }
        }

def test_register_multiple(client):
    """ Test/things/register with multiple descriptions """
    with patch('requests.post', autospec=True):
        response = client.post('/things/register',
        json=[
            {'name': 'test4'},
            {'name': 'test5'},
        ])

        assert response.status_code == 201
        assert len(response.get_json()['uuids']) == 2

        for uuid in response.get_json()['uuids']:
            get_response = client.get('/things/{}'.format(uuid))
            assert get_response.status_code == 200

def test_register_timeout(client):
    """ Test /things/register endpoint when proxy cannot be reached """
    with patch('requests.post', autospec=True) as mock_requests:
        mock_requests.side_effect = requests.exceptions.Timeout()
        response = client.post('/things/register',
            json={
                'schema': {
                    'name': 'test3'
                },
                'properties': {
                    'status': {
                        'forms': [{
                            'href': 'http://example.com'
                        }]
                    }
                }
            })
        assert response.status_code == 504
        assert response.get_json() == {
            'message': 'Could not reach proxy'
        }

def test_register_url_http(client):
    with patch('requests.get', autospec=True) as mock_request:
        mock_request.return_value.json.return_value = {'name': 'test'}
        response = client.post('/things/register_url', json={
            'url': 'http://example.com',
        })

        assert response.status_code == 201
        mock_request.assert_called_once_with('http://example.com')

        get_response = client.get('/things/{}'.format(response.get_json()['uuids'][0]))
        assert get_response.status_code == 200
        assert get_response.get_json() == {'name': 'test'}

def test_register_url_coap(client, context, message):
    context.return_value.request.side_effect = [Request(b'{"name": "test"}')]
    response = client.post('/things/register_url', json={
        'url': 'coap://example.com',
    })

    assert response.status_code == 201
    message.assert_called_once_with(uri='coap://example.com', code=GET)

    get_response = client.get('/things/{}'.format(response.get_json()['uuids'][0]))
    assert get_response.status_code == 200
    assert get_response.get_json() == {'name': 'test'}

def test_register_url_coap_err(client, context, message):
    context.return_value.request.side_effect = [Request(b'not JSON')]
    response = client.post('/things/register_url', json={
        'url': 'coap://example.com',
    })

    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Error getting schema at URL'
    }

def test_register_url_missing(client):
    response = client.post('/things/register_url')
    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Missing data URL',
    }

def test_register_url_not_td(client):
    with patch('requests.get', autospec=True) as mock_request:
        mock_request.return_value.json.side_effect = ValueError()
        response = client.post('/things/register_url', json={
            'url': 'http://example.com',
        })

        assert response.status_code == 400
        mock_request.assert_called_once_with('http://example.com')
        assert response.get_json() == {
            'message': 'Error getting schema at URL'
        }

def test_register_url_no_protocol(client):
    response = client.post('/things/register_url', json={
        'url': 'smtp://example.com',
    })

    assert response.status_code == 501
    assert response.get_json() == {
        'message': 'Cannot parse this URL',
    }

def test_add_group(client):
    """ Test /things/<uuid>/groups POST request """
    initial_response = client.get('/things/123')
    assert initial_response.get_json() == data['123']

    update_response = client.post('/things/123/groups',
        json = {'group': 'group2'})
    assert update_response.get_json() == {
        'message': 'updated'
    }

    new_response = client.get('/things/123')
    assert new_response.get_json() == {
        **data['123'],
        'groups': ['group2']
    }

def test_add_group_404(client):
    """ Test /things/<uuid>groups POST request where thing doesnt exist """
    response = client.post('/things/abc/groups',
        json = {'group': 'group2'})
    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Thing not found',
    }

def test_delete_group(client):
    """ Test /things/<uuid>/groups<group> removes a group """
    initial_response = client.get('/things/456')
    assert initial_response.get_json()['groups'] == ['group1']
    response = client.delete('/things/456/groups/group1')
    assert response.get_json() == {
        'message': 'group removed'
    }
    new_response = client.get('/things/456')
    assert new_response.get_json()['groups'] == []

def test_delete_group_404(client):
    """ Test /things/<uuid>/groups/<group> 404s on nonexistent UUID """
    response = client.delete('/things/abc/groups/test')
    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Thing not found',
    }

def test_delete(client):
    """ Test /things/<uuid> DELETE request """
    initial_response = client.get('/things')
    assert '123' in initial_response.get_json()
    delete_response = client.delete('/things/123')
    assert delete_response.get_json() == {
        'message': 'deleted'
    }
    new_response = client.get('/things')
    assert '123' not in new_response.get_json()

def test_delete_404(client):
    """ Test /things/<uuid> DELETE request where thing doesnt exist """
    response = client.delete('/things/abc')
    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Thing not found',
    }
