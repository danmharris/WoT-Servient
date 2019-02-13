from flask import Flask, jsonify
from binding import tplink

#TODO: Add Thing Description builder based on database

descriptions = list()

def create_app(app_config=None):
    app = Flask(__name__)
    if app_config is None:
        app.config['BINDINGS'] = [tplink.TpLinkProducer()]
    else:
        app.config.from_mapping(app_config)

    for binding in app.config['BINDINGS']:
        for bp, td in binding.produce():
            app.register_blueprint(bp)
            descriptions.append(td)

    @app.route('/', methods=['GET'])
    def get_descriptions():
        return jsonify(descriptions)

    return app
