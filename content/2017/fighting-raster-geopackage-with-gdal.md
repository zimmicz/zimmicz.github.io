Title: Fighting Raster GeoPackage with GDAL
Date: 2017-07-19 13:30
Category: GIS
Tags: bash, gdal
Image: https://www.zimmi.cz/posts/assets/fighting-raster-geopackage-with-gdal/gauss.png

As I'm still running Ubuntu 16.04 based Linux Mint, I have no access to GDAL 2.x repositories (except for ubuntugis, that I really don't like to use). Provided with a GeoPackage raster file recently, I had to find a way to load it into QGIS, somehow. The solution is simple: Docker with gdal_translate.

## Preparing the Docker container

I like using Docker for experiments that might leave the OS in an *unexpected* state (which is exactly what happens to me with ubuntugis repository whenever I use it. That's why I don't anymore.). A very simple Dockerfile keeps the troubles away from you.

    :::bash
    FROM ubuntu:17.04
    RUN apt update
    RUN apt install -y gdal-bin

`cd` into the folder and build the image with `docker build -t gdal .`. Once ready, summon the daemon, run the container, mount the GeoPackage file to the container directory and you're ready to rock.

    :::bash
    docker run -v /path/to/geopackage:/home/ -it gdal

## Raster GeoPackage to GeoTiff translation

With the container running, the raster GeoPackage to GeoTiff translation can be done easily with `gdal_translate`. Note I chose to cut the source file into tiles, because the gdal_translate was choking about the resulting size.

    :::bash
    #!/bin/bash
    SIZE=10000
    ULX=-630000
    ULY=-1135450
    LRX=-560000
    LRY=-1172479
    COUNTER_X=0
    COUNTER_Y=0

    while [[ $ULX -lt $LRX ]]
    do
        while [[ $ULY -gt $LRY ]]
        do
            echo $ULX, $(($ULX+$SIZE)), $ULY, $(($ULY-$SIZE))

            gdal_translate \
                -co TILED=YES \
                -co COMPRESS=DEFLATE \
                -co TFW=YES \
                -co NUM_THREADS=ALL_CPUS \
                -a_nodata 0 \
                -of GTiff \
                -projwin $ULX, $ULY, $(($ULX+$SIZE)), $(($ULY-$SIZE)) \
                -projwin_srs EPSG:5514 \
                data/detected.gpkg data/detected_${COUNTER_X}_${COUNTER_Y}.tiff

            ULY=$(($ULY-$SIZE))
            COUNTER_Y=$((COUNTER_Y+1))
        done
        ULX=$(($ULX+$SIZE))
        ULY=-1135450
        COUNTER_X=$((COUNTER_X+1))
    done

## Final Touch: Raster to Vector

After the GeoTiff is written to hard drive, [inotifywait]({filename}../2015/how-to-use-queue-with-rsync.md) can be used to generate overviews. And with ease of calling `gdal_polygonize.py` on each of GeoTiffs&hellip;vector layer, at you service.
