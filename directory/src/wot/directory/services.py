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
        r = requests.get(uri)
        r.raise_for_status()
        sig = sha256(r.content).hexdigest()

        source = {
            'uri': uri,
            'sig': sig,
            'data': r.json(),
        }

        return self.db.insert(source)
    def get_sources(self):
        sources = list()
        for source in self.db.all():
            sources.append({
                'id': source.doc_id,
                'uri': source['uri'],
                'sig': source['sig'],
            })
        return sources
    def get_things(self):
        things = list()
        for source in self.db.all():
            things = things + source['data']
        return things
    def sync(self):
        updated = 0
        for source in self.db.all():
            r = requests.get(source['uri'])
            try:
                r.raise_for_status()
            except requests.HTTPError:
                continue
            sig = sha256(r.content).hexdigest()

            if sig != source['sig']:
                self.db.update({
                    'sig': sig,
                    'data': r.json()
                    }, doc_ids=[source.doc_id])
                updated = updated + 1
        return updated

