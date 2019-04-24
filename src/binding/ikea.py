"""This module provides support for IKEA Tradfri devices"""
import asyncio
import json
from flask import Blueprint, jsonify, request, current_app
import aiocoap
from aiocoap.numbers.codes import PUT, GET
from common.td_util import ThingDescriptionBuilder, ObjectBuilder
from binding.producer import Producer

# API Information was read from https://github.com/glenndehaan/ikea-tradfri-coap-docs

class IKEAProducer(Producer):
    """Producer (binding template) for IKEA Tradfri devices"""
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
    """Utility method to create aiocoap connection context with credentials"""
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
    """Async method to get the info from a device

    Takes two arguments:
    address - The address of the device (on gateway)
    c - The connection to use (created if not passed)
    """
    config = current_app.config['IKEA']
    if c is None:
        c = await _create_context()
    uri = 'coaps://{}:5684/15001/{}'.format(config['gateway'], address)
    device_info_request = aiocoap.Message(code=GET, uri=uri)
    device_info_response = await c.request(device_info_request).response
    return json.loads(device_info_response.payload.decode())

async def _set_state(payload, address):
    """Updates the state of the device

    Takes two arguments:
    payload - The payload to send to the device
    address - The address of the device (on gateway)
    """
    config = current_app.config['IKEA']
    c = await _create_context()
    uri = 'coaps://{}:5684/15001/{}'.format(config['gateway'], address)
    state_request = aiocoap.Message(code=PUT, payload=payload, uri=uri)
    await c.request(state_request).response

async def discover():
    """Discover devices on the network from the gateway

    Returns a list of discovered devices and their info
    """
    config = current_app.config['IKEA']
    c = await _create_context()
    uri = 'coaps://{}:5684/15001'.format(config['gateway'])
    devices_request = aiocoap.Message(code=GET, uri=uri)
    devices_response = await c.request(devices_request).response
    found_devices = json.loads(devices_response.payload.decode())

    discovered = list()
    for dev in found_devices:
        device_info = await _get_device_info(dev, c)
        discovered.append(device_info)
    return discovered

def _produce_blueprint(prefix, device_info):
    """Produces blueprint for IKEA tradfri products

    Takes 2 arguments:
    prefix - To prepend to the blueprint
    device_info - Dictionary containing device info
    """
    bp = Blueprint(prefix, __name__, url_prefix=prefix)
    loop = asyncio.get_event_loop()
    address = device_info['9003']

    def set_state():
        """POST request to update the state of a device

        Takes JSON input of the new state
        """
        data = request.get_json()

        if '3312' in device_info:
            payload = b'{"3311":[{"5850":'
        payload = payload + str(data['state']).encode() + b'}]}'

        loop.run_until_complete(_set_state(payload, address))
        return jsonify({
            'message': 'updated'
        })

    def get_state():
        """Gets the current state of the device

        Returns this as JSON data
        """
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
    """Generates thing description for IKEA products

    Takes two arguments:
    prefix - prefix for all URIs (relative to this host)
    device_info - Dictionary with info for this device
    """
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
        td.add_action('setState', '{}/{}/state'.format(hostname, prefix),
                      schema.build(), response.build())
        td.add_property('state', '{}/{}/state'.format(hostname, prefix), schema.build())

    return td.build()
