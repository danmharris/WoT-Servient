from flask import Blueprint, request, jsonify, Response
from proxy.endpoint import Endpoint
from common.db import get_db
import requests

bp = Blueprint('proxy', __name__, url_prefix='/proxy')

@bp.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    s = get_db()
    endpoint = Endpoint(s, data['url'])
    endpoint.save()
    response = {
        'uuid': endpoint.uuid,
    }
    return jsonify(response)

@bp.route('/<uuid>/details', methods=['GET'])
def get(uuid):
    try:
        s = get_db()
        endpoint = Endpoint.get_by_uuid(s, uuid)
        return jsonify({
            'url': endpoint.url,
        })
    except Exception as err:
        return (str(err), 404, None)

@bp.route('/<uuid>', methods=['GET','POST'])
def req(uuid):
    try:
        s = get_db()
        endpoint = Endpoint.get_by_uuid(s, uuid)
        try:
            if request.method == 'GET':
                r = requests.get(endpoint.url, timeout=1)
            elif request.method == 'POST':
                if request.is_json:
                    r = requests.post(endpoint.url, json=request.get_json())
                else:
                    r = requests.post(endpoint.url, data=request.data)
            response = Response(r.text)
            response.headers['Content-Type'] = r.headers['content-type']
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            return (jsonify({
                'message': 'Cannot reach thing'
            }), 504, None)
    except Exception as err:
        return (str(err), 404, None)

@bp.route('/<uuid>', methods=['PUT'])
def update(uuid):
    data = request.get_json()
    s = get_db()
    try:
        endpoint = Endpoint.get_by_uuid(s, uuid)
        if 'url' in data:
            endpoint.url = data['url']
        endpoint.save()
        return jsonify({
            'message': 'Updated'
        })
    except Exception as err:
        return (str(err), 404, None)
