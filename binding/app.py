from flask import Flask, jsonify
from binding import tplink
from common.db import get_db, close_db

#TODO: Add Thing Description builder based on database

def create_app(app_config=None):
    app = Flask(__name__)
    if app_config is None:
        app.config['DB'] = 'things.db'
    else:
        app.config.from_mapping(app_config)
    app.register_blueprint(tplink.bp)
    app.teardown_appcontext(close_db)

    @app.route('/', methods=['GET'])
    def get_descriptions():
        s = get_db()
        descriptions = list()
        for id in s:
            category = id.split(':')[0]
            if category == 'tp_link':
                descriptions.append(tplink.build_td(id))
        return jsonify(descriptions)

    return app
