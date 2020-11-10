import os.path
from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from wot.adapter.config import Config
import wot.adapter.device.tplink

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

    @app.route('/things', methods=['GET'])
    def things():
        return jsonify(schemas)

    return app
