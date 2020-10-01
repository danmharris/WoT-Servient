from wot.grouper.config import Config
from logging import getLogger

import requests
from tinydb import Query

class ThingService:
    def __init__(self, db):
        self.db = db
        self.logger = getLogger(__name__)
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
        td['base'] = Config.get('base') + '/things/{}'.format(td['title'])

        for action in td['actions'].keys():
            td['actions'][action]['forms'] = [{
                'href': '/{}'.format(action),
                'htv:methodName': 'POST',
                'op': 'invokeaction',
            }]

        self.db.insert(td)
    def get_thing(self, name):
        Thing = Query()
        thing = self.db.get(Thing.title == name)

        if thing is None:
            raise IndexError('Thing does not exist')
        return thing
    def get_things(self):
        return self.db.all()
    def delete_thing(self, name):
        Thing = Query()
        if not self.db.contains(Thing.title == name):
            raise IndexError('Thing does not exist')
        self.db.remove(Thing.title == name)
    def invoke_action(self, name, action):
        thing = self.get_thing(name)

        if action not in thing['actions']:
            raise IndexError('Action name does not exist')

        failed = 0
        for e in thing['actions'][action]['exec']:
            td = requests.get(e['thing_description']).json()

            base = td['base'] if 'base' in td else ''
            interactions = {**td['actions'], **td['properties']}
            href = None

            for (iname, i) in interactions.items():
                if iname != e['interaction']:
                    continue
                for f in i['forms']:
                    if f['op'] != e['op']:
                        continue

                    method = f['htv:methodName']
                    href = f['href']

            if href is None:
                raise IndexError('Cannot find matching interaction')

            if method == 'PUT':
                url = base + href
                r = requests.put(url, json=e['data'])
                try:
                    r.raise_for_status()
                except:
                    self.logger.error('Request to %s failed with status %i', url, r.status_code)
                    self.logger.error('Response: %s', r.text)
                    failed = failed + 1
            else:
                failed = failed + 1

        if failed > 0:
            raise RuntimeError('One or more requests failed')
