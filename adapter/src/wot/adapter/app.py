import asyncio
import threading
from flask import Flask, jsonify
from flask_cors import CORS

import wot.adapter.device.tplink
from wot.adapter.config import Config
from wot.adapter.device.tasmota import TasmotaDiscovery

class DiscoveryThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.loop = None
        self.event = threading.Event()
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.call_soon(self.event.set)
        self.loop.run_forever()
    def run_coro(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

def create_app(app_config=None):
    Config.load()

    app = Flask(__name__)
    CORS(app)

    schemas = list()
    if 'tplink' in Config.get('plugins'):
        devices = wot.adapter.device.tplink.get_things()
        for device in devices:
            app.register_blueprint(device.blueprint)
            schemas.append(device.schema)

    discovery = DiscoveryThread()
    discovery.start()
    discovery.event.wait()
    if 'tasmota' in Config.get('plugins'):
        tasmota = TasmotaDiscovery(schemas, app)
        discovery.run_coro(tasmota.discover())

    @app.route('/things', methods=['GET'])
    def things():
        return jsonify(schemas)

    return app
