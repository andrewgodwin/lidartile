LidarTile
---------

Little program to convert LIDAR scans into 3D-printable .STL tiles. Accepts
ESRI ASCII grid formats only, right now.

Run it like this::

    python -m lidartile.cli -d 4 -f 0.5 -b 5 -c 2 -z 1.5 -s 3 -m 2 ~/Downloads/LIDAR-DSM-1M-TQ37/tq3979_DSM_1m.asc

Options are:

* ``-d``: Divisor - how many points to combine into one height value for model simplicity
  (size of the square, so ``4`` would be 16 input points per output)

* ``-f``: Feature optimise limit - Combines polygons within this delta into one.

* ``-b``: Base depth from the zero line

* ``-c``: Negative clip to prevent holes penetrating the base

* ``-z``: Z multiplier, for enhancing features

* ``-s``: Snap value, rounds heights to multiples of this for flatter surfaces

* ``-m``: Smoothing factor. Higher is more smooth.
