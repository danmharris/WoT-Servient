from flask import Blueprint, jsonify, request
from pyHS100 import Discover, SmartPlug
from common.db import get_db

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
        s[dev.alias] = dev.host
    return jsonify(discovered)

@bp.route('/<alias>/state', methods=['GET'])
def get_status(alias):
    s = get_db()
    if alias in s:
        plug = SmartPlug(s[alias])
        return jsonify({
            'state': plug.state
        })
    else:
        return (jsonify({
            'message': 'Device not found'
        }), 404, None)

@bp.route('/<alias>/state', methods=['POST'])
def set_status(alias):
    data = request.get_json()
    s = get_db()
    if alias in s:
        plug = SmartPlug(s[alias])
        if data['state'] == 'ON':
            plug.turn_on()
        elif data['state'] == 'OFF':
            plug.turn_off()
        else:
            return (jsonify({
                'message': 'Invalid option'
            }), 400, None)
        return jsonify({
            'message': 'State updated'
        })
    else:
        return (jsonify({
            'message': 'Device not found'
        }), 404, None)

@bp.route('/<alias>/state/toggle', methods=['POST'])
def toggle(alias):
    s = get_db()
    if alias in s:
        plug = SmartPlug(s[alias])
        if plug.state == 'ON':
            plug.turn_off()
        else:
            plug.turn_on()
        return jsonify({
            'message': 'State updated'
        })
    else:
        return (jsonify({
            'message': 'Device not found'
        }), 404, None)
