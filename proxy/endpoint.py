import dbm, uuid

class Endpoint:
    @staticmethod
    def get_by_uuid(s, uuid):
        try:
            db_endpoint = s[uuid]
            return Endpoint(s, db_endpoint, uuid)
        except Exception:
            raise Exception({
                'message': 'Endpoint not found'
            })
    def __init__(self, dbh, url, uuid = uuid.uuid4().hex):
        self.dbh = dbh
        self.url = url
        self.uuid = uuid
    def save(self):
        self.dbh[self.uuid] = self.url
    def delete(self):
        del self.dbh[self.uuid]
