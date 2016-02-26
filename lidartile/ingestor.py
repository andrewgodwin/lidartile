from __future__ import unicode_literals

import sys
import array
from .grid import Grid

POSINF = sys.maxint
NEGINF = None

class AscIngestor(object):
    """
    Loads .asc files into memory.

    Uses a 2D array to store information; it's not great at sparse datasets
    for that reason.

    Array is laid out in rows, e.g. [row1a, row1b, row1c, row2a, row2b...]
    """

    nodata_height = 0

    def __init__(self, files, divisor):
        assert files, "No files!"
        self.files = files
        self.divisor = divisor
        self.cellsize = None
        self.left = None
        self.bottom = None
        self.top = None
        self.right = None

    def load(self):
        # Scan each file to find the borders
        self.left, self.bottom, self.right, self.top, self.cellsize = self.find_limits()
        # Build array
        array_width = (self.right - self.left) / (self.cellsize * float(self.divisor))
        array_height = (self.top - self.bottom) / (self.cellsize * float(self.divisor))
        if int(array_height) != array_height or int(array_width) != array_width:
            raise ValueError("Non-exact divisor!")
        print "Bounds: (%s, %s) to (%s, %s) cellsize %s divisor %s" % (self.left, self.bottom, self.right, self.top, self.cellsize, self.divisor)
        print "Creating array of size %.1f MB" % (array_width * array_height * (4/(1024.0**2)))
        self.grid = Grid(array_width, array_height, self.nodata_height)
        # Load files
        for file in self.files:
            print "Loading %s" % file
            self.load_file(file)

    def array_index(self, x, y, floor=False):
        """
        Returns an index into the array given absolute x and y values
        """
        dx = x - self.left
        dy = y - self.bottom
        step = self.cellsize * self.divisor
        if ((dx < 0) or (dx % step) or (dy < 0) or (dy % step)) and not floor:
            raise ValueError("Tried to find array index of impossible coords %s, %s" % (x, y))
        return (dx // step) + ((dy // step) * self.grid.width)

    def find_limits(self):
        minx, maxx = POSINF, NEGINF
        miny, maxy = POSINF, NEGINF
        cellsize = None
        for filename in self.files:
            data = {}
            # Read file header
            with open(filename, "r") as fh:
                for line in fh:
                    bits = line.strip().split()
                    data[bits[0]] = int(bits[1])
                    if len(data) > 4:
                        break
            # Check cellsize
            if cellsize is None:
                cellsize = data['cellsize']
            elif data['cellsize'] != cellsize:
                raise ValueError("Mismatching cellsize: %s != %s" % (cellsize, data['cellsize']))
            # Work out limits
            xl = data['xllcorner']
            yl = data['yllcorner']
            xh = xl + (cellsize * data['ncols'])
            yh = yl + (cellsize * data['nrows'])
            minx = min(minx, xl)
            maxx = max(maxx, xh)
            miny = min(miny, yl)
            maxy = max(maxy, yh)
        return minx, miny, maxx, maxy, cellsize

    def load_file(self, filename):
        with open(filename, "r") as fh:
            meta = {}
            row = 0
            prevpoints = {}
            for line in fh:
                bits = line.strip().split()
                # Meta info reading?
                if len(bits) == 2:
                    meta[bits[0]] = int(bits[1])
                # Main info reading
                else:
                    for j, bit in enumerate(bits):
                        idx = self.array_index(
                            meta['xllcorner'] + (j * meta['cellsize']),
                            meta['yllcorner'] + ((meta['nrows'] - (row + 1)) * meta['cellsize']),
                            floor=True,
                        )
                        bit = float(bit)
                        if bit == meta['NODATA_value']:
                            bit = self.nodata_height
                        # Cluster into the right divisor sections
                        prevpoints.setdefault(idx, []).append(bit)
                        if ((j + 1) % self.divisor == 0) and ((row + 1) % self.divisor == 0):
                            # Last point in this cluster, write it out
                            assert len(prevpoints[idx]) == self.divisor ** 2, "Wrong size cluster %s" % prevpoints[idx]
                            value = self.coalesce(prevpoints[idx])
                            self.grid[idx] = value
                            del prevpoints[idx]
                    row += 1

    def coalesce(self, values):
        return (sum(values) / float(len(values))) / float(self.divisor)
