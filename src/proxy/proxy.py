from flask import Blueprint, request, jsonify, Response
from proxy.endpoint import Endpoint
from common.db import get_db
from common.redis import get_redis
from common.exception import APIException
from common.auth import check_auth_exclude
import requests
import asyncio
import aiocoap
from aiocoap.numbers.codes import GET
import json

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

async def _coap_request(url):
    c = await aiocoap.Context.create_client_context()
    message = aiocoap.Message(code=GET, uri=url)
    response = await c.request(message).response
    return response.payload

@bp.route('/<uuid>', methods=['GET'])
def req(uuid):
    s = get_db()
    endpoint = Endpoint.get_by_uuid(s, uuid)
    redis = get_redis()
    try:
        if redis.exists(uuid):
            response = Response(redis.hget(uuid, 'data'))
            response.headers['Content-Type'] = redis.hget(uuid, 'content_type')
        else:
            if 'coap://' in endpoint.url:
                data = asyncio.new_event_loop().run_until_complete(_coap_request(endpoint.url))
                redis.hset(uuid, 'data', data)
                redis.expire(uuid, 30)
                response = Response(data)
            else:
                r = requests.get(endpoint.url, timeout=1, headers=request.headers)
                redis.hset(uuid, 'data', r.text)
                redis.hset(uuid, 'content_type', r.headers['content-type'])
                redis.expire(uuid, 30)
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
