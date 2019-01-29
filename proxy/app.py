from flask import Flask

app = Flask(__name__)
app.config['DB'] = 'endpoints.db'

@app.route('/')
def hello_world():
    return "Hello world!"
