from datetime import datetime, timedelta

_buffer = list()
_size = 10
_timeout = timedelta(minutes=5)

def set_size(size):
    _size = size

def push(id, data):
    if len(_buffer) == _size:
        _buffer.pop(0)

    remove(id)
    _buffer.append({
        'id': id,
        'data': data,
        'timestamp': datetime.now()
    })

def _get(id):
    for x in _buffer:
        if x['id'] == id:
            if x['timestamp'] + _timeout > datetime.now():
                return x
            else:
                _buffer.remove(x)
    return None

def get(id):
    return _get(id)['data']

def contains(id):
    return _get(id) != None

def remove(id):
    elem = _get(id)
    if elem is not None:
        _buffer.remove(elem)

def clear():
    _buffer.clear()
