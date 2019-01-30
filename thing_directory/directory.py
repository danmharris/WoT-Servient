from flask import Blueprint, current_app, request, jsonify
import uuid
from thing_directory.thing import Thing
from common.db import get_db

bp = Blueprint('directory', __name__, url_prefix='/things')

@bp.route('', methods=['GET'])
def get_all():
    s = get_db()
    ids = list(s.keys())
    results = {}
    for id in ids:
        thing = Thing.get_by_uuid(s, id)
        results[thing.uuid] = thing.schema
    return jsonify(results)

@bp.route('/<uuid>', methods=['GET'])
def get_by_id(uuid):
    s = get_db()
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        response = jsonify(db_thing.schema)
    except Exception as err:
        response = (str(err), 404, None)
    finally:
        return response

def get_attribute(uuid, property):
    s = get_db()
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        value = getattr(db_thing, property, None)
        return jsonify(value)
    except Exception as err:
        return (str(err), 404, None)

@bp.route('/<uuid>/properties', methods=['GET'])
def get_properties(uuid):
    return get_attribute(uuid, 'properties')

@bp.route('/<uuid>/events', methods=['GET'])
def get_events(uuid):
    return get_attribute(uuid, 'events')

@bp.route('/<uuid>/actions', methods=['GET'])
def get_actions(uuid):
    return get_attribute(uuid, 'actions')

@bp.route('/query', methods=['GET'])
def query():
    req_groups = request.args.get('groups').split(',')
    s = get_db()
    uuids = list(s.keys())
    matching = {}
    for id in uuids:
        try:
            thing = Thing.get_by_uuid(s, id)
            groups = thing.get_groups()
            if len(set(groups).intersection(req_groups)) > 0:
                matching[thing.uuid] = thing.schema
        except Exception:
            continue
    return jsonify(matching)

@bp.route('/register', methods=['POST'])
def register():
    # Needs to validate input
    s = get_db()
    new_thing = Thing(s, request.get_json())
    new_thing.save()
    response = {
        "id": new_thing.uuid
    }
    return (jsonify(response), 201, None)

@bp.route('/<uuid>/groups', methods=['POST'])
def add_group(uuid):
    body = request.get_json()
    s = get_db()
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
    except Exception as err:
        return (str(err), 404, None)
    db_thing.add_group(body['group'])
    db_thing.save()
    response = {
        "message": "updated"
    }
    return (jsonify(response), 200, None)

@bp.route('/<uuid>', methods=['DELETE'])
def delete_thing(uuid):
    s = get_db()
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        db_thing.delete()
        response = (jsonify({"message": "deleted"}), 200, None)
    except Exception as err:
        response = (str(err), 404, None)
    finally:
        return response
