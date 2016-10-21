Title: Ogrinfo Output Formatting
Date: 2016-10-21 23:00
Tags: gdal
Category: automation

Today my workmate asked if there was a way to see an attribute table other than importing spatial data into a PostGIS database. I told him about QGIS and while talking about other GIS stuff, I started thinking about *pipes* and how awesome it would be to actually format the output of the `ogrinfo` command.

Here it is. It is just a much longer way to do `ogr2ogr -f "CSV" dest source`, but sometimes you just have to experiment a bit.

    :::bash
    #!/bin/bash
    FILE=$1

    function columns {
        ogrinfo $FILE -al -so | \
        sed '/Column/,$!d' | \
        sed '/Geometry Column/d' | \
        sed -e 's/Column =/\:/g' | \
        awk -F: '{print $1}' | \
        awk -v RS= -v OFS="|" '{$1 = $1} 1'
    }

    function data {
       ogrinfo $FILE -al | \
       sed '/OGRFeature/,$!d' | \
       sed '/POLYGON\|LINESTRING\|POINT/ d' | \
       sed -e 's/OGRFeature\(.*\)\://g' | \
       sed -e 's/.*\s*\(.*\)\s*=\s*//g' | \
       awk -v RS= -v OFS="|" '{$1 = $1} 1'
    }

    { columns; data; }

The result can be piped to other `bash` functions, such as `less` or `more`. I call it `ogrinfotable`.
