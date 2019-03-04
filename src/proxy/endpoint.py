import dbm
from uuid import uuid4
from common.exception import APIException

class Endpoint:
    @staticmethod
    def get_by_uuid(s, uuid):
        try:
            db_endpoint = s[uuid]
            return Endpoint(s, db_endpoint, uuid)
        except Exception:
            raise APIException('Endpoint not found', 404)
    def __init__(self, dbh, url, uuid=None):
        if uuid is None:
            uuid = uuid4().hex
        self.dbh = dbh
        self.url = url
        self.uuid = uuid
    def save(self):
        self.dbh[self.uuid] = self.url
    def delete(self):
        del self.dbh[self.uuid]
