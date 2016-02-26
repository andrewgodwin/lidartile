from __future__ import unicode_literals

import sys
import argparse
from .ingestor import AscIngestor
from .stlwriter import StlWriter


def main():
    ingestor = AscIngestor(sys.argv[1:], divisor=2)
    ingestor.load()
    writer = StlWriter(base_height=-14, scale=0.3)
    writer.save_grid(ingestor.grid, "test.stl")


if __name__ == "__main__":
    main()
