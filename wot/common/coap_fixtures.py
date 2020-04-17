"""This module contains fixtures when mocking CoAP communications"""
from unittest.mock import patch, MagicMock
import asyncio
import pytest

class Response:
    """Mock Response class"""
    def __init__(self, payload):
        """Initialise with payload to return"""
        self.payload = payload
class Request:
    """Mock Request class"""
    def __init__(self, data):
        """Initialise with data to return. Creates response with this data and resolves future"""
        self.response = asyncio.Future()
        self.response.set_result(Response(data))

@pytest.fixture
def context():
    """Fixture that overrides aiocoap Context with class"""
    with patch('aiocoap.Context', autospec=True) as mock_context:
        mock_context.return_value.client_credentials = MagicMock()
        mock_context.create_client_context.return_value = asyncio.Future()
        mock_context.create_client_context.return_value.set_result(mock_context())
        yield mock_context

@pytest.fixture
def message():
    """Fixture which ovverides aiocoap Message class"""
    with patch('aiocoap.Message', autospec=True) as mock_message:
        yield mock_message
