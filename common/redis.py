import redis
from flask import current_app, g

def get_redis():
    if 'redis' not in g:
        g.redis = redis.Redis(host=current_app.config['redis'], port=6379, db=0)
    return g.redis
