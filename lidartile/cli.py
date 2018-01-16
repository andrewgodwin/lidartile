from __future__ import unicode_literals

import sys
import argparse
from .ingestor import AscIngestor
from .optimiser import GridOptimiser
from .stlwriter import StlWriter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--divisor", type=int, default=1)
    parser.add_argument("-f", "--featuresize", type=float, default=0)
    parser.add_argument("-b", "--base", type=float, default=10)
    parser.add_argument("-c", "--clip", type=float, default=5)
    parser.add_argument("-z", "--zboost", type=float, default=1)
    parser.add_argument("-s", "--snap", type=float, default=0)
    parser.add_argument("-m", "--smoothing", type=float, default=0)
    parser.add_argument("-l", "--scale", type=float, default=0.3)
    parser.add_argument("-o", "--output", default="output.stl")
    parser.add_argument("-ix", "--slicex", type=int, default=0)
    parser.add_argument("-iy", "--slicey", type=int, default=0)
    parser.add_argument("-iw", "--slicewidth", type=int, default=0)
    parser.add_argument("-ih", "--sliceheight", type=int, default=0)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    ingestor = AscIngestor(args.files, divisor=args.divisor, zboost=args.zboost)
    ingestor.load()
    if args.slicewidth and args.sliceheight:
        ingestor.grid = ingestor.grid.slice(args.slicex, args.slicey, args.slicewidth, args.sliceheight)
    grid = ingestor.grid
    if args.clip:
        print "Clipping..."
        grid.lower(args.clip)
    if args.smoothing:
        print "Smoothing..."
        grid.smooth(factor=args.smoothing)
    if args.snap:
        print "Snapping..."
        grid.snap(args.snap)
    if args.featuresize:
        optimiser = GridOptimiser(ingestor.grid, delta=args.featuresize)
        print "Optimising..."
        polygons = optimiser.optimise()
        print "%s polygons found" % len(polygons)
    else:
        polygons = None
    lowest, highest = grid.range()
    print "Grid ranges from %s to %s" % (lowest, highest)
    writer = StlWriter(base_height=-args.base, scale=args.scale)
    writer.save_grid(ingestor.grid, args.output, polygons=polygons)
    print ""


if __name__ == "__main__":
    main()
