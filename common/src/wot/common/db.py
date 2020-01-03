"""This module contains the ability to create shelve database in Flask"""
import shelve
from flask import current_app, g

def get_db():
    """Get the DB object, creating it if not yet open"""
    if 'db' not in g:
        g.db = shelve.open(current_app.config['DB'])
    return g.db

def close_db(e=None):
    """Close the DB object"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
