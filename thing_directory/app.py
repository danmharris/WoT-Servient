from flask import Flask
from thing_directory import directory
from common.db import close_db

#TODO: Change PROXY config option to command line argument

def create_app(app_config=None):
    app = Flask(__name__)
    if app_config is None:
        app.config['DB'] = 'things.db'
        app.config['PROXY'] = 'http://localhost:5001'
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(directory.bp)
    app.teardown_appcontext(close_db)
    return app
