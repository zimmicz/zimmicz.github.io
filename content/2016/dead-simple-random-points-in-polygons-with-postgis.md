Title: Dead Simple Random Points in Polygons with PostGIS
Date: 2016-8-3 20:10
Tags: postgis, postgresql, sql
Category: SQL

Since PostgreSQL 9.3 there has been a handy little keyword called `LATERAL`, which - combined with `JOIN` - might rock your GIS world in a second. To keep it simple, a `LATERAL JOIN` enables a subquery in the `FROM` part of a query to reference columns from preceding expressions in the `FROM` list. What the heck?

Imagine that not so unusual request to **generate random points in polygons** (something I needed to do today). Do it automatically without your favorite piece of desktop GIS software.

It is pretty easy using `LATERAL JOIN`:

    :::sql
    SELECT
        a.id,
        b.*
    FROM (
        VALUES(
            1,
            ST_SetSRID(
                ST_GeomFromText(
                    'POLYGON((0 0, -1 0, -1 -1, 0 -1, 0 0))'
                ),
            4326)
        )
        UNION ALL
        VALUES(
            2,
            ST_SetSRID(
                ST_GeomFromText(
                    'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'
                ),
            4326)
        )
    ) a(id, geom)
    CROSS JOIN LATERAL (
        SELECT ST_SetSRID(ST_MakePoint(tmp.x, tmp.y), 4326) geom
        FROM (
            SELECT
                random() * (ST_XMax(a.geom) - ST_XMin(a.geom)) + ST_XMin(a.geom) x,
                random() * (ST_YMax(a.geom) - ST_YMin(a.geom)) + ST_YMin(a.geom) y
            FROM generate_series(0,200)
        ) tmp
    ) b;

What actually happened over there? If you want to put points inside polygons, you need... polygons. We will do just fine with two of them created inside this query:

    :::sql
    VALUES(
        1,
        ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((0 0, -1 0, -1 -1, 0 -1, 0 0))'
            ),
        4326)
    )
    UNION ALL
    VALUES(
        2,
        ST_SetSRID(
            ST_GeomFromText(
                'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'
            ),
        4326)
    )

All the magic happens inside the `LATERAL JOIN` part of the query:

    :::sql
    CROSS JOIN LATERAL (
        SELECT ST_SetSRID(ST_MakePoint(tmp.x, tmp.y), 4326) geom
        FROM (
            SELECT
                random() * (ST_XMax(a.geom) - ST_XMin(a.geom)) + ST_XMin(a.geom) x,
                random() * (ST_YMax(a.geom) - ST_YMin(a.geom)) + ST_YMin(a.geom) y
            FROM generate_series(0,200)
        ) tmp
    ) b;

The inner `SELECT` calculates random points based on the extent of the polygon. Note it directly calls `a.geom`, a value that comes from the previous `SELECT`! The `LATERAL JOIN` part is thus run for every row of the previous `SELECT` statement inside `FROM` part of the query. This means it will return 201 points for each of the two polygons (run the query inside QGIS to see the result).

Note all the points fall inside the polygons by accident, because they are **square**. Otherwise a `ST_Contains` or `ST_Within` should be used inside the outermost `WHERE` query to filter outliers. This part could use some tweaking.