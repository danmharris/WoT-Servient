"""This module contains utility code for easily creating thing descriptions"""
def _add_form(interaction, name, href, content_type='application/json'):
    """Generic addition of a form to an interaction

    Takes four arguments:
    interaction - dictionary of all interactions of same type
    name - Name to give the interaction
    href - The URL of the interaction endpoint
    content_type - MIME type of endpoint (defaults to application/json)
    """
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

class ThingDescriptionBuilder:
    """Utility class for building a thing description"""
    def __init__(self, id, name, security=None):
        """Initialise with parameters about the device

        Takes 3 arguments:
        id - Unique identify (URN) for the device
        name - Friendly device name
        security - Dictionary of security methods (optional)
        """
        self.id = id
        self.name = name
        self.security = security if security is not None else dict()
        self.properties = dict()
        self.events = dict()
        self.actions = dict()
    def add_property(self, prop, href, schema=None, observable=False):
        """Adds a new property to the description

        Takes 4 arguments:
        prop - Name of the property
        href - URI of the property endpoint
        schema - Data schema (optional)
        observable - Whether this is CoAP observable (defaults to False)
        """
        _add_form(self.properties, prop, href)
        if schema is not None:
            self.properties[prop] = dict(schema, **self.properties[prop])
        if observable == True:
            self.properties[prop]['observable'] = True
    def add_action(self, name, href, input=None, output=None):
        """Adds a new action to the description

        Takes 4 arguments:
        name - Name of the action
        href - URI of the action endpoint
        input - Input schema to endpoint (defaults to None)
        output - Output schema from the endpoint response (defaults to None)
        """
        _add_form(self.actions, name, href)
        if input is not None:
            self.actions[name]['input'] = input
        if output is not None:
            self.actions[name]['output'] = output
    def add_event(self, name, href, data=None):
        """Adds a new event to the description

        Takes 3 arguments:
        name - Name of the event
        href - URI of the event endpoint
        data - Schema of the data when event emitted (defaults to None)
        """
        _add_form(self.events, name, href)
        if data is not None:
            self.events[name]['data'] = data
    def build(self):
        """Convert the thing description into a dictionary with all information"""
        return {
            'id': self.id,
            'name': self.name,
            'security': list(self.security.keys()),
            'securityDefinitions': self.security,
            'properties': self.properties,
            'actions': self.actions,
            'events': self.events
        }

class SchemaBuilder:
    """Abstract schema builder"""
    def __init__(self, type_):
        """Initialise with type of the schema"""
        self.type = type_
    def build(self):
        """Builds the schema into a dictionary"""
        return {
            'type': self.type
        }

class StringBuilder(SchemaBuilder):
    """Schema representing a string value"""
    def __init__(self):
        super().__init__('string')

class NumberBuilder(SchemaBuilder):
    """Schema representing a single number value"""
    def __init__(self):
        super().__init__('number')

class ObjectBuilder(SchemaBuilder):
    """Schema representing more complex object"""
    def __init__(self):
        super().__init__('object')
        self.data = dict()
    def add_number(self, name):
        """Add a new number to the object

        Takes 1 argument:
        name - Key for the number value
        """
        self.data[name] = {
            'type': 'number'
        }
    def add_string(self, name):
        """Add a new string to the object

        Takes 1 argument:
        name - Key for the string value
        """
        self.data[name] = {
            'type': 'string'
        }
    def add_object(self, name, properties):
        """Add nested object to this object

        Takes 2 arguments:
        name - Name of the object key
        properties - Schema of the object
        """
        self.data[name] = properties
    def build(self):
        return {
            'type': 'object',
            'properties': self.data
        }
