"""Pytests for TP-LINK binding template"""
# pylint: disable=redefined-outer-name, unused-argument
# Disabled these checkers as they incorrectly mark pytest fixtures
from unittest.mock import MagicMock, patch
import pytest
from wot.binding.app import create_app

@pytest.fixture()
def smart_plug():
    """Fixture which stubs the PYHS100 methods for a smart plug"""
    with patch('wot.binding.tplink.SmartPlug', autospec=True) as mock_smart_plug:
        mock_smart_plug.return_value.state = 'OFF'
        mock_smart_plug.return_value.has_emeter = True
        mock_smart_plug.return_value.get_emeter_realtime.return_value = {
            'current': '0.123',
            'power': '1.23',
            'voltgage': '230',
            'total': '3',
        }
        yield mock_smart_plug

@pytest.fixture
def app(smart_plug):
    """Mock API fixture with predefined (sample) configuration"""
    app = create_app({
        'TESTING': True,
        'BINDINGS': ['tplink'],
        'HOSTNAME': 'http://localhost:5000'
    })

    yield app

@pytest.fixture
def client(app):
    """Mock API client fixture"""
    return app.test_client()

@pytest.fixture(autouse=True)
def discover():
    """Stubs PYHS100 discovery method, set to use on all tests"""
    with patch('wot.binding.tplink.Discover.discover') as mock_discover:
        smart_device = MagicMock()
        smart_device.alias = 'SmartPlug'
        smart_device.host = '10.0.0.3'
        mock_discover.return_value = {
            'test': smart_device
        }
        yield

def test_get_status(client, smart_plug):
    """Tests that the state is correctly reported to the user"""
    response = client.get('/tp_link:SmartPlug/state')
    assert response.status_code == 200
    assert response.get_json() == {
        'state': 'OFF'
    }

def test_set_status_on(client, smart_plug):
    """Tests setting the status to ON"""
    response = client.post('/tp_link:SmartPlug/state', json={
        'state': 'ON'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }
    smart_plug.return_value.turn_on.assert_called_once()

def test_set_status_off(client, smart_plug):
    """Tests setting the status to OFF"""
    response = client.post('/tp_link:SmartPlug/state', json={
        'state': 'OFF'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }
    smart_plug.return_value.turn_off.assert_called_once()

def test_set_status_other(client):
    """Tests setting the status to unknown value"""
    response = client.post('/tp_link:SmartPlug/state', json={
        'state': 'X'
    })

    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Invalid option'
    }

def test_toggle_on(client, smart_plug):
    """Tests the toggle endpoint when the device is OFF"""
    smart_plug.return_value.state = 'OFF'

    response = client.post('/tp_link:SmartPlug/state/toggle')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }

    smart_plug.return_value.turn_on.assert_called_once()

def test_toggle_off(client, smart_plug):
    """Tests the toggle endpoint when the device is ON"""
    smart_plug.return_value.state = 'ON'

    response = client.post('/tp_link:SmartPlug/state/toggle')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }

    smart_plug.return_value.turn_off.assert_called_once()

def test_get_emeter(client, smart_plug):
    """Tests the emeter values are correctly returned in the response"""
    response = client.get('/tp_link:SmartPlug/emeter')

    assert response.status_code == 200
    assert response.get_json() == {
        'current': '0.123',
        'power': '1.23',
        'voltgage': '230',
        'total': '3',
    }

def test_get_td(client):
    """Tests that the thing description is returned correctly"""
    response = client.get('/')
    assert response.get_json() == [{
        'actions': {
            'state': {
                'forms': [
                    {
                        'contentType': 'application/json',
                        'href': 'http://localhost:5000/tp_link:SmartPlug/state'
                    }
                ],
                'input': {
                    'properties': {
                        'state': {
                            'type': 'string'
                        }
                    },
                    'type': 'object'
                },
                'output': {
                    'properties': {
                        'message': {
                            'type': 'string'
                        }
                    },
                    'type': 'object'
                }
            },
            'toggle': {
                'forms': [
                    {
                        'contentType': 'application/json',
                        'href': 'http://localhost:5000/tp_link:SmartPlug/state/toggle'
                    }
                ],
                'output': {
                    'properties': {
                        'message': {
                            'type': 'string'
                        }
                    },
                    'type': 'object'
                }
            }
        },
        'events': {},
        'id': 'urn:tp_link:SmartPlug',
        'name': 'SmartPlug',
        'properties': {
            'emeter': {
                'forms': [
                    {
                        'contentType': 'application/json',
                        'href': 'http://localhost:5000/tp_link:SmartPlug/emeter'
                    }
                ],
                'properties': {
                    'current': {
                        'type': 'number'
                    },
                    'power': {
                        'type': 'number'
                    },
                    'total': {
                        'type': 'number'
                    },
                    'voltage': {
                        'type': 'number'
                    }
                },
                'type': 'object'
            },
            'state': {
                'forms': [
                    {
                        'contentType': 'application/json',
                        'href': 'http://localhost:5000/tp_link:SmartPlug/state'
                    }
                ],
                'properties': {
                    'state': {
                        'type': 'string'
                    }
                },
                'type': 'object'
            }
        },
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