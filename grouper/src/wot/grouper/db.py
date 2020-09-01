from flask import current_app, g
from tinydb import TinyDB

def get_db():
    if 'db' not in g:
        g.db = TinyDB('grouper.json')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
