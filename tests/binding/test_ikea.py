"""Pytests for IKEA binding template"""
# pylint: disable=redefined-outer-name, unused-import, unused-argument
# Disabled as pylint does not detect pytest fixtures imported from another file

from unittest.mock import call
import pytest
from aiocoap.numbers.codes import GET, PUT
from wot.binding.app import create_app
from wot.common.coap_fixtures import Request, context, message

@pytest.fixture
def app(context, message):
    """Test flask app fixture

    Specifies sample return data for CoAP requests and configuration info
    """
    context.return_value.request.side_effect = [
        Request(b'[12345]'),
        Request(b'{"9001":"TRADFRI outlet", "9003":"12345", "3312":[{"5850":1}]}'),
    ]
    app = create_app({
        'TESTING': True,
        'BINDINGS': ['ikea'],
        'HOSTNAME': 'http://localhost:5000',
        'IKEA': {
            'gateway': '192.168.3.100',
            'psk': 'test',
            'identity': 'test',
        }
    })

    return app

@pytest.fixture
def client(app):
    """Flask client fixture"""
    return app.test_client()

def test_discover(client, message):
    """Tests the discovery method

    Ensures that the gateway listing is retrieved and then the info for each device
    """
    client.get('/')
    calls = [
        call(code=GET, uri='coaps://192.168.3.100:5684/15001'),
        call(code=GET, uri='coaps://192.168.3.100:5684/15001/12345')
    ]
    message.assert_has_calls(calls)

def test_get_status(client, context, message):
    """Tests that the get status endpoint returns the correct state and data"""
    context.return_value.request.side_effect = [
        Request(b'{"9001":"TRADFRI outlet", "3312":[{"5850":1}]}')
    ]
    response = client.get('/ikea:12345/state')

    assert response.status_code == 200
    assert response.get_json() == {
        'state': 1
    }
    message.assert_called_with(code=GET, uri='coaps://192.168.3.100:5684/15001/12345')

def test_set_status_on(client, context, message):
    """Tests the set status endpoint when 1 is inputted"""
    context.return_value.request.side_effect = [Request(b'{}')]
    response = client.post('/ikea:12345/state', json={
        'state': 1
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'updated'
    }

    message.assert_called_with(code=PUT, payload=b'{"3311":[{"5850":1}]}',
                               uri='coaps://192.168.3.100:5684/15001/12345')

def test_set_status_off(client, context, message):
    """Tests the set status endpoint when 0 is inputted"""
    context.return_value.request.side_effect = [Request(b'{}')]
    response = client.post('/ikea:12345/state', json={
        'state': 0
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'updated'
    }

    message.assert_called_with(code=PUT, payload=b'{"3311":[{"5850":0}]}',
                               uri='coaps://192.168.3.100:5684/15001/12345')


def test_get_td(client):
    """Tests that the thing description is correct"""
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_json() == [{
        'id': 'urn:ikea:12345',
        'name': 'TRADFRI outlet',
        'properties': {
            'state': {
                'forms': [{
                    'href': 'http://localhost:5000/ikea:12345/state',
                    'contentType': 'application/json'
                }],
                'type': 'object',
                'properties': {
                    'state': {
                        'type': 'number'
                    }
                }
            },

        },
        'actions': {
            'setState': {
                'forms': [{
                    'href': 'http://localhost:5000/ikea:12345/state',
                    'contentType': 'application/json'
                }],
                'input': {
                    'type': 'object',
                    'properties': {
                        'state': {
                            'type': 'number'
                        }
                    }
                },
                'output': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string'
                        }
                    }
                }
            }
        },
        'events': {},
        'security': ['bearer_token'],
        'securityDefinitions': {
            'bearer_token': {
                'scheme': 'bearer',
                'alg': 'HS256',
                'in': 'header',
                'name': 'Authorization'
            }
        },
    }]
