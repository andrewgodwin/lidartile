from __future__ import unicode_literals

import array
import sys
from .stats import mean, pstdev, clip

class Grid(object):
    """
    Grid of points abstraction
    """

    def __init__(self, width, height, initial_value=0):
        self.width = int(width)
        self.height = int(height)
        self.data = array.array(b"f", (initial_value for i in xrange(self.width * self.height)))

    def __getitem__(self, key):
        if isinstance(key, (int, long)):
            return self.data[key]
        else:
            return self.data[key[0] + (key[1] * self.width)]

    def __setitem__(self, key, val):
        if isinstance(key, (int, long)):
            self.data[key] = val
        else:
            self.data[key[0] + (key[1] * self.width)] = val

    smooth_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def smooth(self, factor=1):
        """
        Tries to remove single jaggies
        """
        factor = float(factor)
        for x in range(self.width):
            for y in range(self.height):
                height = self[x, y]
                # Fetch surrounding heights
                others = []
                for offset in self.smooth_offsets:
                    dx, dy = x + offset[0], y + offset[1]
                    if 0 <= dx < self.width and 0 <= dy < self.height:
                        others.append(self[dx, dy])
                    else:
                        others.append(0)
                # Clip height to at most 1 stdev from the other heights
                m = mean(others)
                s = pstdev(others)
                limit = s * (1 / factor)
                self[x, y] = clip(height, m - limit, m + limit)

    def slice(self, ox, oy, w, h):
        """
        Returns a sub-grid
        """
        assert ox + w <= self.width
        assert oy + h <= self.height
        result = self.__class__(w, h)
        for y in range(h):
            idx = y * w
            ouridx = ox + ((oy+y) * self.width)
            result.data[idx:idx+w] = self.data[ouridx:ouridx+w]
        return result

    def snap(self, delta):
        """
        In-place value snapper
        """
        for i, value in enumerate(self.data):
            self.data[i] = round(value / delta) * delta

    def lower(self, delta):
        """
        Lowers every amount in the grid by the given amount, clipping to 0
        as the lowest value.
        """
        for i, value in enumerate(self.data):
            self.data[i] = max(value - delta, 0)

    def range(self):
        """
        Returns min, max tuple of height values in this grid
        """
        lowest = sys.maxint
        highest = 0
        for value in self.data:
            lowest = min(lowest, value)
            highest = max(highest, value)
        return lowest, highest
