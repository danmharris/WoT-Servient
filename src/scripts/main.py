"""Entry scripts for all APIs in this project"""
import configparser
import sys
from proxy.app import create_app as create_proxy_app
from thing_directory.app import create_app as create_td_app
from binding.app import create_app as create_binding_app
from coap_thing.app import main as create_coap_thing

def read_config(path='/etc/wot-network.ini'):
    """Reads and parses a configuration file

    Takes 1 argument
    path - Path to configuration file (defaults to /etc/wot-network.ini)
    """
    try:
        config = configparser.ConfigParser()
        config.read(path)
        return config
    except:
        print('No config file')
        sys.exit(1)

def read_bool(value):
    """Converts string to boolean"""
    return value == 'yes'

def start_binding():
    """Starts the Binding API"""
    config = read_config()
    bindings = config['binding']['enabled_plugins'].split(' ')
    app = create_binding_app({
        'BINDINGS': bindings,
        'HOSTNAME': config['binding']['hostname'],
        'AUTH': read_bool(config['binding']['require_auth']),
        'SECRET': config['binding']['secret'],
        'IKEA': config['IKEA'],
    })
    app.run(host='0.0.0.0', port=5000)

def start_proxy():
    """Starts the Proxy API"""
    config = read_config()
    app = create_proxy_app({
        'DB': config['proxy']['db'],
        'REDIS': config['proxy']['redis'],
        'AUTH': read_bool(config['proxy']['require_auth']),
        'SECRET': config['proxy']['secret'],
    })
    app.run(host='0.0.0.0', port=5001)

def start_thing_directory():
    """Starts the thing directory API"""
    config = read_config()
    app = create_td_app({
        'DB': config['thing_directory']['db'],
        'PROXY': config['thing_directory']['proxy'],
        'AUTH': read_bool(config['thing_directory']['require_auth']),
        'SECRET': config['thing_directory']['secret'],
    })
    app.run(host='0.0.0.0', port=5002)

def start_coap_thing():
    """Starts the example CoAP device"""
    create_coap_thing()
