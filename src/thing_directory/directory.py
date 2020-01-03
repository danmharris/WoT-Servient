"""Flask blueprint module for thing directory"""
from uuid import uuid4
import json
import asyncio
from flask import Blueprint, current_app, request, jsonify
import requests
import aiocoap
from aiocoap.numbers.codes import GET
from thing_directory.thing import Thing
from wot.common.db import get_db
from wot.common.exception import APIException
from wot.common.auth import check_auth

bp = Blueprint('directory', __name__, url_prefix='/things')
bp.before_request(check_auth)

@bp.route('', methods=['GET'])
def get_all():
    """GET request for getting all descriptions"""
    s = get_db()
    ids = list(s.keys())
    results = {}
    for id in ids:
        thing = Thing.get_by_uuid(s, id)
        results[thing.uuid] = thing.schema
    return jsonify(results)

@bp.route('/<uuid>', methods=['GET'])
def get_by_id(uuid):
    """GET request for retrieving by UUID"""
    s = get_db()
    db_thing = Thing.get_by_uuid(s, uuid=uuid)
    return jsonify(db_thing.schema)

@bp.route('/query', methods=['GET'])
def query():
    """GET request for performing query"""
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

def _add_proxy_endpoints(host, properties):
    """Registers endpoints on the proxy"""
    # Don't want to proxy observable endpoints as client needs to request those directly
    properties = {k: p for k, p in properties.items() if p.get('observable', False) is not True}
    for prop in properties:
        forms = [f for f in properties[prop].get('forms', list()) if 'href' in f]
        for form in forms:
            # Forward Auth header
            if 'Authorization' in request.headers:
                headers = {'Authorization': request.headers['Authorization']}
            else:
                headers = None
            res = requests.post(host+'/proxy/add', json={
                'url': form['href']
            }, headers=headers)
            form['href'] = '{}/proxy/{}'.format(host, res.json()['uuid'])

def _register_things(s, data):
    """Registers new things in the directory"""
    if isinstance(data, dict):
        data = [data]

    uuids = list()
    for schema in data:
        new_thing = Thing(s, schema, uuid4().hex)

        if 'PROXY' in current_app.config:
            try:
                _add_proxy_endpoints(current_app.config['PROXY'], new_thing.schema.get('properties', dict()))
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                raise APIException('Could not reach proxy', 504)

        new_thing.save()
        uuids.append(new_thing.uuid)
    return uuids

@bp.route('/register', methods=['POST'])
def register():
    """POST request for performing device registration"""
    # If only a single description provided wrap in a list
    data = request.get_json()
    s = get_db()

    response = {
        "uuids": _register_things(s, data),
    }
    return (jsonify(response), 201, None)

async def _coap_request(url):
    """Performs a CoAP request"""
    c = await aiocoap.Context.create_client_context()
    message = aiocoap.Message(code=GET, uri=url)
    response = await c.request(message).response
    return json.loads(response.payload.decode())

@bp.route('/register_url', methods=['POST'])
def register_url():
    """POST request for registering a thing by a given URL"""
    data = request.get_json()
    if data is None:
        url = None
    else:
        url = request.get_json().get('url', None)

    if url is None:
        raise APIException('Missing data URL')

    s = get_db()
    if 'http' in url:
        try:
            td_response = requests.get(url)
            tds = td_response.json()
        except:
            raise APIException('Error getting schema at URL')

        uuids = _register_things(s, tds)
    elif 'coap' in url:
        try:
            tds = asyncio.new_event_loop().run_until_complete(_coap_request(url))
        except:
            raise APIException('Error getting schema at URL')

        uuids = _register_things(s, tds)
    else:
        raise APIException('Cannot parse this URL', 501)
    response = {
        'uuids': uuids,
    }
    return (jsonify(response), 201, None)

@bp.route('/<uuid>/groups', methods=['POST'])
def add_group(uuid):
    """POST request for adding groups"""
    body = request.get_json()
    s = get_db()
    db_thing = Thing.get_by_uuid(s, uuid=uuid)
    db_thing.add_group(body['group'])
    db_thing.save()
    response = {
        "message": "updated"
    }
    return (jsonify(response), 200, None)

@bp.route('/<uuid>/groups/<group>', methods=['DELETE'])
def del_group(uuid, group):
    """DELETE request for removing groups"""
    s = get_db()
    db_thing = Thing.get_by_uuid(s, uuid=uuid)
    db_thing.del_group(group)
    db_thing.save()
    return jsonify({
        'message': 'group removed'
    })

@bp.route('/<uuid>', methods=['DELETE'])
def delete_thing(uuid):
    """DELETE request for removing device from directory"""
    s = get_db()
    db_thing = Thing.get_by_uuid(s, uuid=uuid)
    db_thing.delete()
    response = (jsonify({"message": "deleted"}), 200, None)
    return response
