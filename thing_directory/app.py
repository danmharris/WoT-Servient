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
    s = shelve.open('things.db')
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        response = db_thing.get_json()
    except Exception as err:
        response = (str(err), 404, None)
    finally:
        s.close()
        return response

@app.route('/things/query', methods=['GET'])
def query():
    req_groups = request.args.get('groups').split(',')
    s = shelve.open('things.db')
    uuids = list(s.keys())
    matching = []
    for id in uuids:
        try:
            thing = Thing.get_by_uuid(s, id)
            groups = thing.get_groups()
            if len(set(groups).intersection(req_groups)) > 0:
                matching.append(thing.schema)
        except Exception:
            continue
    s.close()
    return json.dumps(matching)

@app.route('/things/register', methods=['POST'])
def register():
    # Needs to validate input
    s = shelve.open('things.db')
    new_thing = Thing(s, request.get_json())
    new_thing.save()
    response = {
        "id": new_thing.uuid
    }
    s.close()
    return (json.dumps(response), 201, None)

@app.route('/things/<uuid>/groups', methods=['POST'])
def add_group(uuid):
    body = request.get_json()
    s = shelve.open('things.db')
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
    except Exception as err:
        s.close()
        return (str(err), 404, None)
    db_thing.add_group(body['group'])
    db_thing.save()
    response = {
        "message": "updated"
    }
    s.close()
    return (json.dumps(response), 200, None)

@app.route('/things/<uuid>', methods=['DELETE'])
def delete_thing(uuid):
    s = shelve.open('things.db')
    try:
        db_thing = Thing.get_by_uuid(s, uuid=uuid)
        db_thing.delete()
        response = (json.dumps({"message": "deleted"}), 200, None)
    except Exception as err:
        response = (str(err), 404, None)
    finally:
        s.close()
        return response
