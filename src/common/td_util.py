def add_form(interaction, name, href, content_type='application/json'):
    if name in interaction:
        interaction[name]['forms'].append({
            'href': href,
            'contentType': content_type,
        })
    else:
        interaction[name] = {
            'forms': [{
                'href': href,
                'contentType': content_type,
            }]
        }

class ThingDescriptionBuilder(object):
    def __init__(self, id, name, security=dict()):
        self.id = id
        self.name = name
        self.security = security
        self.properties = dict()
        self.events = dict()
        self.actions = dict()
    def add_property(self, prop, href, schema=None):
        add_form(self.properties, prop, href)
        if schema is not None:
            self.properties[prop] = dict(schema, **self.properties[prop])
    def add_action(self, name, href, input=None, output=None):
        add_form(self.actions, name, href)
        if input is not None:
            self.actions[name]['input'] = input
        if output is not None:
            self.actions[name]['output'] = output
    def add_event(self, name, href, data=None):
        add_form(self.events, name, href)
        if data is not None:
            self.events[name]['data'] = data
    def build(self):
        return {
            'id': self.id,
            'name': self.name,
            'security': list(self.security.keys()),
            'securityDefinitions': self.security,
            'properties': self.properties,
            'actions': self.actions,
            'events': self.events
        }

class SchemaBuilder(object):
    def __init__(self, type_):
        self.type = type_
    def build(self):
        return {
            'type': self.type
        }

class StringBuilder(SchemaBuilder):
    def __init__(self):
        super().__init__('string')

class NumberBuilder(SchemaBuilder):
    def __init__(self):
        super().__init__('number')

class ObjectBuilder(SchemaBuilder):
    def __init__(self):
        super().__init__('object')
        self.data = dict()
    def add_number(self, name):
        self.data[name] = {
            'type': 'number'
        }
    def add_string(self, name):
        self.data[name] = {
            'type': 'string'
        }
    def add_object(self, name, properties):
        self.data[name] = properties
    def build(self):
        return {
            'type': 'object',
            'properties': self.data
        }
