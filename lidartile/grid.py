from __future__ import unicode_literals

import array


class Grid(object):
    """
    Grid of points abstraction
    """

    def __init__(self, width, height, initial_value=0):
        self.width = int(width)
        self.height = int(height)
        self.data = array.array(b"f", (initial_value for i in xrange(self.width * self.height)))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        else:
            return self.data[key[0] + (key[1] * self.width)]

    def __setitem__(self, key, val):
        if isinstance(key, int):
            self.data[key] = val
        else:
            self.data[key[0] + (key[1] * self.width)] = val
