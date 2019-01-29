import dbh, uuid

class Endpoint:
    def __init__(self, dbh, url, uuid = uuid.uuid4().hex):
        self.dbh = dbh
        self.url = url
        self.uuid = uuid
    def save(self):
        self.dbh[self.uuid] = self.url
    def delete(self):
        del self.dbh[self.uuid]
