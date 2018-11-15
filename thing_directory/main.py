from flask import Flask, request
import shelve, json, uuid

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

@app.route('/things/register', methods=['POST'])
def register():
    # Needs to validate input
    s = shelve.open('things.db')
    data_json = request.get_json()
    new_uuid = uuid.uuid4().hex
    s[new_uuid] = data_json
    s.close()
    response = {
        "id": new_uuid
    }
    return (json.dumps(response), 201, None)
