import shelve, json, uuid

class Thing:
    @staticmethod
    def get_by_uuid(uuid):
        s = shelve.open('things.db')
        try:
            thing = s[uuid]
            return Thing(uuid, thing)
        except:
            raise Exception({
                "message": "Thing not found",
            })
        finally:
            s.close()
    def __init__(self, schema = {}, uuid= uuid.uuid4().hex):
        self.schema = schema
        self.uuid = uuid
    def add_group(self, group):
        if 'groups' in self.schema:
            self.schema['groups'].append(group)
        else:
            self.schema.update({ "groups": [group]})
    def save(self):
        s = shelve.open('things.db')
        s[self.uuid] = self.schema
        s.close()
    def get_json(self):
        return json.dumps(self.schema)
