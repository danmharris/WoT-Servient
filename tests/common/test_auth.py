"""This module contains pytests for auth utility module"""
# pylint: disable=redefined-outer-name, unused-argument, unused-import
# Disabled these checkers as they conflict with pytest fixtures
from unittest.mock import patch
import pytest
import jwt
from flask import Flask
from wot.common.auth import check_auth, check_auth_exclude, check_auth_include

@pytest.fixture
def app():
    """Mock flask app, with only a single test endpoint"""
    flask_app = Flask(__name__)
    flask_app.config['AUTH'] = True
    flask_app.config['SECRET'] = 'test'
    flask_app.before_request(check_auth)

    @flask_app.route('/')
    def index():
        return 'Success!'

    return flask_app

@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()

def test_no_auth_header(client):
    """Tests that the request is rejected if no header supplied"""
    response = client.get('/')
    assert response.status_code == 401
    assert response.get_json() == {
        'message': 'No auth'
    }

def test_invalid_header(client):
    """Tests that request is rejected if invalid header supplied"""
    response = client.get('/', headers={
        'Authorization': 'abc'
    })
    assert response.status_code == 401
    assert response.get_json() == {
        'message': 'No auth'
    }

def test_invalid_jwt(client):
    """Tests that the request is rejected if the JWT is invalid"""
    response = client.get('/', headers={
        'Authorization': 'bearer abc'
    })
    assert response.status_code == 401
    assert response.get_json() == {
        'message': 'No auth'
    }

def test_valid_jwt(client):
    """Tests that the request is successful with a valid JWT"""
    token = jwt.encode({'name': 'test'}, 'test', algorithm='HS256')
    response = client.get('/', headers={
        'Authorization': b'bearer ' + token
    })

    assert response.status_code == 200
    assert response.get_data() == b'Success!'

def test_exclude():
    """Tests the auth exclusion logic"""
    with patch('wot.common.auth.check_auth') as mock_auth:
        with patch('wot.common.auth.request') as mock_request:
            mock_request.endpoint = 'test'
            check_auth_exclude(['test'])()
            mock_auth.assert_not_called()

            mock_request.endpoint = 'another'
            check_auth_exclude(['test'])()
            mock_auth.assert_called_once()

def test_include():
    """Tests the auth inclusion logic"""
    with patch('wot.common.auth.check_auth') as mock_auth:
        with patch('wot.common.auth.request') as mock_request:
            mock_request.endpoint = 'test'
            check_auth_include(['test2'])()
            mock_auth.assert_not_called()

            check_auth_include(['test'])()
            mock_auth.assert_called_once()
