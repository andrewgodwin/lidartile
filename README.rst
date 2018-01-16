LidarTile
=========

Little program to convert LIDAR scans into 3D-printable .STL tiles. Accepts
ESRI ASCII grid formats only, right now.

Run it like this::

    python -m lidartile.cli -d 4 -f 0.5 -b 5 -c 2 -z 1.5 -s 3 -m 2 ~/Downloads/LIDAR-DSM-1M-TQ37/tq3979_DSM_1m.asc

You can pass as many .asc files as you like on the commandline and it'll merge
them all into one tile. Make sure they're adjacent, though, or it'll fill in
the gaps with empty 0-height space and you'll have a huge file!

Options are:

* ``-d``: Divisor - how many points to combine into one height value for model simplicity
  (size of the square, so ``4`` would be 16 input points per output)

* ``-f``: Feature optimise limit - Combines polygons within this delta into one.

* ``-b``: Base depth from the zero line

* ``-c``: Negative clip to prevent holes penetrating the base

* ``-z``: Z multiplier, for enhancing features

* ``-s``: Snap value, rounds heights to multiples of this for flatter surfaces

* ``-m``: Smoothing factor. Higher is more smooth.

* ``-l``: Scale. Use numbers less than 1 to scale down, e.g. 0.5 is half scale.

* ``-ix,iy,iw,ih``: Sub-grid, use to cut out a certain piece from the input map. ``x,y`` define lower-left corner and ``w,h`` the width and height of the cut-out.


Commandline Examples
--------------------

My London tiles are built somewhat like this, from the Environment Agency 1m DSM set::

    python -m lidartile.cli -d 2 -b 5 -c 10 -z 1.5 -m 2 -l 0.075 ~/Downloads/LIDAR-DSM-1M-TQ48/tq4081_DSM_1m.asc

An example of what they look like:

.. image:: https://pbs.twimg.com/media/CcSWm2jUMAAkoNl.jpg
    :target: https://twitter.com/andrewgodwin/status/703853037018722304/photo/1
