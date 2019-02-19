from flask import Flask, jsonify
from binding import tplink, ikea
from common.auth import check_auth

#TODO: Add Thing Description builder based on database

def create_app(app_config=None):
    app = Flask(__name__)
    if app_config is None:
        app.config['BINDINGS'] = ['tplink', 'ikea']
        app.config['HOSTNAME'] = 'http://localhost:5000'
    else:
        app.config.from_mapping(app_config)
    app.before_request(check_auth)

    descriptions = dict()

    with app.app_context():
        for binding_name in app.config['BINDINGS']:
            if binding_name == 'tplink':
                binding = tplink.TpLinkProducer()
            elif binding_name == 'ikea':
                binding = ikea.IKEAProducer()

            for bp, td in binding.produce():
                app.register_blueprint(bp)
                if td['id'] not in descriptions:
                    descriptions[td['id']] = td

    @app.route('/', methods=['GET'])
    def get_descriptions():
        return jsonify(list(descriptions.values()))

    return app
