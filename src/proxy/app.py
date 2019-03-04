from flask import Flask, jsonify
from proxy import proxy
from common.db import close_db
from common.auth import check_auth
from common.exception import APIException

def create_app(app_config=None):
    app = Flask(__name__)
    if app_config is None:
        app.config['DB'] = 'endpoints.db'
        app.config['REDIS'] = 'localhost'
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(proxy.bp)
    app.teardown_appcontext(close_db)
    app.before_request(check_auth)

    @app.errorhandler(APIException)
    def api_error_handler(err):
        return (jsonify({'message': err.message}), err.status, None)

    return app
