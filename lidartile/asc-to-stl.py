from __future__ import unicode_literals

import sys
import array
import struct

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
        self.files = files
        self.divisor = divisor
        self.cellsize = None
        self.left = None
        self.bottom = None
        self.top = None
        self.right = None
        self.array_height = None
        self.array_width = None

    def load(self):
        # Scan each file to find the borders
        self.left, self.bottom, self.right, self.top, self.cellsize = self.find_limits()
        # Build array
        self.array_width = (self.right - self.left) / (self.cellsize * float(self.divisor))
        self.array_height = (self.top - self.bottom) / (self.cellsize * float(self.divisor))
        if int(self.array_height) != self.array_height or int(self.array_width) != self.array_width:
            raise ValueError("Non-exact divisor!")
        self.array_width = int(self.array_width)
        self.array_height = int(self.array_height)
        print "Bounds: (%s, %s) to (%s, %s) cellsize %s divisor %s" % (self.left, self.bottom, self.right, self.top, self.cellsize, self.divisor)
        print "Creating array of size %.1f MB" % (self.array_width * self.array_height * (4/(1024.0**2)))
        self.data = array.array(b"f", (self.nodata_height for i in xrange(self.array_width * self.array_height)))
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
        return (dx // step) + ((dy // step) * self.array_width)

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
                            self.data[idx] = value
                            del prevpoints[idx]
                    row += 1

    def coalesce(self, values):
        return (sum(values) / float(len(values))) / float(self.divisor)


class 


class GridOptimiser(object):
    """
    Takes a grid of points and simplifies it into a set of polygons, each
    representing an approximate contour.

    Not terribly efficient.
    """

    def __init__(self, data, width, height):
        self.data = data
        self.width = width
        self.height = height

    def 

    def optimise(self):
        seen = set()
        for 


class StlWriter(object):
    """
    Writes a data grid out as .stl
    """

    def __init__(self, ingestor, base_height=-1, scale=1):
        self.ingestor = ingestor
        self.base_height = base_height
        self.scale = scale

    def save(self, filename):
        self.facets = []
        print "Saving %s" % filename
        with open(filename, "w") as fh:
            fh.write(b" " * 80)
            # We'll update this later
            fh.write(struct.pack(b"<L", 0))
            self.num_written = 0
            # Main surface
            for y in range(ingestor.array_height - 1):
                for x in range(ingestor.array_width - 1):
                    idx = x + (y * ingestor.array_width)
                    blh = ingestor.data[idx]
                    tlh = ingestor.data[idx + ingestor.array_width]
                    brh = ingestor.data[idx + 1]
                    trh = ingestor.data[idx + 1 + ingestor.array_width]
                    assert blh > self.base_height, "Point below base: %s (%s, %s)" % (blh, x, y)
                    assert tlh > self.base_height, "Point below base: %s (%s, %s)" % (tlh, x, y+1)
                    assert brh > self.base_height, "Point below base: %s (%s, %s)" % (brh, x+1, y)
                    assert trh > self.base_height, "Point below base: %s (%s, %s)" % (trh, x+1, y+1)
                    self.add_facet(
                        fh,
                        x, y, blh,
                        x, y + 1, tlh,
                        x + 1, y + 1, trh,
                    )
                    self.add_facet(
                        fh,
                        x, y, blh,
                        x + 1, y + 1, trh,
                        x + 1, y, brh,
                    )
            # Edges
            for x in range(ingestor.array_width - 1):
                for y in [0, ingestor.array_height - 1]:
                    idx = x + (y * ingestor.array_width)
                    lh = ingestor.data[idx]
                    rh = ingestor.data[idx + 1]
                    self.add_facet(
                        fh,
                        x, y, self.base_height,
                        x, y, lh,
                        x + 1, y, rh,
                    )
                    self.add_facet(
                        fh,
                        x, y, self.base_height,
                        x + 1, y, rh,
                        x + 1, y, self.base_height,
                    )
            for y in range(ingestor.array_height - 1):
                for x in [0, ingestor.array_width - 1]:
                    idx = x + (y * ingestor.array_width)
                    bh = ingestor.data[idx]
                    th = ingestor.data[idx + ingestor.array_width]
                    self.add_facet(
                        fh,
                        x, y, self.base_height,
                        x, y, bh,
                        x, y + 1, th,
                    )
                    self.add_facet(
                        fh,
                        x, y, self.base_height,
                        x, y + 1, th,
                        x, y + 1, self.base_height,
                    )
            # Base
            self.add_facet(
                fh,
                0, 0, self.base_height,
                0, ingestor.array_height - 1, self.base_height,
                ingestor.array_width - 1, ingestor.array_height - 1, self.base_height,
            )
            self.add_facet(
                fh,
                0, 0, self.base_height,
                ingestor.array_width - 1, ingestor.array_height - 1, self.base_height,
                ingestor.array_width - 1, 0, self.base_height,
            )
            # Update facet count
            fh.seek(80)
            fh.write(struct.pack(b"<L", self.num_written))


    def add_facet(self, fh, x1, y1, z1, x2, y2, z2, x3, y3, z3):
        fh.write(
            struct.pack(
                b"<ffffffffffffH",
                0, 0, 0,
                x1 * self.scale, y1 * self.scale, z1 * self.scale,
                x2 * self.scale, y2 * self.scale, z2 * self.scale,
                x3 * self.scale, y3 * self.scale, z3 * self.scale,
                0,
            )
        )
        self.num_written += 1


if __name__ == "__main__":
    ingestor = AscIngestor(sys.argv[1:], 2)
    ingestor.load()
    writer = StlWriter(ingestor, base_height=-14, scale=0.3)
    writer.save("test.stl")
