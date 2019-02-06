import pytest
from datetime import datetime, timedelta
from common import ring_buffer

def teardown_function():
    ring_buffer.clear()

def test_empty_push():
    assert ring_buffer.contains(1) == False
    ring_buffer.push(1, 'test')
    assert ring_buffer.contains(1) == True

def test_full_push():
    for i in range(10):
        ring_buffer.push(i, 'test')
    assert ring_buffer.contains(0) == True
    ring_buffer.push(10, 'test')
    assert ring_buffer.contains(0) == False

def test_get():
    ring_buffer.push(1, 'test')
    assert ring_buffer.get(1) == 'test'

def test_get_none():
    assert ring_buffer.get(2) == None

def test_get_expired():
    timediff = timedelta(minutes=10)
    expired = datetime.now() - timediff
    ring_buffer.push(1, 'test', expired)
    assert ring_buffer.get(1) == None

def test_remove():
    ring_buffer.push(1, 'test')
    assert ring_buffer.contains(1) == True
    ring_buffer.remove(1)
    assert ring_buffer.contains(1) == False

def test_set_size():
    ring_buffer.set_size(1)
    ring_buffer.push(1, 'test')
    ring_buffer.push(2, 'test')
    assert ring_buffer.contains(1) == False
