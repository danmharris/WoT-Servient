"""Entry module to thing directory API"""
from flask import Flask, jsonify
from wot.thing_directory import directory
from wot.common.db import close_db
from wot.common.exception import APIException

def create_app(app_config=None):
    """Creates the API with configuration if provided

    Takes 1 (optional) argument:
    app_config - dictionary of configuration parameters
    """
    app = Flask(__name__)
    if app_config is None:
        app.config.from_object('wot.thing_directory.config')
        app.config.from_envvar('WOT_THING_DIRECTORY_CONFIG', silent=True)
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(directory.bp)
    app.teardown_appcontext(close_db)

    @app.errorhandler(APIException)
    def handle_api_error(err):
        """Assign error handler to all endpoints when APIException thrown"""
        return (jsonify({'message': err.message}), err.status, None)

    return app
