from wot.directory.config import Config
from logging import getLogger

from hashlib import sha256
import requests
from tinydb import Query

class DirectoryService:
    def __init__(self, db):
        self.db = db
        self.logger = getLogger(__name__)
    def new_source(self, uri):
        sources = self.db.table('sources')
        things = self.db.table('things')

        r = requests.get(uri)
        r.raise_for_status()
        sig = sha256(r.content).hexdigest()

        source = {
            'uri': uri,
            'sig': sig,
        }

        source_id = sources.insert(source)

        for thing in r.json():
            thing['source_id'] = source_id
            things.insert(thing)

        return source_id
    def delete_source(self, source_id):
        sources = self.db.table('sources')
        things = self.db.table('things')
        source_id = int(source_id)

        Thing = Query()
        things.remove(Thing.source_id == source_id)
        sources.remove(doc_ids=[source_id])
    def get_sources(self):
        sources = list()
        for source in self.db.table('sources').all():
            sources.append({
                'id': source.doc_id,
                'uri': source['uri'],
                'sig': source['sig'],
            })
        return sources
    def get_things(self):
        return self.db.table('things').all()
    def get_thing(self, thing_id):
        Thing = Query()

        thing = self.db.table('things').get(Thing.id == thing_id)

        if thing is None:
            raise IndexError('Thing not found')

        return thing
    def sync(self):
        sources = self.db.table('sources')
        things = self.db.table('things')

        updated = 0
        for source in sources.all():
            r = requests.get(source['uri'])
            try:
                r.raise_for_status()
            except requests.HTTPError:
                continue
            sig = sha256(r.content).hexdigest()

            if sig != source['sig']:
                Thing = Query()
                things.remove(Thing.source_id == source.doc_id)
                for thing in r.json():
                    thing['source_id'] = source.doc_id
                    things.insert(thing)
                updated = updated + 1
        return updated
