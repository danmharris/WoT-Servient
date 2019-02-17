from proxy.app import create_app as create_proxy_app
from thing_directory.app import create_app as create_td_app
from binding.app import create_app as create_binding_app
import configparser
import sys
import jwt

def read_config():
    try:
        config = configparser.ConfigParser()
        config.read('/etc/wot-network.ini')
        return config
    except:
        print('No config file')
        sys.exit(1)

def read_bool(value):
    return True if value == 'yes' else False

def start_binding():
    config = read_config()
    bindings = config['binding']['enabled_plugins'].split(' ')
    app = create_binding_app({
        'BINDINGS': bindings,
        'HOSTNAME': config['binding']['hostname'],
        'AUTH': read_bool(config['binding']['require_auth']),
        'SECRET': config['binding']['secret'],
    })
    app.run(host='0.0.0.0', port=5000)

def start_proxy():
    config = read_config()
    app = create_proxy_app({
        'DB': config['proxy']['db'],
        'REDIS': config['proxy']['redis'],
        'AUTH': read_bool(config['proxy']['require_auth']),
        'SECRET': config['proxy']['secret'],
    })
    app.run(host='0.0.0.0', port=5001)

def start_thing_directory():
    config = read_config()
    app = create_td_app({
        'DB': config['thing_directory']['db'],
        'PROXY': config['thing_directory']['proxy'],
        'AUTH': read_bool(config['thing_directory']['require_auth']),
        'SECRET': config['thing_directory']['secret'],
    })
    app.run(host='0.0.0.0', port=5002)

def generate_api_token():
    config = read_config()
    secret = config['DEFAULT']['secret']
    description = input('Enter description for key: ')

    return jwt.encode({'description': description}, secret, algorithm='HS256')
