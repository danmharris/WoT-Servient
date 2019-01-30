from thing_directory.app import create_app
from thing_directory.data import data
from common.db import get_db, close_db
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

    with app.app_context():
        s = get_db()
        for key in data:
            s[key] = data[key]
        close_db()

    yield app

    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_things(client):
    """ Test the /things GET request """
    response = client.get('/things')
    assert response.status_code == 200
    assert response.get_json() == {
        '123': {
            'name':'test'
        },
        '456': {
            'name':'test2',
            'groups':['group1']
        }
    }

def test_thing_uuid(client):
    """ Test /things/<uuid> GET request where the UUID exists """
    response = client.get('/things/123')
    assert response.status_code == 200
    assert response.get_json() == {
        'name': 'test'
    }

def test_thing_uuid_404(client):
    """ Test /things/<uuid> GET request where the UUID doesn't exist """
    response = client.get('/things/abc')
    assert response.status_code == 404
    assert response.data == b"{'message': 'Thing not found'}"

def test_query_groups(client):
    """ Test /things/query GET request with match """
    response = client.get('/things/query?groups=group1')
    assert response.status_code == 200
    print(response.get_json())
    assert response.get_json() == {
        '456': {
            'name': 'test2',
            'groups': ['group1']
        }
    }

def test_query_groups_none(client):
    """ Test /things/query with no match """
    response = client.get('/things/query?groups=group2')
    assert response.status_code == 200
    assert response.get_json() == {}

def test_register(client):
    """ Test /things/register POST endpoint """
    response = client.post('/things/register',
        json={
            'schema': {
                'name': 'test3'
            }
        })
    assert response.status_code == 201

def test_add_group(client):
    """ Test /things/<uuid>/groups POST request """
    initial_response = client.get('/things/123')
    assert initial_response.get_json() == {
        'name': 'test'
    }

    update_response = client.post('/things/123/groups',
        json = {'group': 'group2'})
    assert update_response.get_json() == {
        'message': 'updated'
    }

    new_response = client.get('/things/123')
    assert new_response.get_json() == {
        'name': 'test',
        'groups': ['group2']
    }

def test_add_group_404(client):
    """ Test /things/<uuid>groups POST request where thing doesnt exist """
    response = client.post('/things/abc/groups',
        json = {'group': 'group2'})
    assert response.status_code == 404
    assert response.data == b"{'message': 'Thing not found'}"

def test_delete(client):
    """ Test /things/<uuid> DELETE request """
    initial_response = client.get('/things')
    assert '123' in initial_response.get_json()
    delete_response = client.delete('/things/123')
    assert delete_response.get_json() == {
        'message': 'deleted'
    }
    new_response = client.get('/things')
    assert '123' not in new_response.get_json()

def test_delete_404(client):
    """ Test /things/<uuid> DELETE request where thing doesnt exist """
    response = client.delete('/things/abc')
    assert response.status_code == 404
    assert response.data == b"{'message': 'Thing not found'}"
