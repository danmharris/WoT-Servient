from flask import Blueprint, jsonify, request, current_app
from common.td_util import ThingDescriptionBuilder, ObjectBuilder, StringBuilder
from binding.producer import Producer
import asyncio
import json
import aiocoap
from aiocoap.numbers.codes import PUT, GET, POST

# API Information was read from https://github.com/glenndehaan/ikea-tradfri-coap-docs

class IKEAProducer(Producer):
    def __init__(self):
        super().__init__()
    def produce(self):
        loop = asyncio.get_event_loop()
        discovered = list()
        try:
            for dev in loop.run_until_complete(discover()):
                prefix = 'ikea:{}'.format(dev['9003'])
                td = _generate_td(prefix, dev)
                bp = _produce_blueprint('/'+prefix, dev)
                discovered.append((bp, td))
        except Exception as err:
            print(err)
        return discovered

async def _create_context():
    config = current_app.config['IKEA']

    c = await aiocoap.Context.create_client_context()
    c.client_credentials.load_from_dict({
        'coaps://{}:5684/*'.format(config['gateway']): {
            'dtls': {
                'psk': config['psk'].encode(),
                'client-identity': config['identity'].encode(),
            }
        }
    })
    return c

async def _get_device_info(address, c=None):
    config = current_app.config['IKEA']
    if c is None:
        c = await _create_context()
    device_info_request = aiocoap.Message(code=GET, uri='coaps://{}:5684/15001/{}'.format(config['gateway'], address))
    device_info_response = await c.request(device_info_request).response
    return json.loads(device_info_response.payload.decode())

async def _set_state(payload, address):
    config = current_app.config['IKEA']
    c = await _create_context()
    request = aiocoap.Message(code=PUT, payload=payload, uri='coaps://{}:5684/15001/{}'.format(config['gateway'], address))
    await c.request(request).response

async def discover():
    config = current_app.config['IKEA']
    c = await _create_context()
    devices_request = aiocoap.Message(code=GET, uri='coaps://{}:5684/15001'.format(config['gateway']))
    devices_response = await c.request(devices_request).response
    found_devices = json.loads(devices_response.payload.decode())

    discovered = list()
    for dev in found_devices:
        device_info = await _get_device_info(dev, c)
        discovered.append(device_info)
    return discovered

def _produce_blueprint(prefix, device_info):
    bp = Blueprint(prefix, __name__, url_prefix=prefix)
    loop = asyncio.get_event_loop()
    address = device_info['9003']

    def set_state():
        data = request.get_json()

        if '3312' in device_info:
            payload = b'{"3311":[{"5850":'
        payload = payload + str(data['state']).encode() + b'}]}'

        loop.run_until_complete(_set_state(payload, address))
        return jsonify({
            'message': 'updated'
        })

    def get_state():
        device_info = loop.run_until_complete(_get_device_info(address))

        if '3312' in device_info:
            value = device_info['3312'][0]['5850']

        return jsonify({
            'state': value
        })

    if '3312' in device_info:
        bp.add_url_rule('/state', methods=['GET'], view_func=get_state)
        bp.add_url_rule('/state', methods=['POST'], view_func=set_state)

    return bp

def _generate_td(prefix, device_info):
    hostname = current_app.config['HOSTNAME']

    security = {
        'bearer_token': {
            'scheme': 'bearer',
            'alg': 'HS256',
            'in': 'header',
            'name': 'Authorization'
        }
    }
    td = ThingDescriptionBuilder('urn:{}'.format(prefix), device_info['9001'], security=security)

    schema = ObjectBuilder()
    schema.add_number('state')

    response = ObjectBuilder()
    response.add_string('message')

    if '3312' in device_info:
        td.add_action('setState', '{}/{}/state'.format(hostname, prefix), schema.build(), response.build())
        td.add_property('state', '{}/{}/state'.format(hostname, prefix), schema.build())

    return td.build()
