from app import create_app
from data import data
import pytest
import tempfile
import shelve
import os

@pytest.fixture
def app():
    db_path = 'test.db'

    app = create_app({
        'TESTING': True,
        'DB': db_path
    })

    s = shelve.open(db_path)
    for key in data:
        s[key] = data[key]
    s.close()

    yield app

    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_things(client):
    response = client.get('/things')
    assert response.status_code == 200
