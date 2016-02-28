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

    def print_progress(self, noun, i, total):
        sys.stdout.write("\r%s / %s %s      " % (i, total, noun))
        sys.stdout.flush()

    def save_grid(self, grid, filename, polygons=None):
        self.facets = []
        print "Saving %s" % filename
        with open(filename, "w") as fh:
            fh.write(b" " * 80)
            # We'll update this later
            fh.write(struct.pack(b"<L", 0))
            self.num_written = 0
            # Main surface
            if polygons is not None:
                self.add_surface_polygons(fh, grid, polygons)
            else:
                self.add_surface_raw(fh, grid)
            # Edges
            self.add_edges(fh, grid)
            # Base
            self.add_base(fh, grid)
            # Update facet count
            fh.seek(80)
            fh.write(struct.pack(b"<L", self.num_written))

    def add_surface_raw(self, fh, grid):
        # Main surface
        for y in range(grid.height - 1):
            self.print_progress("rows", y, grid.height - 1)
            for x in range(grid.width - 1):
                self.add_square(fh, grid, x, y)

    def add_surface_polygons(self, fh, grid, polygons):
        # Write out polygons first
        in_polygons = set()
        for i, polygon in enumerate(polygons):
            self.print_progress("polygons", i, len(polygons))
            for x, y in polygon:
                in_polygons.add((x, y))
            self.add_polygon(fh, grid, polygon)
        print "done"
        # Main surface that isn't in polygons
        for y in range(grid.height - 1):
            self.print_progress("rows", y, grid.height - 1)
            for x in range(grid.width - 1):
                if (x, y) not in in_polygons:
                    self.add_square(fh, grid, x, y)
        print "done"

    def add_polygon(self, fh, grid, polygon):
        polygon = set(polygon)
        # Try to do contiguous rectangles of the polygon
        while polygon:
            x, y = sorted(polygon)[0]
            w, h = 1, 1
            # Grow rectangle until it hits a gap in the polygon
            xok = lambda: all((x + w, dy) in polygon for dy in range(y, y + h))
            yok = lambda: all((dx, y + h) in polygon for dx in range(x, x + w))
            while True:
                if xok():
                    w += 1
                else:
                    break
                if yok():
                    h += 1
                else:
                    break
            # Add that rectangle
            self.add_rectangle(fh, grid, x, y, w, h)
            # Remove those from the polygon
            for dx in range(x, x + w):
                for dy in range(y, y + h):
                    polygon.remove((dx, dy))

    def add_rectangle(self, fh, grid, x, y, w, h):
        # We build a tristrip
        even_points = []
        odd_points = []
        # Left edge
        for dy in range(y, y + h):
            even_points.append((x, dy))
        # Bottom edge
        for dx in range(x + 1, x + w):
            odd_points.append((dx, y))
        # Top edge
        for dx in range(x, x + w):
            even_points.append((dx, y + h))
        # Right edge
        for dy in range(y, y + h + 1):
            odd_points.append((x + w, dy))
        assert len(odd_points) == len(even_points)
        points = []
        for e, o in zip(even_points, odd_points):
            points.append(e)
            points.append(o)
        # Draw tristrip
        for i in range(len(points) - 2):
            if i % 2:
                self.add_grid_facet(fh, grid, *(points[i] + points[i + 2] + points[i + 1]))
            else:
                self.add_grid_facet(fh, grid, *(points[i] + points[i + 1] + points[i + 2]))

    def add_square(self, fh, grid, x, y):
        blh = grid[x, y]
        tlh = grid[x, y + 1]
        brh = grid[x + 1, y]
        trh = grid[x + 1, y + 1]
        minh = min(blh, tlh, brh, trh)
        assert minh > self.base_height, "Point below base: %s (%s, %s)" % (minh, x, y)
        # Put the seam in the best place
        if abs(blh - trh) > abs(brh - tlh):
            self.add_grid_facet(
                fh, grid,
                x, y,
                x + 1, y,
                x, y + 1,
            )
            self.add_grid_facet(
                fh, grid,
                x, y + 1,
                x + 1, y,
                x + 1, y + 1,
            )
        else:
            self.add_grid_facet(
                fh, grid,
                x, y,
                x + 1, y + 1,
                x, y + 1,
            )
            self.add_grid_facet(
                fh, grid,
                x, y,
                x + 1, y,
                x + 1, y + 1,
            )

    def add_edges(self, fh, grid):
        # Bottom edge
        y = 0
        for x in range(grid.width - 1):
            lh = grid[x, y]
            rh = grid[x + 1, y]
            self.add_facet(
                fh,
                x, y, self.base_height,
                x + 1, y, rh,
                x, y, lh,
            )
            self.add_facet(
                fh,
                x, y, self.base_height,
                x + 1, y, self.base_height,
                x + 1, y, rh,
            )
        # Top edge
        y = grid.height - 1
        for x in range(grid.width - 1):
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
        # Left edge
        x = 0
        for y in range(grid.height - 1):
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
        # Right edge
        x = grid.width - 1
        for y in range(grid.height - 1):
            bh = grid[x, y]
            th = grid[x, y + 1]
            self.add_facet(
                fh,
                x, y, self.base_height,
                x, y + 1, th,
                x, y, bh,
            )
            self.add_facet(
                fh,
                x, y, self.base_height,
                x, y + 1, self.base_height,
                x, y + 1, th,
            )

    def add_base(self, fh, grid):
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

    def add_grid_facet(self, fh, grid, x1, y1, x2, y2, x3, y3):
        self.add_facet(
            fh,
            x1, y1, grid[x1, y1],
            x2, y2, grid[x2, y2],
            x3, y3, grid[x3, y3],
        )

    def add_facet(self, fh, x1, y1, z1, x2, y2, z2, x3, y3, z3):
        # Calculate normal - clockwise vectors from solid face
        u = (x2 - x1, y2 - y1, z2 - z1)
        v = (x3 - x1, y3 - y1, z3 - z1)
        normal = (
            (u[1] * v[2]) - (u[2] * v[1]),
            (u[2] * v[0]) - (u[0] * v[2]),
            (u[0] * v[1]) - (u[1] * v[0]),
        )
        normal_magnitude = ((normal[0]**2) + (normal[1]**2) + (normal[2]**2)) ** 0.5
        normal = (
            normal[0] / normal_magnitude,
            normal[1] / normal_magnitude,
            normal[2] / normal_magnitude,
        )
        # Write out entry
        fh.write(
            struct.pack(
                b"<ffffffffffffH",
                normal[0], normal[1], normal[2],
                x1 * self.scale, y1 * self.scale, z1 * self.scale,
                x2 * self.scale, y2 * self.scale, z2 * self.scale,
                x3 * self.scale, y3 * self.scale, z3 * self.scale,
                0,
            )
        )
        self.num_written += 1
