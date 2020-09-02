from tinydb import Query

class ThingService:
    def __init__(self, db):
        self.db = db
    def new_thing(self, td):
        if 'title' not in td:
            raise ValueError('Title is a required parameter')
        if 'actions' not in td:
            raise ValueError('Virtual thing must have at least one action')

        Thing = Query()
        if self.db.contains(Thing.title == td['title']):
            raise IndexError('Thing already exists (title must be unique)')

        if 'id' not in td:
            td['id'] = "urn:wot:virtual:{}".format(td['title'])

        self.db.insert(td)
    def get_thing(self, name):
        Thing = Query()
        thing = self.db.get(Thing.title == name)

        if thing is None:
            raise IndexError('Thing does not exist')
        return thing
    def get_things(self):
        return self.db.all()
