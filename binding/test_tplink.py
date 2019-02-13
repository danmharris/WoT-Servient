import pytest
import os
from unittest.mock import MagicMock, patch
from binding.app import create_app
from binding.tplink import TpLinkProducer

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'BINDINGS': [TpLinkProducer()],
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def discover():
    with patch('binding.tplink.Discover.discover') as mock_discover:
        smart_device = MagicMock()
        smart_device.alias = 'SmartPlug'
        smart_device.host = '10.0.0.3'
        mock_discover.return_value = {
            'test': smart_device
        }
        yield

@pytest.fixture()
def smart_plug():
    with patch('binding.tplink.SmartPlug', autospec=True) as mock_smart_plug:
        mock_smart_plug.return_value.state = 'OFF'
        yield mock_smart_plug

def test_get_status(client, smart_plug):
    response = client.get('/tp_link:SmartPlug/state')
    assert response.status_code == 200
    assert response.get_json() == {
        'state': 'OFF'
    }

def test_set_status_on(client, smart_plug):
    response = client.post('/tp_link:SmartPlug/state', json={
        'state': 'ON'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }
    smart_plug.return_value.turn_on.assert_called_once()

def test_set_status_off(client, smart_plug):
    response = client.post('/tp_link:SmartPlug/state', json={
        'state': 'OFF'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }
    smart_plug.return_value.turn_off.assert_called_once()

def test_set_status_other(client):
    response = client.post('/tp_link:SmartPlug/state', json={
        'state': 'X'
    })

    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Invalid option'
    }

def test_toggle_on(client, smart_plug):
    smart_plug.return_value.state = 'OFF'

    response = client.post('/tp_link:SmartPlug/state/toggle')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }

    smart_plug.return_value.turn_on.assert_called_once()

def test_toggle_off(client, smart_plug):
    smart_plug.return_value.state = 'ON'

    response = client.post('/tp_link:SmartPlug/state/toggle')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }

    smart_plug.return_value.turn_off.assert_called_once()
