Title: Clip Raster With Vector Using GDAL
Date: 2015-07-21 07:51
Tags: linux, gdal
Category: automation

Recently I needed to clip several raster files with polygonal layer of municipalities. A solution to this task is pretty straightforward using [GDAL](http://gdal.org/) and a bit of Bash and QGIS thrown in.

The necessary steps are:

1. Put each polygon to a separate file. This can be done easily with `Vector - Data Management Tools - Split Vector Layer` in QGIS. The solution below assumes that each shapefile has the same basename as the raster file.
2. These polygons are stored in the `obce` subfolder relative to the folder with rasters.
3. An `output` folder exists that is used for... output, yes.
4. Rasters are saved with output alpha band for nodata (`-dstalpha` flag).
5. The script takes one argument - raster name.
6. Profit!

```bash
#!/usr/bin/env bash

OBEC=$1
BASE=$(basename $OBEC _jpeg.tif)
echo $BASE
EXTENT=$(ogrinfo -so obce/${BASE}.shp $BASE | grep Extent \
| sed 's/Extent: //g' | sed 's/(//g' | sed 's/)//g' \
| sed 's/ - /, /g')
EXTENT=$(echo $EXTENT | awk -F ',' '{print $1 " " $4 " " $3 " " $2}')
gdal_translate -projwin $EXTENT -of GTiff $OBEC output/${BASE}.tif
gdalwarp -dstalpha -s_srs 'EPSG:5514' -t_srs 'EPSG:5514' \
    -co COMPRESS=JPEG \
    -co TILED=YES -\
    of GTiff \
    -cutline obce/${BASE}.shp \
    output/${BASE}.tif output/${BASE}.final.tif
```

Note that if `gdalwarp` doesn't recognize an EPSG code (which is the case for my country national grid), you might pass it as a PROJ.4 string.

According to the point 5 in the above list, the script needs to be run in a loop:

```bash
for f in *_jpeg.tif;
    do the_script_above.sh $f
;done
```