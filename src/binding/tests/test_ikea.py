import pytest
import asyncio
from binding.app import create_app
from unittest.mock import patch, call, MagicMock
from aiocoap.numbers.codes import GET, PUT

class Response(object):
    def __init__(self, payload):
        self.payload = payload
class Request(object):
    def __init__(self, data):
        self.response = asyncio.Future()
        self.response.set_result(Response(data))

@pytest.fixture
def context():
    with patch('binding.ikea.Context', autospec=True) as mock_context:
        mock_context.return_value.client_credentials = MagicMock()
        mock_context.create_client_context.return_value = asyncio.Future()
        mock_context.create_client_context.return_value.set_result(mock_context())
        yield mock_context

@pytest.fixture
def message():
    with patch('binding.ikea.Message') as mock_message:
        yield mock_message

@pytest.fixture
def app(context, message):
    context.return_value.request.side_effect = [
        Request(b'[12345]'),
        Request(b'{"9001":"TRADFRI outlet", "3312":[{"5850":1}]}'),
    ]
    app = create_app({
        'TESTING': True,
        'BINDINGS': ['ikea'],
        'HOSTNAME': 'http://localhost:5000',
    })

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_discover(client, message):
    client.get('/')
    calls = [
        call(code=GET, uri='coaps://192.168.3.100:5684/15001'),
        call(code=GET, uri='coaps://192.168.3.100:5684/15001/12345')
    ]
    message.assert_has_calls(calls)

def test_get_status(client, context, message):
    context.return_value.request.side_effect = [Request(b'{"9001":"TRADFRI outlet", "3312":[{"5850":1}]}')]
    response = client.get('/ikea:12345/state')

    assert response.status_code == 200
    assert response.get_json() == {
        'state': 1
    }
    message.assert_called_with(code=GET, uri='coaps://192.168.3.100:5684/15001/12345')

def test_set_status_on(client, context, message):
    context.return_value.request.side_effect = [Request(b'{}')]
    response = client.post('/ikea:12345/state', json={
        'state': 1
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'updated'
    }

    message.assert_called_with(code=PUT, payload=b'{"3311":[{"5850":1}]}', uri='coaps://192.168.3.100:5684/15001/12345')

def test_set_status_off(client, context, message):
    context.return_value.request.side_effect = [Request(b'{}')]
    response = client.post('/ikea:12345/state', json={
        'state': 0
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'updated'
    }

    message.assert_called_with(code=PUT, payload=b'{"3311":[{"5850":0}]}', uri='coaps://192.168.3.100:5684/15001/12345')


def test_get_td(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_json() == [{
        'id': 'urn:ikea:12345',
        'name': 'TRADFRI outlet',
        'security': [],
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
        'events': {}
    }]
