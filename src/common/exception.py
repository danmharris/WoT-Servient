"""Utility module for exception handling in Flask"""
class APIException(Exception):
    """Generic API exception to be returned from all endpoints"""
    def __init__(self, message='', status=400):
        """Initialises with a message and status code

        Status code defaults to 400 (BAD REQUEST)
        """
        super().__init__(self)
        self.status = status
        self.message = message
