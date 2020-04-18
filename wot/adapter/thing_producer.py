from flask import Blueprint, jsonify

class ThingProducer:
    def __init__(self, schema):
        self.schema = schema
        self.properties = dict()
        base = self.schema['base']

        bp = Blueprint(schema['id'], __name__, url_prefix=base)
        self.blueprint = bp

        @bp.route('/', methods=['GET'])
        def get_td():
            return jsonify(self.schema)

    def setPropertyReadHandler(self, name, func):
        self._setHandler(name, 'readproperty', func)

    def setPropertyWriteHandler(self, name, func):
        self._setHandler(name, 'writeproperty', func)

    def setActionHandler(self, name, func):
        self._setHandler(name, 'invokeaction', func)

    def _setHandler(self, name, op, func):
        default_methods = {
            'readproperty': 'GET',
            'writeproperty': 'PUT',
            'invokeaction': 'POST',
        }

        interaction_type = 'actions' if op == 'invokeaction' else 'properties'

        prop = self.schema[interaction_type][name]
        form = None
        for f in prop['forms']:
            if f['op'] == op:
                form = f
                break

        href = form['href']
        method = form['htv:methodName'] or default_methods[op]

        endpoint = self.schema['id'] + ':' + name + ':' + op
        bp = self.blueprint
        bp.add_url_rule(href, endpoint, func, methods=[method])

