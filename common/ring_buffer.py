"""
This module contains a ring buffer class implementation
"""
from datetime import datetime, timedelta

class RingBuffer(object):
    """Ring buffer implementation that has an expiration time on elements"""

    def __init__(self, size=10, timeout=5):
        """Create a new instance of the buffer

        Arguments:
        size - Size of the buffer (default 10)
        timeout - How many minutes after which elements should expire (default 5)
        """
        self._buffer = list()
        self._timeout = timedelta(minutes=timeout)
        self.size = size

    def push(self, id, data, timestamp=datetime.now()):
        """Adds a new element to the end of the buffer

        Arguments:
        id - ID of the data to store
        data - The value of the data
        timestamp - When this value was inserted (default now)
        """

        if len(self._buffer) == self.size:
            self._buffer.pop(0)

        self.remove(id)
        self._buffer.append({
            'id': id,
            'data': data,
            'timestamp': timestamp
        })

    def _get(self, id):
        """Retrieves an element from the buffer

        Arguments:
        id - ID of the element to retireve

        Returns:
        The data element with that ID or None if not present (or expired)
        """

        for x in self._buffer:
            if x['id'] == id:
                if x['timestamp'] + self._timeout > datetime.now():
                    return x
                self._buffer.remove(x)
        return None

    def get(self, id):
        """Retrieve just the data from an element

        Arguments:
        id - ID of the element to retrieve

        Returns:
        The data attribute of the element with that ID or None if not present (or expired)
        """

        elem = self._get(id)
        if elem is not None:
            return self._get(id)['data']
        return None

    def contains(self, id):
        """Checks if an ID is in the buffer

        Arguments:
        id - ID to check

        Returns:
        True if the element is in the buffer and not expired
        """

        return self._get(id) != None

    def remove(self, id):
        """ Removes an element from the buffer

        Arguments:
        id - ID of the element to remove
        """

        elem = self._get(id)
        if elem is not None:
            self._buffer.remove(elem)

    def clear(self):
        """Clear the buffer"""
        self._buffer.clear()
