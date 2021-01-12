import os, socket
from yaml import safe_load

class Config:
    __default = {
        'plugins': [],
        'base': 'http://' + socket.gethostname(),
    }
    __custom = dict()

    @classmethod
    def load(cls):
        config_path = os.environ.get('CONFIG_PATH', 'adapter.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as stream:
                cls.__custom = safe_load(stream)

        # Environment variable overrides
        if 'ADAPTER_PLUGINS' in os.environ:
            cls.__custom['plugins'] = os.environ['ADAPTER_PLUGINS'].split(',')
        if 'ADAPTER_BASE_URI' in os.environ:
            cls.__custom['base'] = os.environ['ADAPTER_BASE_URI']

    @classmethod
    def get(cls, key):
        return cls.__custom[key] if key in cls.__custom else cls.__default[key]
