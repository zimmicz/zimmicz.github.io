Title: WMS Download For Future Offline Use
Date: 2015-03-15 18:10
Tags: ogc, python, wms
Category: automation

Using WMS in real time might easily become pain in the ass due to low connection speed or slow server response. Downloading images beforehand seems to be a reasonable choice both to avoid any slowdowns and to improve user experience when working with WMS layers.

[OWSLib](https://geopython.github.io/OWSLib/) is a great tool to help you get images from WMS server. Code and some comments follow.

    import math
    import os
    import random
    import time
    from owslib.wms import WebMapService

    BOTTOM_LEFT = (-679363,-1120688)
    TOP_RIGHT   = (-565171,-1042703)
    SRS_WIDTH   = math.fabs(-639084 - -638825) # tile width in units of crs => 259 m
    SRS_HEIGHT  = math.fabs(-1070426 - -1070273) # tile height in units of crs => 153 m
    PX_WIDTH    = 977
    PX_HEIGHT   = 578

    FORMAT      = 'image/png'
    LAYERS      = ['KN', 'RST_PK']
    SIZE        = (PX_WIDTH, PX_HEIGHT)
    SRS         = 'EPSG:5514'
    STYLES      = ['default', 'default']
    TRANSPARENT = True

    DIRECTORY = 'tiles/'
    SLEEP     = random.randint(0,20) # seconds

    dx = math.fabs(BOTTOM_LEFT[0] - TOP_RIGHT[0]) # area width in units of crs
    dy = math.fabs(BOTTOM_LEFT[1] - TOP_RIGHT[1]) # area height in units of crs

    cols = int(math.ceil(dx / SRS_WIDTH)) + 1
    rows = int(math.ceil(dy / SRS_HEIGHT)) + 1

    counter = 0

    with open('world_file.pngw', 'r') as wld_template:
        tmpl = wld_template.read()

    wms = WebMapService('http://services.cuzk.cz/wms/wms.asp', version='1.1.1')

    for i in xrange(0, rows):
        if not os.path.exists(DIRECTORY + str(i)):
            os.mkdir(DIRECTORY + str(i))

        for j in xrange(0, cols):
            if os.path.exists(DIRECTORY + str(i) +'/kn_' + str(i) + '_' + str(j) + '.png'):
                counter += 1
                continue

            bbox = (
                i * SRS_WIDTH + BOTTOM_LEFT[0],
                j * SRS_HEIGHT + BOTTOM_LEFT[1],
                (i + 1) * SRS_WIDTH + BOTTOM_LEFT[0],
                (j + 1) * SRS_HEIGHT + BOTTOM_LEFT[1]
            )

            img = wms.getmap(
                layers=LAYERS,
                styles=STYLES,
                srs=SRS,
                bbox=bbox,
                size=SIZE,
                format=FORMAT,
                transparent=TRANSPARENT
            )

            with open(DIRECTORY + str(i) +'/kn_' + str(i) + '_' + str(j) + '.png', 'wb') as png:
                png.write(img.read())

            with open(DIRECTORY + str(i) + '/kn_' + str(i) + '_' + str(j) + '.pngw', 'w') as wld_file:
                wld_file.write(tmpl)
                wld_file.write('\n' + str(i * SRS_WIDTH + BOTTOM_LEFT[0]))
                wld_file.write('\n' + str((j+1) * SRS_HEIGHT + BOTTOM_LEFT[1]))

            counter += 1
            print str(counter), ' out of ', str(rows * cols)
            time.sleep(SLEEP)

First, always make sure **you are not violating terms of use** defined by service provider. If you are not, here are the necessary steps:

1. Define your area of interest with bottom left and top right coordinates.
2. Calculate width of single image both in pixels and units of CRS to get the rightsized image. Note that there may be image size restrictions defined by provider (2048 &times; 2048 px is usually the biggest you can get).
3. Define template [world file](https://en.wikipedia.org/wiki/World_file) for referencing images. OWSLib doesn't provide world files to saved images, these have to be created by you. I recommend to use a template file for creating real world files.
4. Be nice! Don't overload the service. I use `time.sleep()` for this.
5. Profit.

The trouble with WMS is that you can't set an arbitrary scale you want to obtain images in (e.g. 1:1 000). It's fairly easy to get all values needed to imitate this behavior though.

Using [QGIS](http://qgis.org) you can:

1. Get bounding box of area you're interested in.
2. Save current view as an image (together with the world file!) and use it as a specimen for your own world files.
3. Derive image width (CRS, pixels) from the saved image, thus getting the same zoom level you were using in QGIS.

Code given is not bulletproof, it will fail on any network error. However, if you restart it after such a crash, it checks for existing files and starts with the first missing, so you don't have to download all the tiles again.
