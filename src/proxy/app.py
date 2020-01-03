"""Entry module for proxy Flask API"""
from flask import Flask, jsonify
from proxy import proxy
from wot.common.db import close_db
from wot.common.exception import APIException

def create_app(app_config=None):
    """Constructs the API with configuration if provided

    Takes 1 argument (optional):
    app_config: Dictionary of the config to be parsed
    """
    app = Flask(__name__)
    if app_config is None:
        app.config['DB'] = 'endpoints.db'
        app.config['REDIS'] = 'localhost'
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(proxy.bp)
    app.teardown_appcontext(close_db)

    @app.errorhandler(APIException)
    def api_error_handler(err):
        """Assign error handler to all endpoints when APIException thrown"""
        return (jsonify({'message': err.message}), err.status, None)

    return app
