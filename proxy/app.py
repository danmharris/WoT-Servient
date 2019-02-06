from flask import Flask
from proxy import proxy
from common.db import close_db

def create_app(app_config=None):
    app = Flask(__name__)
    if app_config is None:
        app.config['DB'] = 'endpoints.db'
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(proxy.bp)
    app.teardown_appcontext(close_db)
    return app
