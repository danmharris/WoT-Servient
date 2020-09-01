from flask import Blueprint, jsonify, request
from wot.grouper.db import get_db
from wot.grouper.services import ThingService

bp = Blueprint('grouper', __name__)

# TODO: Improve exception handling (specific exception types and status codes)

@bp.route('/', methods=['GET'])
def get_things():
    """ returns all things known to the system """
    things = None
    try:
        things = ThingService(get_db()).get_things()
    except:
        return (jsonify({'message': 'An error occured'}), 500, None)

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
    except:
        return (jsonify({'message': 'An error occured'}), 500, None)

    return (jsonify({'status': 'created'}), 201, None)

@bp.route('/<name>', methods=['GET'])
def get_thing(name):
    """
    Retrieves a description for a single thing
    """
    thing = None
    try:
        thing = ThingService(get_db()).get_thing(name)
    except:
        return (jsonify({'message': 'An error occured'}), 500, None)

    return jsonify(thing)

@bp.route('/<name>/<action>', methods=['POST'])
def invoke_action(name, action):
    """
    Invokes the action by performing all steps in exec
    """
    # TODO: Implement
    pass

@bp.route('/<name>', methods=['DELETE'])
def delete_thing(name):
    """
    Deletes a thing
    """
    # TODO: Implement
    pass
