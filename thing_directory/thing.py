import dbm, uuid

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
        if 'properties' in schema:
            self.properties = schema['properties']
            del schema['properties']
        else:
            self.properties = {}
        if 'events' in schema:
            self.events = schema['events']
            del schema['events']
        else:
            self.events = {}
        if 'actions' in schema:
            self.actions = schema['actions']
            del schema['actions']
        else:
            self.actions = {}
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
        self.schema['properties'] = self.properties
        self.schema['actions'] = self.actions
        self.schema['events'] = self.events
        self.dbh[self.uuid] = self.schema
    def delete(self):
        del self.dbh[self.uuid]
