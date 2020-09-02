from wot.grouper.db import get_db
from wot.grouper.services import ThingService

from flask import Blueprint, jsonify, request

bp = Blueprint('grouper', __name__)

@bp.route('/', methods=['GET'])
def get_things():
    """ returns all things known to the system """
    things = None
    things = ThingService(get_db()).get_things()

    return jsonify(things)

@bp.route('/', methods=['POST'])
def new_thing():
    """
    Creates a new virtual thing. This takes a thing description as parameters,
    with an additional field called "exec" in action definitions.

    Currently only actions are supported
    """
    try:
        ThingService(get_db()).new_thing(request.get_json())
    except (ValueError, IndexError) as e:
        return (jsonify({'message': str(e)}), 400, None)

    return (jsonify({'status': 'created'}), 201, None)

@bp.route('/<name>', methods=['GET'])
def get_thing(name):
    """
    Retrieves a description for a single thing
    """
    thing = None
    try:
        thing = ThingService(get_db()).get_thing(name)
    except IndexError as e:
        return (jsonify({'message': str(e)}), 404, None)

    return jsonify(thing)

@bp.route('/<name>/<action>', methods=['POST'])
def invoke_action(name, action):
    """
    Invokes the action by performing all steps in exec
    """
    try:
        ThingService(get_db()).invoke_action(name, action)
    except IndexError as e:
        return (jsonify({'message': str(e)}), 400, None)
    except RuntimeError as e:
        return (jsonify({'message': str(e)}), 500, None)

    return jsonify({'message': 'Action executed successfully'})

@bp.route('/<name>', methods=['DELETE'])
def delete_thing(name):
    """
    Deletes a thing
    """
    try:
        ThingService(get_db()).delete_thing(name)
    except IndexError as e:
        return (jsonify({'message': str(e)}), 404, None)

    return (jsonify({'message': 'Deleted'}), 410, None)
