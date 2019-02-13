from flask import Blueprint, jsonify, request
from pyHS100 import Discover, SmartPlug
from common.td_util import ThingDescriptionBuilder, ObjectBuilder, StringBuilder
from binding.producer import Producer

class TpLinkProducer(Producer):
    def __init__(self):
        super().__init__()
    def produce(self):
        discovered = list()
        for dev in Discover.discover().values():
            prefix = 'tp_link:{}'.format(dev.alias)
            bp = _produce_blueprint(dev.host, '/'+prefix)
            td = _build_td(prefix, dev.alias)
            discovered.append((bp, td))
        return discovered

def _produce_blueprint(address, prefix):
    bp = Blueprint(prefix, __name__, url_prefix=prefix)

    #TODO: Add device type to data storage (e.g. SmartPlug, SmartBulb etc.)

    @bp.route('/state', methods=['GET'])
    def get_status():
        plug = SmartPlug(address)
        return jsonify({
            'state': plug.state
        })

    def _set_status(device, state):
        if state == 'ON':
            device.turn_on()
        elif state == 'OFF':
            device.turn_off()
        else:
            return (jsonify({
                'message': 'Invalid option'
            }), 400, None)
        return jsonify({
            'message': 'State updated'
        })

    @bp.route('/state', methods=['POST'])
    def set_status():
        data = request.get_json()
        plug = SmartPlug(address)
        return _set_status(plug, data['state'])

    @bp.route('/state/toggle', methods=['POST'])
    def toggle():
        plug = SmartPlug(address)
        new_state = 'OFF' if plug.state == 'ON' else 'ON'
        return _set_status(plug, new_state)

    return bp

def _build_td(prefix, alias):
    td=ThingDescriptionBuilder('urn:{}'.format(prefix), alias)

    schema = ObjectBuilder()
    schema.add_string('state')
    updated = ObjectBuilder()
    updated.add_string('message')

    td.add_property('state', 'http://localhost:5000/{}/state'.format(prefix), schema.build())
    td.add_action('state', 'http://localhost:5000/{}/state'.format(prefix), schema.build(), updated.build())
    td.add_action('toggle', 'http://localhost:5000/{}/state/toggle'.format(prefix), output=updated.build())
    return td.build()
