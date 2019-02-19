from flask import Blueprint, jsonify, request, current_app
from common.td_util import ThingDescriptionBuilder, ObjectBuilder, StringBuilder
from binding.producer import Producer
import asyncio
import json
from aiocoap import Message, Context
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
                prefix = 'ikea:{}'.format(dev['address'])
                if dev['name'] == 'TRADFRI outlet':
                    td = _generate_plug_td(prefix)
                    bp = _produce_plug_blueprint('/'+prefix, dev['address'])
                    discovered.append((bp, td))
        except Exception as err:
            print(err)
        return discovered

async def _create_context():
    c = await Context.create_client_context()
    c.client_credentials.load_from_dict({
        'coaps://192.168.3.100:5684/*': {
            'dtls': {
                'psk': b'ZSI7flwhfzpe0UOf',
                'client-identity': b'test',
            }
        }
    })
    return c

async def _get_device_info(address, c=None):
    if c is None:
        c = await _create_context()
    device_info_request = Message(code=GET, uri='coaps://192.168.3.100:5684/15001/{}'.format(address))
    device_info_response = await c.request(device_info_request).response
    return json.loads(device_info_response.payload)

async def _set_state(state, address):
    c = await _create_context()
    if state == 1:
        payload = b'{"3311":[{"5850":1}]}'
    elif state == 0:
        payload = b'{"3311":[{"5850":0}]}'
    request = Message(code=PUT, payload=payload, uri='coaps://192.168.3.100:5684/15001/{}'.format(address))
    await c.request(request).response

async def discover():
    c = await _create_context()
    devices_request = Message(code=GET, uri='coaps://192.168.3.100:5684/15001')
    devices_response = await c.request(devices_request).response
    found_devices = json.loads(devices_response.payload)

    discovered = list()
    for dev in found_devices:
        device_info = await _get_device_info(dev, c)

        discovered.append({
            'address': dev,
            'name': device_info['9001']
        })
    return discovered

def _produce_plug_blueprint(prefix, address):
    bp = Blueprint(prefix, __name__, url_prefix=prefix)
    loop = asyncio.get_event_loop()

    @bp.route('/state', methods=['POST'])
    def set_state():
        data = request.get_json()
        loop.run_until_complete(_set_state(data['state'], address))
        return jsonify({
            'message': 'updated'
        })

    @bp.route('/state', methods=['GET'])
    def get_state():
        device_info = loop.run_until_complete(_get_device_info(address))
        return jsonify({
            'state': device_info['3312'][0]['5850']
        })

    return bp

def _generate_plug_td(prefix):
    hostname = current_app.config['HOSTNAME']
    td = ThingDescriptionBuilder('urn:{}'.format(prefix), 'TRADFRI outlet')

    schema = ObjectBuilder()
    schema.add_number('state')

    response = ObjectBuilder()
    response.add_string('message')

    td.add_action('setState', '{}/{}/state'.format(hostname, prefix), schema.build(), response.build())
    td.add_property('state', '{}/{}/state'.format(hostname, prefix), schema.build())
    return td.build()

#TODO: Need a way to automate the generating the PSK rather than doing it once manually then hardcoding key

# async def generate_psk():
#     c = await Context.create_client_context()
#     c.client_credentials.load_from_dict({
#         'coaps://192.168.3.100:5684/*': {
#             'dtls': {
#                 'psk': b'REPLACE_ME_WITH_KEY',
#                 'client-identity': b'Client_identity',
#             }
#         }
#     })

#     payload=b'{"9090":"test"}'
#     request = Message(code=POST, payload=payload, uri='coaps://192.168.3.100:5684/15011/9063')
#     response = await c.request(request).response
#     print(response.payload)
