"""Module for Thing representation"""
from uuid import uuid4
from wot.common.exception import APIException

class Thing:
    """Class that represents a Thing in the directory"""
    @staticmethod
    def get_by_uuid(s, uuid):
        """Retrieves a thing by a UUID from the database

        Takes 1 argument:
        uuid - UUID of device to retrieve
        """
        try:
            thing = s[uuid]
            return Thing(s, thing, uuid)
        except:
            raise APIException('Thing not found', 404)
    def __init__(self, dbh, schema=None, uuid=None):
        """Creates new thing instance with required parameters

        Takes 3 arguments:
        dbh - Database handler
        schema - Thing description
        uuid - UUID of the device (defaults to random)
        """
        self.dbh = dbh
        self.schema = schema if schema is not None else {}
        self.uuid = uuid if uuid is not None else uuid4().hex
    def add_group(self, group):
        """Adds a thing to a group

        Takes 1 argument:
        group - name of group to add
        """
        if 'groups' in self.schema:
            self.schema['groups'].append(group)
        else:
            self.schema.update({"groups": [group]})
    def get_groups(self):
        """Gets the groups this thing is apart of"""
        if 'groups' in self.schema:
            return self.schema['groups']
        return []
    def del_group(self, group):
        """Deletes a group from the thing

        Takes 1 argument:
        group - Group name to remove
        """
        if 'groups' in self.schema:
            self.schema['groups'] = [g for g in self.schema['groups'] if g != group]
    def save(self):
        """Saves the thing in the database"""
        self.dbh[self.uuid] = self.schema
    def delete(self):
        """Deletes the thing from the database"""
        del self.dbh[self.uuid]
