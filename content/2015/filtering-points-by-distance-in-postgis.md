Title: Filtering points by distance in PostGIS
Date: 2015-07-21 07:51
Category: SQL
Tags: postgis

Filtering really big (millions of rows) point datasets by distance might get catchy when solved with wrong PostGIS functions. Without spatial indexes PostGIS would take ages to finish such task.

[Someone over StackExchange asked](https://gis.stackexchange.com/questions/148184/why-the-execution-of-a-query-is-very-slow-using-postgis) why the next query had been running for 15 hours (!) with no result:

    :::sql
    SELECT
        a.gid,
        b.gid,
        ST_Distance(a.geom,b.geom)
    FROM
        shp1 a,
        shp2 b
    WHERE
        ST_Intersects(
            ST_Difference(
                ST_Buffer(a.geom,2000),
                ST_Buffer(a.geom,500)
            ),
            b.geom
        ) AND
        abs(a.value - b.value) > 400

The answer is quite simple: because it was using wrong functions. Let's see:

1.  `ST_Distance()` does not use spatial index, it's a simple mathematical calculation, it's expensive and it can be replaced by spatial operator for point datasets.
2. `ST_Buffer()` will definitely take time to build polygons around points. And it's being run twice!
3. `ST_Difference()` needs more time to compare the buffers and return just the portion of space they don't share. Isn't it a huge waste to create buffers and then throw them away?
4. `ST_Intersects()` finally checks whether the point should be included in the result.

That was a great challenge to test my knowledge of how PostGIS works and here's my shot at it:

    :::sql
    SELECT * FROM (
        SELECT
            a.gid,
            b.gid,
            a.geom <-> b.geom distance
        FROM
            shp1 a, shp2 b
        WHERE
            abs(a.value - b.value) > 400 AND
            ST_DWithin(a.geom, b.geom, 2000)
        ) sq
    WHERE
        distance > 500;

1. I use [`<->`](http://postgis.net/docs/geometry_distance_centroid.html), a.k.a geometry distance centroid instead of `ST_Distance()`. It takes advantage of spatial indexes, thus it's fast. And it's perfectly fine to use it with point dataset, because the centroid of a bounding box of a point is? That point, exactly. **Spatial indexes have to be built beforehand.**
2. Buffers are not necessary to check whether a geometry lies in a certain distance from another one. That's what `ST_Dwithin()` was made for. With the inner `WHERE` clause I get all the points lying at most 2,000 meters from the current, having the absolute value difference bigger than 400. `ST_Dwithin()` will make use of any spatial index available, unlike `ST_Distance()`.
3. The outer `WHERE` clause throws away all the points closer than 500 meters. Remember, we already got only those not further than 2,000 meters from the previous step.

It took PostGIS 1060545,590 ms (~ 17 minutes) on my Quad-Core Intel® Core™ i5-4210M CPU @ 2.60GHz, 4 GB RAM, 500 GB SSD hard drive, PostgreSQL 9.3 and PostGIS 2.1 with two point datasets having 4M and 300K rows, respectively.