from flask import jsonify, current_app, request
import jwt

def check_auth_exclude(exclude=list()):
    def wrapper():
        if request.endpoint not in exclude:
            return check_auth()
    return wrapper

def check_auth_include(include=list()):
    def wrapper():
        if request.endpoint in include:
            return check_auth()
    return wrapper

def check_auth():
    if current_app.config.get('AUTH') == True:
        header = request.headers.get('Authorization')
        if header is not None:
            token = header.split(' ')[1]
            try:
                jwt.decode(token, current_app.config.get('SECRET'), algorithm='HS256')
                return
            except:
                pass
        return (jsonify({
            'message': 'No auth'
        }), 401, None)
