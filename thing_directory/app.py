from flask import Flask, request
import shelve, json, uuid
from thing import Thing

app = Flask(__name__)

@app.route('/things', methods=['GET'])
def get_all():
    s = shelve.open('things.db')
    ids = list(s.keys())
    s.close()
    response = {
        "ids": ids
    }
    return json.dumps(response)

@app.route('/things/<uuid>', methods=['GET'])
def get_by_id(uuid):
    try:
        db_thing = Thing.get_by_uuid(uuid=uuid)
        return db_thing.get_json()
    except Exception as err:
        return (json.dumps(err.message), 404, None)

@app.route('/things/register', methods=['POST'])
def register():
    # Needs to validate input
    new_thing = Thing(request.get_json())
    new_thing.save()
    response = {
        "id": new_thing.uuid
    }
    return (json.dumps(response), 201, None)

@app.route('/things/<uuid>/groups', methods=['POST'])
def add_group(uuid):
    body = request.get_json()
    try:
        db_thing = Thing.get_by_uuid(uuid=uuid)
    except Exception as err:
        return (json.dumps(err.message), 404, None)
    db_thing.add_group(body['group'])
    db_thing.save()
    response = {
        "message": "updated"
    }
    return (json.dumps(response), 200, None)
