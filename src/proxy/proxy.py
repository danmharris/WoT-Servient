from flask import Blueprint, request, jsonify, Response
from proxy.endpoint import Endpoint
from common.db import get_db
from common.redis import get_redis
from common.exception import APIException
from common.auth import check_auth_exclude
import requests

bp = Blueprint('proxy', __name__, url_prefix='/proxy')
bp.before_request(check_auth_exclude(['proxy.req']))

@bp.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    s = get_db()
    endpoint = Endpoint(s, data['url'])
    endpoint.save()
    response = {
        'uuid': endpoint.uuid,
    }
    return (jsonify(response), 201, None)

@bp.route('/<uuid>/details', methods=['GET'])
def get(uuid):
    s = get_db()
    endpoint = Endpoint.get_by_uuid(s, uuid)
    return jsonify({
        'url': endpoint.url,
    })

@bp.route('/<uuid>', methods=['GET','POST'])
def req(uuid):
    s = get_db()
    endpoint = Endpoint.get_by_uuid(s, uuid)
    redis = get_redis()
    try:
        if request.method == 'GET' and redis.exists(uuid):
            response = Response(redis.hget(uuid, 'data'))
            response.headers['Content-Type'] = redis.hget(uuid, 'content_type')
        else:
            print('making request!')
            if request.method == 'GET':
                r = requests.get(endpoint.url, timeout=1, headers=request.headers)
                redis.hset(uuid, 'data', r.text)
                redis.hset(uuid, 'content_type', r.headers['content-type'])
                redis.expire(uuid, 30)
            elif request.method == 'POST':
                if request.is_json:
                    r = requests.post(endpoint.url, json=request.get_json(), headers=request.headers)
                else:
                    r = requests.post(endpoint.url, data=request.data, headers=request.headers)
            response = Response(r.text)
            response.headers['Content-Type'] = r.headers['content-type']
        return response
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise APIException('Cannot reach thing', 504)

@bp.route('/<uuid>', methods=['PUT'])
def update(uuid):
    data = request.get_json()
    s = get_db()
    endpoint = Endpoint.get_by_uuid(s, uuid)
    if 'url' in data:
        endpoint.url = data['url']
    endpoint.save()
    return jsonify({
        'message': 'Updated'
    })
