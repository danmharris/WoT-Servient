import pytest
from common.td_util import add_form, ThingDescriptionBuilder, StringBuilder, NumberBuilder, ObjectBuilder

def test_add_form_empty():
    interactions = dict()
    add_form(interactions, 'test', 'http://example.com')
    assert 'test' in interactions
    assert interactions['test'] == {
        'forms': [{
            'href': 'http://example.com',
            'contentType': 'application/json'
        }]
    }

def test_add_form():
    interactions = {
        'test': {
            'forms': [{
                'href': 'http://example.com',
                'contentType': 'application/json'
            }]
        }
    }
    add_form(interactions, 'test', 'http://test.xyz', 'text/html')
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
    res = StringBuilder().build()
    assert res == {
        'type': 'string'
    }

def test_number_builder():
    res = NumberBuilder().build()
    assert res == {
        'type': 'number'
    }

def test_object_builder_empty():
    res = ObjectBuilder().build()
    assert res == {
        'type': 'object',
        'properties': {}
    }

def test_object_builder_scalar():
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
    assert ThingDescriptionBuilder('123', 'test',{'bearer_test':{'scheme': 'bearer'}}).build() == {
        'id': '123',
        'name': 'test',
        'securityDefinitions': {'bearer_test':{'scheme': 'bearer'}},
        'security': ['bearer_test'],
        'properties': {},
        'actions': {},
        'events': {},
    }

def test_td_builder_add_property():
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

def test_td_builder_add_action():
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
