from wot.grouper.routes import bp
from wot.grouper.db import close_db

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix='/things')
    app.teardown_appcontext(close_db)

    return app
