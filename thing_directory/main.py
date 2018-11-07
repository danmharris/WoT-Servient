from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()
db = client.thing_directory
things = db.things


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/things/register', methods=['POST'])
def register():
    # Needs to validate input
    data = request.get_json()
    _id = things.insert(data)
    return str(_id)
