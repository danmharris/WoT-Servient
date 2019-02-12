import pytest
import os
from unittest.mock import MagicMock, patch
from binding.app import create_app
from common.db import get_db, close_db

@pytest.fixture
def app():
    db_path = 'test.db'

    app = create_app({
        'TESTING': True,
        'DB': db_path,
    })

    with app.app_context():
        s = get_db()
        s['tp_link:SmartPlug'] = '10.0.0.3'
        close_db()

    yield app

    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def MockSmartPlug():
    with patch('binding.tplink.SmartPlug') as MockSmartPlug:
        yield MockSmartPlug

def test_discover(client):
    with patch('binding.tplink.Discover.discover') as mock_discover:

        smart_device = MagicMock()
        smart_device.alias = 'SmartPlug'
        smart_device.host = '10.0.0.3'

        mock_discover.return_value = {
            'test': smart_device
        }

        response = client.post('/tp_link/discover')
        assert response.status_code == 200
        assert response.get_json() == [
            {
                'alias': 'SmartPlug',
                'ip': '10.0.0.3',
            }
        ]

def test_get_status(client, MockSmartPlug):
    MockSmartPlug.return_value.state = 'OFF'

    response = client.get('/tp_link/SmartPlug/state')
    assert response.status_code == 200
    assert response.get_json() == {
        'state': 'OFF'
    }

def test_get_status_404(client):
    response = client.get('/tp_link/Test/state')
    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Device not found'
    }

def test_set_status_on(client, MockSmartPlug):
    response = client.post('/tp_link/SmartPlug/state', json={
        'state': 'ON'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }
    MockSmartPlug.return_value.turn_on.assert_called_once()

def test_set_status_off(client, MockSmartPlug):
    response = client.post('/tp_link/SmartPlug/state', json={
        'state': 'OFF'
    })

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }
    MockSmartPlug.return_value.turn_off.assert_called_once()

def test_set_status_other(client):
    response = client.post('/tp_link/SmartPlug/state', json={
        'state': 'X'
    })

    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Invalid option'
    }

def test_set_status_not_found(client):
    response = client.post('/tp_link/Test/state', json={
        'state': 'OFF'
    })

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Device not found'
    }

def test_toggle_on(client, MockSmartPlug):
    MockSmartPlug.return_value.state = 'OFF'

    response = client.post('/tp_link/SmartPlug/state/toggle')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }

    MockSmartPlug.return_value.turn_on.assert_called_once()

def test_toggle_off(client, MockSmartPlug):
    MockSmartPlug.return_value.state = 'ON'

    response = client.post('/tp_link/SmartPlug/state/toggle')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'State updated'
    }

    MockSmartPlug.return_value.turn_off.assert_called_once()

def test_toggle_not_found(client):
    response = client.post('/tp_link/Test/state/toggle', json={
        'state': 'OFF'
    })

    assert response.status_code == 404
    assert response.get_json() == {
        'message': 'Device not found'
    }
