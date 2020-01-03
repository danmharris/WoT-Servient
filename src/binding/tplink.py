"""This module contains code for creating a binding template for TP-LINK products"""

from flask import Blueprint, jsonify, request, current_app
from pyHS100 import Discover, SmartPlug
from wot.common.td_util import ThingDescriptionBuilder, ObjectBuilder
from binding.producer import Producer

class TpLinkProducer(Producer):
    """Binding template for TP-LINK smart products"""
    def produce(self):
        discovered = list()
        for dev in Discover.discover().values():
            prefix = 'tp_link:{}'.format(dev.alias)
            bp = _produce_blueprint(dev.host, '/'+prefix)
            td = _build_td(prefix, dev.alias, dev.host)
            discovered.append((bp, td))
        return discovered

def _produce_blueprint(address, prefix):
    """Produces Flask blueprints for TP-LINK products

    Takes two arguments:
    address - IP address of the device
    prefix - Prefix to prepend to all URIs
    """
    bp = Blueprint(prefix, __name__, url_prefix=prefix)
    plug = SmartPlug(address)

    def get_emeter():
        """Gets the Emeter values from the smart plug (if capable)"""
        return jsonify(plug.get_emeter_realtime())

    if plug.has_emeter:
        bp.add_url_rule('/emeter', view_func=get_emeter)

    @bp.route('/state', methods=['GET'])
    def get_status():
        """GET endpoint that returns the status of the device"""
        plug = SmartPlug(address)
        return jsonify({
            'state': plug.state
        })

    def _set_status(device, state):
        """Set the status of a smart device

        Takes two arguments:
        device - Device to set state on
        state - Either 'ON' or 'OFF'
        """
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
        """POST request that sets the status of the smart device

        Requires JSON input with the state"""
        data = request.get_json()
        plug = SmartPlug(address)
        return _set_status(plug, data['state'])

    @bp.route('/state/toggle', methods=['POST'])
    def toggle():
        """POST request which inverts the state

        No input required
        """
        plug = SmartPlug(address)
        new_state = 'OFF' if plug.state == 'ON' else 'ON'
        return _set_status(plug, new_state)

    return bp

def _build_td(prefix, alias, address):
    """Build the thing descriptions for TP-LINK products

    Takes three arguments:
    prefix - prefix for this device (relative to this host)
    alias - Name given to this device
    address - IP address of device
    """
    hostname = current_app.config['HOSTNAME']

    security = {
        'bearer_token': {
            'scheme': 'bearer',
            'alg': 'HS256',
            'in': 'header',
            'name': 'Authorization'
        }
    }

    td = ThingDescriptionBuilder('urn:{}'.format(prefix), alias, security=security)
    plug = SmartPlug(address)

    schema = ObjectBuilder()
    schema.add_string('state')
    updated = ObjectBuilder()
    updated.add_string('message')

    td.add_property('state', '{}/{}/state'.format(hostname, prefix), schema.build())
    td.add_action('state', '{}/{}/state'.format(hostname, prefix), schema.build(), updated.build())
    td.add_action('toggle', '{}/{}/state/toggle'.format(hostname, prefix), output=updated.build())

    if plug.has_emeter:
        emeter = ObjectBuilder()
        emeter.add_number('current')
        emeter.add_number('power')
        emeter.add_number('total')
        emeter.add_number('voltage')
        td.add_property('emeter', '{}/{}/emeter'.format(hostname, prefix), emeter.build())

    return td.build()
