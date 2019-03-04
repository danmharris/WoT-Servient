import dbm, uuid
from common.exception import APIException

class Thing:
    @staticmethod
    def get_by_uuid(s, uuid):
        try:
            thing = s[uuid]
            return Thing(s, thing, uuid)
        except:
            raise APIException('Thing not found', 404)
    def __init__(self, dbh, schema = {}, uuid= uuid.uuid4().hex):
        self.dbh = dbh
        self.schema = schema
        self.uuid = uuid
    def add_group(self, group):
        if 'groups' in self.schema:
            self.schema['groups'].append(group)
        else:
            self.schema.update({ "groups": [group]})
    def get_groups(self):
        if 'groups' in self.schema:
            return self.schema['groups']
        else:
            return []
    def del_group(self, group):
        if 'groups' in self.schema:
            self.schema['groups'] = [g for g in self.schema['groups'] if g != group]
    def save(self):
        self.dbh[self.uuid] = self.schema
    def delete(self):
        del self.dbh[self.uuid]
