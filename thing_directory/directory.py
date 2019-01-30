from flask import Blueprint, current_app, request, jsonify
import shelve, uuid
from thing import Thing

bp = Blueprint('directory', __name__, url_prefix='/things')

@bp.route('', methods=['GET'])
def get_all():
    s = shelve.open(current_app.config['DB'])
    ids = list(s.keys())
    s.close()
    response = {
        "ids": ids
    }
    return jsonify(response)

@bp.route('/<uuid>', methods=['GET'])
def get_by_id(uuid):
    s = shelve.open(current_app.config['DB'])
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        response = jsonify(db_thing.schema)
    except Exception as err:
        response = (str(err), 404, None)
    finally:
        s.close()
        return response

@bp.route('/query', methods=['GET'])
def query():
    req_groups = request.args.get('groups').split(',')
    s = shelve.open(current_app.config['DB'])
    uuids = list(s.keys())
    matching = []
    for id in uuids:
        try:
            thing = Thing.get_by_uuid(s, id)
            groups = thing.get_groups()
            if len(set(groups).intersection(req_groups)) > 0:
                matching.append(thing.schema)
        except Exception:
            continue
    s.close()
    return jsonify(matching)

@bp.route('/register', methods=['POST'])
def register():
    # Needs to validate input
    s = shelve.open(current_app.config['DB'])
    new_thing = Thing(s, request.get_json())
    new_thing.save()
    response = {
        "id": new_thing.uuid
    }
    s.close()
    return (jsonify(response), 201, None)

@bp.route('/<uuid>/groups', methods=['POST'])
def add_group(uuid):
    body = request.get_json()
    s = shelve.open(current_app.config['DB'])
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
    except Exception as err:
        s.close()
        return (str(err), 404, None)
    db_thing.add_group(body['group'])
    db_thing.save()
    response = {
        "message": "updated"
    }
    s.close()
    return (jsonify(response), 200, None)

@bp.route('/<uuid>', methods=['DELETE'])
def delete_thing(uuid):
    s = shelve.open(current_app.config['DB'])
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        db_thing.delete()
        response = (jsonify({"message": "deleted"}), 200, None)
    except Exception as err:
        response = (str(err), 404, None)
    finally:
        s.close()
        return response
