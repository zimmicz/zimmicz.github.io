Title: Testing PostgreSQL OGR FDW
Date: 2016-7-1 11:10
Tags: postgresql, gdal
Category: SQL

[PostgreSQL foreign data wrappers](https://wiki.postgresql.org/wiki/Foreign_data_wrappers) are used to connect PostgreSQL database to different datasources, e.g. other SQL databases, CSV files, XLS spreadsheets&times;

The one I've been interested in for several months is [Paul Ramsey's OGR FDW](https://github.com/pramsey/pgsql-ogr-fdw) - it gives you access to OGR supported spatial formats directly from your database. *No more shapefiles lying around?*

Each foreign data wrapper should have three basic components:

* foreign server object
* foreign user mapping - not necessary if you're not connecting to other database
* foreign table(s)

I got some data about [rivers](http://www.dibavod.cz/download.php?id_souboru=1413) and [dams](http://www.dibavod.cz/download.php?id_souboru=1416) from [DIBAVOD](http://www.dibavod.cz) open datasets to play with.

First define the foreign server object:

    CREATE SERVER dibavod
    FOREIGN DATA WRAPPER ogr_fdw
    OPTIONS (
        datasource '/downloads/dibavod',
        format 'ESRI Shapefile',
        config_options 'SHAPE_ENCODING=CP1250'
    );

Note the OGR specific driver configuration options are available inside `config_options`. In case of ESRI Shapefiles, the `datasource` is the directory your files reside in.

Let's create PostgreSQL tables (use `ogrinfo` or Paul's `ogr_fdw_info` to list the columns):

    CREATE FOREIGN TABLE rivers (
        fid integer,
        utokj_id numeric,
        utokjn_id numeric,
        utokjn_f numeric,
        prprop_z integer,
        ex_jh integer,
        pozn text,
        shape_leng numeric,
        naz_tok text,
        idvt integer,
        tok_id numeric,
        shape_len numeric,
        geom geometry(LINESTRING, 5514)
    )
    SERVER dibavod
    OPTIONS (layer 'A02_Vodni_tok_JU');

    CREATE FOREIGN TABLE dams (
        fid integer,
        objectid integer,
        naz_na text,
        nadr_gid numeric,
        kota_hladi numeric,
        hloubka numeric,
        zatop_ploc numeric,
        objem numeric,
        kota_hraz numeric,
        kota_preli numeric,
        kota_vypus numeric,
        plocha_m2 numeric,
        shape_area numeric,
        shape_len numeric,
        geom geometry(MULTIPOLYGON, 5514)
    )
    SERVER dibavod
    OPTIONS (LAYER 'A05_Vodni_nadrze');

Note the `fid` column - required for **write access** to underlying datasource.

Things to remember:

* foreign tables mean no constraints nor indices
* no indices mean spatial queries are terribly slow compared to PostGIS
* I like the idea of `CREATE UNLOGGED TABLE dams2 AS SELECT * FROM dams`, not sure what to use it for though