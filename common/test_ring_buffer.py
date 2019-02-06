import pytest
from datetime import datetime, timedelta
from common.ring_buffer import RingBuffer

@pytest.fixture
def buffer(scope='function'):
    buffer = RingBuffer()
    return buffer

def test_empty_push(buffer):
    assert buffer.contains(1) == False
    buffer.push(1, 'test')
    assert buffer.contains(1) == True

def test_full_push(buffer):
    for i in range(10):
        buffer.push(i, 'test')
    assert buffer.contains(0) == True
    buffer.push(10, 'test')
    assert buffer.contains(0) == False

def test_get(buffer):
    buffer.push(1, 'test')
    assert buffer.get(1) == 'test'

def test_get_none(buffer):
    assert buffer.get(2) == None

def test_get_expired(buffer):
    timediff = timedelta(minutes=10)
    expired = datetime.now() - timediff
    buffer.push(1, 'test', expired)
    assert buffer.get(1) == None

def test_remove(buffer):
    buffer.push(1, 'test')
    assert buffer.contains(1) == True
    buffer.remove(1)
    assert buffer.contains(1) == False

def test_clear(buffer):
    buffer.push(1, 'test')
    assert buffer.contains(1) == True
    buffer.clear()
    assert buffer.contains(1) == False
