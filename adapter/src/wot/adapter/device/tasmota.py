import asyncio
import re
import paho.mqtt.client as mqtt
import json
import requests
from flask import jsonify, request

from wot.adapter.config import Config
from wot.adapter.schema.tasmota import PLUG
from wot.adapter.thing_producer import ThingProducer

class TasmotaDiscovery:
    def __init__(self, schemas, app):
        self.discovered = list()
        self.registered = list()
        self.pattern = re.compile('(?P<prefix>[^/]+)/(?P<topic>[^/]+)/(?P<arg>[^/]+)')
        self.schemas = schemas
        self.app = app

    async def discover(self):
        loop = asyncio.get_event_loop()
        client = mqtt.Client()
        client.loop_start()

        connected = asyncio.Event()
        def on_connect(*args):
            loop.call_soon_threadsafe(connected.set)
        client.on_connect = on_connect

        await loop.run_in_executor(None, client.connect, Config.get('mqtt'))
        await connected.wait()

        client.subscribe('tele/+/STATE')
        client.subscribe('stat/+/STATUS5')

        def on_message(*args):
            loop.call_soon_threadsafe(self._on_message, *args)
        client.on_message = on_message

    def new_thing(self, status):
        mac = status['Mac'].replace(':', '').lower()
        ip = status['IPAddress']
        base_uri = 'http://'+ip+'/cm?cmnd='

        name = requests.get(base_uri+'FriendlyName1').json()['FriendlyName1']

        device_schema = dict(PLUG)
        device_schema['id'] = mac
        device_schema['title'] = name

        producer = ThingProducer(device_schema)

        def read_state():
            r = requests.get(base_uri+'Power')
            state = True if r.json()['POWER'] == 'ON' else False
            return jsonify(state)

        def write_state():
            new_state = request.get_json()
            arg = 'ON' if new_state == True else 'OFF'
            requests.get(base_uri+'Power%20'+arg)

            return jsonify(new_state)

        def toggle_state():
            requests.get(base_uri+'Power%20Toggle')
            return ''

        def read_power():
            r = requests.get(base_uri+'Status%208')
            state = r.json()['StatusSNS']['ENERGY']['Power']
            return jsonify(state)

        producer.setPropertyReadHandler('state', read_state)
        producer.setPropertyWriteHandler('state', write_state)
        producer.setActionHandler('toggle', toggle_state)
        producer.setPropertyReadHandler('power', read_power)

        self.app.register_blueprint(producer.blueprint)
        self.schemas.append(producer.schema)

    def _on_message(self, client, userdata, msg):
        topic = self.pattern.match(msg.topic)
        name = topic.group('topic')

        if topic.group('prefix') == 'tele' and topic.group('arg') == 'STATE':
            # state telemetry
            if name not in self.discovered:
                client.publish('cmnd/'+name+'/STATUS', payload=5)
                self.discovered.append(name)
        elif topic.group('prefix') == 'stat' and topic.group('arg') == 'STATUS5':
            # response to status request
            if name not in self.registered:
                content = json.loads(msg.payload)
                self.new_thing(content['StatusNET'])
                self.registered.append(name)
