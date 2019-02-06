from datetime import datetime, timedelta

class RingBuffer:
    def __init__(self, size=10, timeout=5):
        self._buffer = list()
        self._timeout = timedelta(minutes=timeout)
        self.size = size
    def push(self, id, data, timestamp=datetime.now()):
        if len(self._buffer) == self.size:
            self._buffer.pop(0)

        self.remove(id)
        self._buffer.append({
            'id': id,
            'data': data,
            'timestamp': timestamp
        })

    def _get(self, id):
        for x in self._buffer:
            if x['id'] == id:
                if x['timestamp'] + self._timeout > datetime.now():
                    return x
                else:
                    self._buffer.remove(x)
        return None

    def get(self, id):
        elem = self._get(id)
        if elem is not None:
            return self._get(id)['data']
        else:
            return None

    def contains(self, id):
        return self._get(id) != None

    def remove(self, id):
        elem = self._get(id)
        if elem is not None:
            self._buffer.remove(elem)

    def clear(self):
        self._buffer.clear()
