from __future__ import unicode_literals

import sys
import argparse
from .ingestor import AscIngestor
from .optimiser import GridOptimiser
from .stlwriter import StlWriter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--divisor", type=int, default=1)
    parser.add_argument("-f", "--featuresize", type=float, default=0.3)
    parser.add_argument("-b", "--base", type=float, default=10)
    parser.add_argument("-c", "--clip", type=float, default=5)
    parser.add_argument("-z", "--zboost", type=float, default=1)
    parser.add_argument("-s", "--snap", type=float, default=0)
    parser.add_argument("-e", "--snapexp", type=float, default=0)
    parser.add_argument("-m", "--smoothing", type=float, default=1)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    ingestor = AscIngestor(args.files, divisor=args.divisor, clip=-args.clip, zboost=args.zboost, snap=args.snap, snapexp=args.snapexp)
    ingestor.load()
    print "Smoothing..."
    ingestor.grid.smooth(factor=args.smoothing)
    if args.featuresize:
        optimiser = GridOptimiser(ingestor.grid, delta=args.featuresize)
        print "Optimising..."
        polygons = optimiser.optimise()
        print "%s polygons found" % len(polygons)
    else:
        polygons = None
    writer = StlWriter(base_height=-args.base, scale=0.3)
    writer.save_grid(ingestor.grid, "output.stl", polygons=polygons)


if __name__ == "__main__":
    main()
