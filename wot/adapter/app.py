from flask import Flask, Blueprint, jsonify
import wot.adapter.device.tplink

def create_app():
    app = Flask(__name__)

    device_bp = Blueprint('devices', __name__, '/devices')
    schemas = list()

    devices = wot.adapter.device.tplink.get_things()
    for device in devices:
        app.register_blueprint(device.blueprint)
        schemas.append(device.schema)

    @app.route('/things', methods=['GET'])
    def things():
        return jsonify(schemas)

    return app
