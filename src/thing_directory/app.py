from flask import Flask, jsonify
from thing_directory import directory
from common.db import close_db
from common.exception import APIException

def create_app(app_config=None):
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
        return (jsonify({'message': err.message}), err.status, None)

    return app
