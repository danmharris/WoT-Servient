
import os.path
from flask import Flask, Blueprint, jsonify
import yaml
import wot.adapter.device.tplink

CONFIG_LOCATION = '/opt/wot/config/adapter.yaml'

def create_app(app_config=None):
    app = Flask(__name__)

    if app_config is None:
        app.config.from_object('wot.adapter.config')
        if os.path.exists(CONFIG_LOCATION):
            with open(CONFIG_LOCATION, 'r') as stream:
                app.config.from_mapping(yaml.safe_load(stream))

    schemas = list()

    if 'tplink' in app.config['ENABLED']:
        devices = wot.adapter.device.tplink.get_things()
        for device in devices:
            app.register_blueprint(device.blueprint)
            schemas.append(device.schema)

    @app.route('/things', methods=['GET'])
    def things():
        return jsonify(schemas)

    return app
