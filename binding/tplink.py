from flask import Blueprint, jsonify, request
from pyHS100 import Discover, SmartPlug
from common.db import get_db
from common.td_util import ThingDescriptionBuilder, ObjectBuilder, StringBuilder

bp = Blueprint('tplink', __name__, url_prefix='/tp_link')

#TODO: Add device type to data storage (e.g. SmartPlug, SmartBulb etc.)

@bp.route('/discover', methods=['POST'])
def discover():
    discovered = list()
    s = get_db()
    for dev in Discover.discover().values():
        discovered.append({
            'alias': dev.alias,
            'ip': dev.host,
        })
        s[f'tp_link:{dev.alias}'] = dev.host
    return jsonify(discovered)

@bp.route('/<alias>/state', methods=['GET'])
def get_status(alias):
    s = get_db()
    if f'tp_link:{alias}' in s:
        plug = SmartPlug(s[f'tp_link:{alias}'])
        return jsonify({
            'state': plug.state
        })
    else:
        return (jsonify({
            'message': 'Device not found'
        }), 404, None)

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

@bp.route('/<alias>/state', methods=['POST'])
def set_status(alias):
    data = request.get_json()
    s = get_db()
    if f'tp_link:{alias}' in s:
        plug = SmartPlug(s[f'tp_link:{alias}'])
        return _set_status(plug, data['state'])
    else:
        return (jsonify({
            'message': 'Device not found'
        }), 404, None)

@bp.route('/<alias>/state/toggle', methods=['POST'])
def toggle(alias):
    s = get_db()
    if f'tp_link:{alias}' in s:
        plug = SmartPlug(s[f'tp_link:{alias}'])
        new_state = 'OFF' if plug.state == 'ON' else 'ON'
        return _set_status(plug, new_state)
    else:
        return (jsonify({
            'message': 'Device not found'
        }), 404, None)

def build_td(id):
    alias = id.split(':')[1]
    td=ThingDescriptionBuilder(f'urn:{id}','SmartPlug')

    schema = ObjectBuilder()
    schema.add_string('state')
    updated = ObjectBuilder()
    updated.add_string('message')

    td.add_property('state', f'http://localhost:5000/tp_link/{alias}/state', schema.build())
    td.add_action('state', f'http://localhost:5000/tp_link/{alias}/state', schema.build(), updated.build())
    td.add_action('toggle', f'http://localhost:5000/tp_link/{alias}/state/toggle', output=updated.build())
    return td.build()
