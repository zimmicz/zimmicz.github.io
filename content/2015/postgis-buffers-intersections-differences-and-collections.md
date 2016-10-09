Title: PostGIS: Buffers, Intersections, Differences And Collections
Date: 2015-03-19 19:27
Tags: postgis, postgresql
Category: SQL

Being part of [CleverMaps](http://clevermaps.cz) means doing lot of nasty work with PostGIS. Recently, I've been given a following task that needed to be done for a really big project dealing with agricultural parcels:

- given a polygonal shapefile of agricultural parcels, create 20m wide buffers around all of them,
- extract holes from these parcels,
- clip buffers so they don't overlap with other parcels,
- get rid of overlaps between nearby parcels (e.g. dissolve them),
- create output combined from holes and buffers,
- the output must not contain features having more than ~1,000,000 vertices

This process is going to be run ~20&times; on layers with ~40,000-70,000 polygons.

## Input data
- polygonal layer of agricultural parcels
- rectangular grid (7.5 &times; 7.5 km) for cutting the output

## First try

My initial effort was to union all the buffers and then clip them with a rectangular grid. Long story short: **Don't do that. Never. Ever. I mean it.**

It works fine until you end up with one huge multipolygon having like ~2,000,000 vertices. But then you need to split it somehow so you meet the 1,000,000 limit rule (see list above). Spatial index doesn't help you much in such cases, so that really huge polygon is being cut by every rectangle it intersects and it takes hours and hours. It's just a no go.

## The other way round

Let's put it the other way round. First, split buffers by rectangular grid, doing union on each cell separately.

### Import

Using the swiss knife of GIS to import the data:

    export SHAPE_ENCODING="ISO-8859-1"
    ogr2ogr -f PostgreSQL PG:"dbname=db user=postgres" parcels.shp -lco ENCODING=UTF-8 -t_srs "EPSG:2154"
    ogr2ogr -f PostgreSQL PG:"dbname=db user=postgres" grid.shp -lco ENCODING=UTF-8 -t_srs "EPSG:2154"

### PostGIS processing

Recently I stumbled upon a psql `\set` command. Launching several queries on the same table, it might be useful to define it's name with `\set table tablename`:

    \set table 'parcels'
    -- prepare separate table for holes (inner rings)
    DROP TABLE IF EXISTS holes;
    CREATE TABLE holes (
    id serial,
    ilot_id varchar,
    wkb_geometry geometry('Polygon', 2154),
    path integer);

I found the following query an easy way to get all the rings from geometries having more than one ring:

    INSERT INTO holes (ilot_id, wkb_geometry, path) (
    SELECT id,
        (ST_DumpRings(wkb_geometry)).geom::geometry('Polygon', 2154) as wkb_geometry,
        unnest((ST_DumpRings(wkb_geometry)).path) as path
    FROM :table
    WHERE ST_NRings(wkb_geometry) > 1
    );

Here's a little trick. Doing some checks I found out that some of the polygons had two rings without having any inner ring, both of them being the same. I guess this comes from some kind of human error. This query thus deletes all rings with `path = 0` (exterior rings). At the same time, it deals with that *invalid* polygons by checking their spatial relationship to parcels.

    DELETE FROM holes
        WHERE path = 0
        OR id IN (
            SELECT holes.id
            FROM holes
            JOIN :table ON
                ST_Within(
                    ST_Buffer(holes.wkb_geometry,-1),
                    :table.wkb_geometry
                )
            AND holes.wkb_geometry && :table.wkb_geometry
    );

To my surprise, it is possible that parcel has a hole with another parcel being in that hole. Argh. Find those and get rid of them.

    DROP TABLE IF EXISTS ints;
    CREATE TABLE ints AS
        SELECT holes.*
        FROM holes
        JOIN :table ON ST_Intersects(holes.wkb_geometry, :table.wkb_geometry)
        AND ST_Relate(holes.wkb_geometry, :table.wkb_geometry, '2********');
    DELETE FROM holes
    WHERE id IN (SELECT id FROM ints);

I still need to get the difference between the hole geometry and the parcel that resides inside it - this difference is the actual hole I'm looking for.

    DROP TABLE IF EXISTS diff_ints;
    CREATE TABLE diff_ints AS
        SELECT
            ints.id,
            ST_Difference(
                ints.wkb_geometry,
                ST_Collect(:table.wkb_geometry)
            ) wkb_geometry
        FROM ints, :table
        WHERE ST_Within(:table.wkb_geometry, ints.wkb_geometry)
        GROUP BY ints.wkb_geometry, ints.id;

And I'm done with holes. Get back to buffers.

    DROP TABLE IF EXISTS buffer;
    CREATE TABLE buffer AS
        SELECT id, ST_Buffer(wkb_geometry, 20) wkb_geometry
        FROM :table;
    CREATE INDEX buffer_gist_idx ON buffer USING gist(wkb_geometry);
    ALTER TABLE buffer ADD PRIMARY KEY(id);
    VACUUM ANALYZE buffer;

Combine all the parts together.

    DROP TABLE IF EXISTS diff;
    CREATE TABLE diff AS
        SELECT a.id, ST_Difference(a.wkb_geometry, ST_Union(ST_MakeValid(b.wkb_geometry))) as wkb_geometry
        FROM buffer a, :table b
        WHERE ST_Intersects(a.wkb_geometry, b.wkb_geometry)
        GROUP BY a.id, a.wkb_geometry
        UNION
        SELECT id::varchar, wkb_geometry FROM holes
        UNION
        SELECT id::varchar, wkb_geometry FROM diff_ints;
    CREATE INDEX diff_gist_idx ON diff USING gist(wkb_geometry);
    VACUUM ANALYZE diff;

Collect the geometries in every cell, simplify them a little, snap them to 3 decimal numbers, make them valid and dump them to simple features. This query takes ~300,000 ms which is orders of magnitude faster than my initial attempt.

    DROP TABLE IF EXISTS uni;
    CREATE TABLE uni AS
    SELECT
        g.ogc_fid AS grid_id,
        (ST_Dump(
            ST_MakeValid(
                ST_SnapToGrid(
                    ST_SimplifyPreserveTopology(
                        ST_CollectionExtract(
                            ST_Buffer(
                                ST_Collect(
                                    ST_Intersection(a.wkb_geometry, g.wkb_geometry)
                                )
                            , 0)
                        , 3)
                    , 0.1)
                , 0.001)
            )
        )).geom as wkb_geometry
    FROM diff a, grid g
    WHERE ST_Intersects(a.wkb_geometry, g.wkb_geometry)
    GROUP BY g.ogc_fid;

After running the query it is reasonable to check the results. I'm only interested in polygonal geometries, `ST_GeometryType()` would tell me of any other geometry type. Invalid geometries are not allowed.

    SELECT DISTINCT ST_GeometryType(wkb_geometry) FROM uni;
    SELECT COUNT(1) FROM uni WHERE NOT ST_IsValid(wkb_geometry);

Add primary key on serial column as a last SQL step.

    ALTER TABLE uni ADD COLUMN id serial;
    ALTER TABLE uni ADD PRIMARY KEY(id);

### Export

And spit it out as a shapefile.

    ogr2ogr -f "ESRI Shapefile" output.shp PG:"dbname=ign user=postgres" uni -s_srs "EPSG:2154" -t_srs "EPSG:2154" -lco ENCODING=UTF-8

## Lesson learned

- More of little seems to be faster than less of bigger.
- Never stop learning and trying different approaches.
- Although using `CTE` might be tempting, creating separate tables for separate steps of the whole process is much more comfortable for debugging.
