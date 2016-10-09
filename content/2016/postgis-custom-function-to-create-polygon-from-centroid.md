Title: PostGIS Custom Function to Create Polygon from Centroid
Date: 2016-08-28 09:00
Tags: postgis, postgresql, sql
Category: SQL

Needed to create a polygon from a point defining its size in both axes, here's a little syntax sugar to make life easier.

<!-- codeblock -->

    :::sql
    CREATE OR REPLACE FUNCTION ST_PolygonFromCentroid(centroid geometry, xsize numeric, ysize numeric)
    RETURNS geometry
    AS $ST_PolygonFromCentroid$
    SELECT ST_MakeEnvelope(
        ST_X(ST_Translate($1, -$2, -$3)),
        ST_Y(ST_Translate($1, -$2, -$3)),
        ST_X(ST_Translate($1, $2, $3)),
        ST_Y(ST_Translate($1, $2, $3))
    );
    $ST_PolygonFromCentroid$
    LANGUAGE SQL;

Run it as:

<!-- codeblock -->

    :::sql
    SELECT ST_PolygonFromCentroid(ST_SetSRID(ST_MakePoint(13.912,50.633),4326), 1, 1);
