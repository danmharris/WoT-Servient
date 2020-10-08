from wot.directory.routes import bp
from wot.directory.db import close_db
from wot.directory.config import Config

from flask import Flask

def create_app():
    Config.load()

    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix='/api/v1/directory')
    app.teardown_appcontext(close_db)

    return app
