"""Module for proxy endpoints"""
from uuid import uuid4
from wot.common.exception import APIException

class Endpoint:
    """Class representing proxy endpoint"""
    @staticmethod
    def get_by_uuid(s, uuid):
        """Gets an endpoint URL from the database

        Takes 1 argument:
        uuid - UUID of the endpoint to retrieve
        """
        try:
            db_endpoint = s[uuid]
            return Endpoint(s, db_endpoint, uuid)
        except Exception:
            raise APIException('Endpoint not found', 404)
    def __init__(self, dbh, url, uuid=None):
        """Initialise endpoint

        Takes 3 arguments:
        dbh - Database handler
        url - Endpoint location
        uuid - UUID to give the endpoint (defaults to random uuidv4)
        """
        if uuid is None:
            uuid = uuid4().hex
        self.dbh = dbh
        self.url = url
        self.uuid = uuid
    def save(self):
        """Updates the URL in the database"""
        self.dbh[self.uuid] = self.url
    def delete(self):
        """Deletes the URL from the database"""
        del self.dbh[self.uuid]
