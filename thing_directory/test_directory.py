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
    """ Test the /things GET request """
    response = client.get('/things')
    assert response.status_code == 200
    assert response.get_json() == {
        'ids': ['123','456']
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
    assert response.get_json() == [
        {
            'name': 'test2',
            'groups': ['group1']
        }
    ]

def test_query_groups_none(client):
    """ Test /things/query with no match """
    response = client.get('/things/query?groups=group2')
    assert response.status_code == 200
    assert response.get_json() == []

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
    assert '123' in initial_response.get_json()['ids']
    delete_response = client.delete('/things/123')
    assert delete_response.get_json() == {
        'message': 'deleted'
    }
    new_response = client.get('/things')
    assert '123' not in new_response.get_json()['ids']

def test_delete_404(client):
    """ Test /things/<uuid> DELETE request where thing doesnt exist """
    response = client.delete('/things/abc')
    assert response.status_code == 404
    assert response.data == b"{'message': 'Thing not found'}"
