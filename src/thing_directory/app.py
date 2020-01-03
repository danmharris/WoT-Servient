"""Entry module to thing directory API"""
from flask import Flask, jsonify
from thing_directory import directory
from wot.common.db import close_db
from wot.common.exception import APIException

def create_app(app_config=None):
    """Creates the API with configuration if provided

    Takes 1 (optional) argument:
    app_config - dictionary of configuration parameters
    """
    app = Flask(__name__)
    if app_config is None:
        app.config['DB'] = 'things.db'
        app.config['PROXY'] = 'http://localhost:5001'
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(directory.bp)
    app.teardown_appcontext(close_db)

    @app.errorhandler(APIException)
    def handle_api_error(err):
        """Assign error handler to all endpoints when APIException thrown"""
        return (jsonify({'message': err.message}), err.status, None)

    return app
