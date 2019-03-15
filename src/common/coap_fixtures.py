from unittest.mock import patch, MagicMock
import asyncio
import pytest

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
        mock_context.return_value.client_credentials = MagicMock()
        mock_context.create_client_context.return_value = asyncio.Future()
        mock_context.create_client_context.return_value.set_result(mock_context())
        yield mock_context

@pytest.fixture
def message():
    with patch('aiocoap.Message', autospec=True) as mock_message:
        yield mock_message
