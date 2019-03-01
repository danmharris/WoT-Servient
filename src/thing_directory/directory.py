from flask import Blueprint, current_app, request, jsonify
import uuid
from thing_directory.thing import Thing
from common.db import get_db
import requests

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

def add_proxy_endpoints(host, properties):
    for prop in properties:
        if 'forms' in properties[prop]:
            for form in properties[prop]['forms']:
                if 'href' in form:
                    #Add to proxy
                    res = requests.post(host+'/proxy/add', json={
                        'url': form['href']
                    })
                    form['href'] = '{}/proxy/{}'.format(host, res.json()['uuid'])

@bp.route('/register', methods=['POST'])
def register():
    # Needs to validate input
    s = get_db()
    new_thing = Thing(s, request.get_json(), uuid.uuid4().hex)

    if 'PROXY' in current_app.config:
        try:
            add_proxy_endpoints(current_app.config['PROXY'], new_thing.schema.get('properties', dict()))
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            return (jsonify({
                'message': 'Could not reach proxy'
            }), 504, None)

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

@bp.route('/<uuid>/groups/<group>', methods=['DELETE'])
def del_group(uuid, group):
    s = get_db()
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        db_thing.del_group(group)
        db_thing.save()
        return jsonify({
            'message': 'group removed'
        })
    except Exception as err:
        return (str(err), 404, None)

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
