import shelve, json, uuid

class Thing:
    @staticmethod
    def get_by_uuid(uuid):
        s = shelve.open('things.db')
        try:
            thing = s[uuid]
            return Thing(thing)
        except:
            raise Exception({
                "message": "Thing not found",
            })
        finally:
            s.close()
    def __init__(self, schema = {}):
        self.schema = schema
    def save(self):
        s = shelve.open('things.db')
        new_uuid = uuid.uuid4().hex
        s[new_uuid] = self.schema
        s.close()
        self.uuid = new_uuid
        return new_uuid
    def get_json(self):
        return json.dumps(self.schema)
