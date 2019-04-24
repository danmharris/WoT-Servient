"""Pytests for thing description utility module"""
from common.td_util import _add_form, ThingDescriptionBuilder
from common.td_util import StringBuilder, NumberBuilder, ObjectBuilder

def test_add_form_empty():
    """Tests that default arguments are used in _add_form"""
    interactions = dict()
    _add_form(interactions, 'test', 'http://example.com')
    assert 'test' in interactions
    assert interactions['test'] == {
        'forms': [{
            'href': 'http://example.com',
            'contentType': 'application/json'
        }]
    }

def test_add_form():
    """Tests adding a generic interaction form"""
    interactions = {
        'test': {
            'forms': [{
                'href': 'http://example.com',
                'contentType': 'application/json'
            }]
        }
    }
    _add_form(interactions, 'test', 'http://test.xyz', 'text/html')
    assert interactions['test'] == {
        'forms': [
            {
                'href': 'http://example.com',
                'contentType': 'application/json'
            },
            {
                'href': 'http://test.xyz',
                'contentType': 'text/html'
            },
        ]
    }

def test_string_builder():
    """Tests StringBuilder class"""
    res = StringBuilder().build()
    assert res == {
        'type': 'string'
    }

def test_number_builder():
    """Tests NumberBuilder class"""
    res = NumberBuilder().build()
    assert res == {
        'type': 'number'
    }

def test_object_builder_empty():
    """Tests ObjectBuilder with no properties"""
    res = ObjectBuilder().build()
    assert res == {
        'type': 'object',
        'properties': {}
    }

def test_object_builder_scalar():
    """Tests ObjectBuilder with multiple scalar properties"""
    builder = ObjectBuilder()
    builder.add_number('id')
    builder.add_string('title')
    assert builder.build() == {
        'type': 'object',
        'properties': {
            'id': {
                'type': 'number'
            },
            'title': {
                'type': 'string'
            }
        }
    }

def test_object_builder_object():
    """Tests ObjectBuilder with nested object"""
    builder1 = ObjectBuilder()
    builder1.add_number('nested_id')
    builder2 = ObjectBuilder()
    builder2.add_object('nested', builder1.build())
    assert builder2.build() == {
        'type': 'object',
        'properties': {
            'nested': {
                'type': 'object',
                'properties': {
                    'nested_id': {
                        'type': 'number'
                    }
                }
            }
        }
    }

def test_td_builder_empty():
    """Tests ThingDescriptionBuilder default arguments"""
    assert ThingDescriptionBuilder('123', 'test').build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {},
        'security': [],
        'properties': {},
        'actions': {},
        'events': {},
    }

def test_td_builder_security():
    """Tests security definitions"""
    assert ThingDescriptionBuilder('123', 'test', {'bearer_test':{'scheme': 'bearer'}}).build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {'bearer_test':{'scheme': 'bearer'}},
        'security': ['bearer_test'],
        'properties': {},
        'actions': {},
        'events': {},
    }

def test_td_builder_add_property():
    """Tests adding a property"""
    td = ThingDescriptionBuilder('123', 'test')
    td.add_property('status', 'http://example.com', StringBuilder().build())
    assert td.build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {},
        'security': [],
        'properties': {
            'status': {
                'forms': [{
                    'href': 'http://example.com',
                    'contentType': 'application/json'
                }],
                'type': 'string'
            }
        },
        'actions': {},
        'events': {},
    }

def test_td_builder_add_observable_property():
    """Tests adding an observable property"""
    td = ThingDescriptionBuilder('123', 'test')
    td.add_property('status', 'http://example.com', StringBuilder().build(), True)
    assert td.build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {},
        'security': [],
        'properties': {
            'status': {
                'forms': [{
                    'href': 'http://example.com',
                    'contentType': 'application/json'
                }],
                'type': 'string',
                'observable': True,
            }
        },
        'actions': {},
        'events': {},
    }

def test_td_builder_add_action():
    """Tests adding an action"""
    td = ThingDescriptionBuilder('123', 'test')
    td.add_action('toggle', 'http://example.com', NumberBuilder().build(), StringBuilder().build())
    assert td.build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {},
        'security': [],
        'properties': {},
        'actions': {
            'toggle': {
                'forms': [{
                    'href': 'http://example.com',
                    'contentType': 'application/json'
                }],
                'input': {
                    'type': 'number'
                },
                'output': {
                    'type': 'string'
                }
            }
        },
        'events': {},
    }

def test_td_builder_add_event():
    """Tests adding an event"""
    td = ThingDescriptionBuilder('123', 'test')
    td.add_event('toggle', 'http://example.com', NumberBuilder().build())
    assert td.build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {},
        'security': [],
        'properties': {},
        'actions': {},
        'events': {
            'toggle': {
                'forms': [{
                    'href': 'http://example.com',
                    'contentType': 'application/json'
                }],
                'data': {
                    'type': 'number'
                }
            }
        },

    }
