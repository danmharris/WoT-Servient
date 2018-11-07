from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()
db = client.thing_directory
things = db.things


@app.route('/')
def hello_world():
    return 'Hello World!'
