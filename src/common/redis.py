"""Utility module to connect to redis database in Flask"""
import redis
from flask import current_app, g

def get_redis():
    """Creates a redis connection and stores in Flask gloval if not already established

    Connects to address at REDIS configuration key
    """
    if 'redis' not in g:
        g.redis = redis.Redis(host=current_app.config['REDIS'], port=6379, db=0)
    return g.redis
