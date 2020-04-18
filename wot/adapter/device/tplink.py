from wot.adapter.schema.tplink import HS100
from wot.adapter.thing_producer import ThingProducer

from pyHS100 import Discover
from flask import jsonify, request

def get_things():
    producers = list()
    for plug in Discover.discover().values():
        producers.append(_produce_tplink(plug))

    return producers

def _produce_tplink(plug):
    mac = plug.mac.replace(':', '').lower()

    device_schema = dict(HS100)
    device_schema['id'] = mac
    device_schema['title'] = plug.alias
    device_schema['base'] = '/things/' + mac

    producer = ThingProducer(device_schema)

    def read_state():
        print(device_schema['id'])
        state = True if plug.state == 'ON' else False
        return jsonify({'state': state})

    def write_state():
        new_state = request.get_json()['state']
        plug.state = 'ON' if new_state == True else 'OFF'
        return jsonify({'state': new_state})

    def toggle_state():
        plug.state = 'ON' if plug.state == 'OFF' else 'OFF'
        return ''

    producer.setPropertyReadHandler('state', read_state)
    producer.setPropertyWriteHandler('state', write_state)
    producer.setActionHandler('toggle', toggle_state)

    return producer
