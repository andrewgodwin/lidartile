from __future__ import unicode_literals

import sys
import collections


class GridOptimiser(object):
    """
    Takes a Grid and returns a set of polygons, optimising points of similar
    height into contours
    """

    def __init__(self, grid, delta=0.1):
        self.grid = grid
        self.delta = delta

    def print_progress(self, noun, i, total):
        sys.stdout.write("\r%s / %s %s      " % (i, total, noun))
        sys.stdout.flush()

    def group(self, height):
        return int(height / self.delta)

    def optimise(self):
        # First, collect all tiles which are relatively "flat"
        flat_tiles = {}
        for x in range(self.grid.width - 1):
            self.print_progress("flat tile cols", x, self.grid.width)
            for y in range(self.grid.height - 1):
                bl = self.group(self.grid[x, y])
                tl = self.group(self.grid[x, y + 1])
                tr = self.group(self.grid[x + 1, y + 1])
                br = self.group(self.grid[x + 1, y])
                if bl == tl == tr == br:
                    flat_tiles[x, y] = br
        print "done"
        # Now, collect all neighbouring flat tiles into polygon sets
        polygons = []
        done = 0
        while flat_tiles:
            self.print_progress("polygons", done, "???")
            polygons.append(self.create_polygon(flat_tiles))
            done += 1
        print "done"
        return polygons

    def create_polygon(self, flat_tiles):
        # Pick a random remaining flat tile
        (x, y), height = list(flat_tiles.items())[0]
        queue = collections.deque([(x, y)])
        polygon = []
        while queue:
            tx, ty = queue.popleft()
            # Add this tile to the polygon
            del flat_tiles[tx, ty]
            polygon.append((tx, ty))
            # See if any of its neighbours count
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nx = tx + dx
                ny = ty + dy
                if (nx, ny) in flat_tiles and flat_tiles[nx, ny] == height and (nx, ny) not in queue:
                    queue.append((nx, ny))
        return polygon
