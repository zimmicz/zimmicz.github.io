Title: How to convert DGN to Tiff with GDAL
Date: 2016-2-21 18:45
Tags: gdal
Category: automation

We have to deal with DGN drawings quite often at [CleverMaps](http://www.clevermaps.cz) - heavily used for infrastructure projects (highways, roads, pipelines), they are a pure nightmare to the GIS person inside me. Right now, I'm only capable of converting it into a raster file and serve it with Geoserver. The transformation from DGN to PDF to PNG to Tiff is not something that makes me utterly happy though.

All you need to do the same is <a href="{tag}gdal">GDAL</a>, ImageMagick, some PDF documents created out of DGN files - something MicroStation can help you with - and their upper left and lower right corner coordinates.

    :::bash
    # I recommend putting some limits on ImageMagick - it tends to eat up all the resources and quit
    export MAGICK_MEMORY_LIMIT=1512
    export MAGICK_MAP_LIMIT=512
    export MAGICK_AREA_LIMIT=1024
    export MAGICK_FILES_LIMIT=512
    export MAGICK_TMPDIR=/partition/large/enough

    # I expect two files on the input: the first is PDF file with drawing, the second is a simple text file with four coordinates on a single line in the following order: upper left x, upper left y, lower right x, lower right y
    INPUT=${1:?"PDF file path"}
    COORDS=${2:?"Bounding box file path"}
    OUTPUTDIRNAME=$(dirname $INPUT)
    OUTPUTFILENAME=$(basename $INPUT | cut -d. -f1).png
    OUTPUTPATH=$OUTPUTDIRNAME/$OUTPUTFILENAME

    # create PNG image - I actually don't remember why it didn't work directly to Tiff
    gdal_translate \
        -co WORLDFILE=YES \
        -co ZLEVEL=5 \
        -of PNG \
        --config GDAL_CACHEMAX 500 \
        --config GDAL_PDF_DPI 300 \
        -a_srs EPSG:5514 \ # Czech local CRS
        -a_ullr $(echo $(cat $COORDS)) \ # read the file with coordinates
        $INPUT \
        $OUTPUTPATH

    # convert to Tiff image
    convert \
        -define tiff:tile-geometry=256x256 \
        -transparent white \ # drawings come with white background
        $OUTPUTPATH \
        ${OUTPUTPATH/.png}_alpha.tif

    # build overwies to speed things up
    gdaladdo ${OUTPUTPATH/.png}_alpha.tif 2 4 8 16 32

And you're done. The `.wld` file will be present for each resulting file. I rename it manually to match the name of a GeoTiff - that should be probably done automatically as well.