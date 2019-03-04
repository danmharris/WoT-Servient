class APIException(Exception):
    def __init__(self, message='', status=400):
        super().__init__(self)
        self.status = status
        self.message = message
