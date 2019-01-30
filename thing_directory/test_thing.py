from thing_directory.thing import Thing
import pytest

def test_constructor_given_args():
    """ Tests that the constructor sets fields based on arguments """
    thing = Thing('placeholder dbh', {'property': 'value'}, '123')
    assert thing.dbh == 'placeholder dbh'
    assert thing.schema == {
        'property': 'value'
    }
    assert thing.uuid == '123'

def test_constructor_default_args():
    """ Tests that the constructor uses default arguments if not provided """
    thing = Thing('dbh')
    assert thing.dbh == 'dbh'
    assert thing.schema == {}
    assert thing.uuid != None

def test_constructor_missing_dbh():
    """ Tests that the constructor raises an error if dbh not provided """
    with pytest.raises(TypeError):
        Thing()

def test_get_by_uuid_present():
    """ Tests that get_by_uuid retrieves the schema if it exists """
    s = {
        '123': 'schema'
    }
    thing = Thing.get_by_uuid(s, '123')
    assert thing.uuid == '123'
    assert thing.dbh == s
    assert thing.schema == 'schema'

def test_get_by_uuid_not_present():
    """ Tests that get_by_uuid raises an exception if it doesn't exist """
    s = {
        '123': 'schema'
    }
    with pytest.raises(Exception):
        Thing.get_by_uuid(s, '456')

def test_add_groups_not_present():
    """ Tests adding the first group to a schema """
    thing = Thing('', {}, '123')
    thing.add_group('living room')
    assert thing.schema == {'groups': ['living room']}

def test_add_groups_already_present():
    """ Tests adding further groups to a schema """
    thing = Thing('', {'groups': ['living room']}, '123')
    thing.add_group('kitchen')
    assert thing.schema == {'groups': ['living room', 'kitchen']}

def test_get_groups_present():
    """ Tests getting groups when there are groups """
    thing = Thing('', {'groups': ['living room']}, '123')
    assert thing.get_groups() == ['living room']

def test_get_groups_empty():
    """ Tests getting groups when there are none """
    thing = Thing('', {}, '123')
    assert thing.get_groups() == []

def test_save():
    """ Tests that saving updates the database object """
    s = {}
    thing = Thing(s, {'property': 'value'}, '123')
    thing.save()
    assert s['123'] == {'property': 'value'}

def test_delete_present():
    """ Tests deleting an object """
    s = {
        '123': {'property': 'value'}
    }
    thing = Thing(s, {'property': 'value'}, '123')
    thing.delete()
    assert s == {}

def test_delete_not_present():
    """ Tests that an exception is raised if a nonexistent object is deleted """
    s = {}
    thing = Thing(s, {'property': 'value'}, '123')
    with pytest.raises(KeyError):
        thing.delete()
