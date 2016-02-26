from __future__ import unicode_literals

import sys
import struct


class StlWriter(object):
    """
    Writes a data grid out as .stl
    """

    def __init__(self, base_height=-1, scale=1):
        self.base_height = base_height
        self.scale = scale

    def save_grid(self, grid, filename):
        self.facets = []
        print "Saving %s" % filename
        with open(filename, "w") as fh:
            fh.write(b" " * 80)
            # We'll update this later
            fh.write(struct.pack(b"<L", 0))
            self.num_written = 0
            # Main surface
            for y in range(grid.height - 1):
                for x in range(grid.width - 1):
                    blh = grid[x, y]
                    tlh = grid[x, y + 1]
                    brh = grid[x + 1, y]
                    trh = grid[x + 1, y + 1]
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
            for x in range(grid.width - 1):
                for y in [0, grid.height - 1]:
                    lh = grid[x, y]
                    rh = grid[x + 1, y]
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
            for y in range(grid.height - 1):
                for x in [0, grid.width - 1]:
                    bh = grid[x, y]
                    th = grid[x, y + 1]
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
                0, grid.height - 1, self.base_height,
                grid.width - 1, grid.height - 1, self.base_height,
            )
            self.add_facet(
                fh,
                0, 0, self.base_height,
                grid.width - 1, grid.height - 1, self.base_height,
                grid.width - 1, 0, self.base_height,
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
