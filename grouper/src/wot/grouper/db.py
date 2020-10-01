from wot.grouper.config import Config

from flask import current_app, g
from tinydb import TinyDB

def get_db():
    if 'db' not in g:
        g.db = TinyDB(Config.get('db'))
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
