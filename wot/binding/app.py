"""Main entry point for binding Flask API"""
from flask import Flask, jsonify
from wot.binding import tplink, ikea
from wot.common.auth import check_auth

def create_app(app_config=None):
    """Creates Flask APP

    Optionally takes configuration file as dictionary, this will be parsed if present
    """
    app = Flask(__name__)
    if app_config is None:
        app.config.from_object('wot.binding.config')
        app.config.from_envvar('WOT_BINDING_CONFIG', silent=True)
    else:
        app.config.from_mapping(app_config)

    descriptions = dict()

    with app.app_context():
        for binding_name in app.config['BINDINGS']:
            if binding_name == 'tplink':
                binding = tplink.TpLinkProducer()
            elif binding_name == 'ikea':
                binding = ikea.IKEAProducer()

            for bp, td in binding.produce():
                bp.before_request(check_auth)
                app.register_blueprint(bp)
                if td['id'] not in descriptions:
                    descriptions[td['id']] = td

    @app.route('/', methods=['GET'])
    def get_descriptions():
        """GET request that returns thing descriptions for all devices found"""
        return jsonify(list(descriptions.values()))

    return app
