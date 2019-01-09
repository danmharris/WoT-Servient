import dbm, json, uuid

class Thing:
    @staticmethod
    def get_by_uuid(s, uuid):
        try:
            thing = s[uuid]
            return Thing(s, thing, uuid)
        except:
            raise Exception({
                "message": "Thing not found",
            })
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
    def save(self):
        self.dbh[self.uuid] = self.schema
    def delete(self):
        del self.dbh[self.uuid]
    def get_json(self):
        return json.dumps(self.schema)
