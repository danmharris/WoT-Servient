"""This module contains method for performing auth checks on endpoints"""
# pylint: disable=inconsistent-return-statements
# Disabled this check as before_request implementations should not return anything on success
from flask import jsonify, current_app, request
import jwt

def check_auth_exclude(exclude):
    """Allow certain endpoint names to be excluded from auth checks"""
    def wrapper():
        if request.endpoint not in exclude:
            return check_auth()
    return wrapper

def check_auth_include(include):
    """Allow certain endpoint names to be included in auth checks"""
    def wrapper():
        if request.endpoint in include:
            return check_auth()
    return wrapper

def check_auth():
    """Checks the presence and validity of a JWT in a request"""
    if current_app.config.get('AUTH'):
        header = request.headers.get('Authorization')
        if header is not None:
            try:
                token = header.split(' ')[1]
                jwt.decode(token, current_app.config.get('SECRET'), algorithms=['HS256'])
                return
            except IndexError:
                pass
            except jwt.InvalidTokenError:
                pass
        return (jsonify({
            'message': 'No auth'
        }), 401, None)
