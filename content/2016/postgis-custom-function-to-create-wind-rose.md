Title: PostGIS Custom Function to Create Wind Rose
Date: 2016-09-01 22:00
Tags: postgis, postgresql, sql
Category: SQL

I've come across the [beautiful GIS StackExchange question](http://gis.stackexchange.com/questions/208797/draw-wind-rose-with-qgis-from-postgis/) recently, asking how to draw a [wind rose](https://en.wikipedia.org/wiki/Wind_rose) within PostGIS.

<div class="text-center">
<img src="http://i.stack.imgur.com/0xAMU.png">
</div>

It's pretty easy to accomplish this with a custom PLPGSQL procedure below, that takes line geometry, number of sections and radius of the inner circle as parameters.

<!-- codeblock -->

    :::sql
    CREATE OR REPLACE FUNCTION ST_WindRose(
        line geometry,
        directions int,
        radius numeric
    )
    RETURNS TABLE (
        id integer,
        geom geometry(LINESTRING)
    )
    AS $ST_WindRose$
    BEGIN
        IF directions % 2 <> 0 THEN
            RAISE EXCEPTION 'Odd number of directions found, please provide even number of directions instead.';
        END IF;

    IF radius > ST_Length(line) THEN
        RAISE EXCEPTION 'Inner circle radius is bigger than the wind rose diameter, please make it smaller.';
    END IF;

    RETURN QUERY
    WITH rose AS (
        SELECT
            ST_Rotate(_line, radians(360) / directions * dirs.id, ST_Centroid(_line)) _line
        FROM (
            SELECT line _line
        ) a
        CROSS JOIN (
            SELECT generate_series(1, directions / 2) id
        ) dirs
    )
    SELECT
        row_number() OVER ()::integer id,
        _line geom
    FROM (
        SELECT _line FROM rose
        UNION ALL
        SELECT ST_ExteriorRing(ST_Buffer(ST_Centroid(line), radius, 30)) -- inner circle
        UNION ALL
        SELECT ST_ExteriorRing(ST_Buffer(ST_Centroid(line), ST_Length(line)/2, 30)) -- outer circle
    ) a;
    END
    $ST_WindRose$
    LANGUAGE PLPGSQL;

Wind rose created with this function might look like the one below.

<div class="text-center">
<img src="http://i.stack.imgur.com/4OD0J.png">
</div>

Run it as follows. The `line` parameter should be a simple straight line made of just two vertices.

<!-- codeblock -->

    :::sql
    SELECT * FROM ST_WindRose(ST_MakeLine(ST_MakePoint(0,0), ST_MakePoint(0,1)), 12, 0.01);