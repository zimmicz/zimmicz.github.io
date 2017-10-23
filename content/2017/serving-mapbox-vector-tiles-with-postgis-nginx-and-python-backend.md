Title: Serving Mapbox Vector Tiles with PostGIS, Nginx and Python Backend
Date: 2017-10-23 16:00
Category: SQL
Tags: postgis, python
Image: https://www.zimmi.cz/posts/assets/serving-mapbox-vector-tiles-with-postgis-nginx-and-python-backend/mvt.png

[Since version 2.4.0, PostGIS can serve MVT](({filename}../2017/postgis-as-a-mapbox-vector-tiles-generator.md)) data directly. MVT returning queries put heavy workload on the database though. On top of that, each of the query has to be run again every time a client demands the data. This leaves us with plenty of room to optimize the process.

<div class="text-center"><img data-echo="/posts/assets/serving-mapbox-vector-tiles-with-postgis-nginx-and-python-backend/election.gif"/></div>


During the last week, while working on the Czech legislative election data visualization, I've struggled with the server becoming unresponsive far too often due to the issues mentioned above.

<div class="text-center"><img data-echo="/posts/assets/serving-mapbox-vector-tiles-with-postgis-nginx-and-python-backend/schema.png"/></div>

According to the schema, the first client to come to the server:

* goes through filesystem unstopped, because there are no cached files yet,
* continues to the Flask backend and asks for a file at `{z}/{x}/{y}`,
* Flask backend asks the database to return the MVT for the given tile,
* Flask backend writes the response to the filesystem and sends it to the client.

Other clients get tiles directly from the filesystem, leaving the database at ease.

## Nginx

Nginx is fairly simple to set up, once you know what you're doing. The `/volby-2017/municipality/` location serves static MVT from the given alias directory. If not found, the request is passed to `@postgis` location, that asks the Flask backend for the response.

    :::bash
    server election {
        location /volby-2017/municipality {
                alias /opt/volby-cz-2017/server/cache/;
                try_files $uri @postgis;
        }

        location @postgis {
                include uwsgi_params;
                uwsgi_pass 127.0.0.1:5000;
        }
    }

## Flask backend

<script src="https://gist.github.com/zimmicz/46485676e1cf3d6566f0aaa7f93f055b.js"></script>

## Generating static MVT in advance

If you're going to serve static tiles that don't change often, it might be a good idea to use PostGIS to create files in advance and serve them with Nginx.


    :::sql
    CREATE TABLE tiles (
        x integer,
        y integer,
        z integer,
        west numeric,
        south numeric,
        east numeric,
        north numeric,
        geom geometry(POLYGON, 3857)
    );

Using [mercantile](https://github.com/mapbox/mercantile), you can create the `tiles` table holding the bounding boxes of the tiles you need. PostGIS them inserts the actual MVT into the `mvt` table.

    :::sql
    CREATE TEMPORARY TABLE tmp_tiles AS
        SELECT
            muni.muni_id,
            prc.data,
            ST_AsMVTGeom(
                muni.geom,
                TileBBox(z, x , y, 3857),
                4096,
                0,
                false
            ) geom,
            x,
            y,
            z
        FROM muni
        JOIN (
            SELECT
                x,
                y,
                z,
                geom
            FROM tiles
        ) bbox ON (ST_Intersects(muni.geom, bbox.geom))
        JOIN party_results_cur prc ON (muni.muni_id = prc.muni_id);
    CREATE TABLE mvt (mvt bytea, x integer, y integer, z integer);
    DO
    $$
    DECLARE r record;
    BEGIN
    FOR r in SELECT DISTINCT x, y, z FROM tmp_tiles LOOP
        INSERT INTO mvt
        SELECT ST_AsMVT(q, 'municipality', 4096, 'geom'), r.x, r.y, r.z
        FROM (
            SELECT
                muni_id,
                data,
                geom
            FROM tmp_tiles
            WHERE (x, y, z) = (r)
        ) q;
        RAISE INFO '%', r;
    END LOOP;
    END;
    $$;

Once filled, the table rows can be written to the filesystem with the simple piece of Python code.

    :::python
    #!/usr/bin/env python

    import logging
    import os
    import time
    from sqlalchemy import create_engine, text

    CACHE_PATH="cache/"

    e = create_engine('postgresql:///')
    conn = e.connect()
    sql=text("SELECT mvt, x, y, z FROM mvt")
    query = conn.execute(sql)
    data = query.cursor.fetchall()

    for d in data:
        cachefile = "{}/{}/{}/{}".format(CACHE_PATH, d[3], d[1], d[2])
        print(cachefile)

        if not os.path.exists("{}/{}/{}".format(CACHE_PATH, d[3], d[1])):
            os.makedirs("{}/{}/{}".format(CACHE_PATH, d[3], d[1]))

        with open(cachefile, "wb") as f:
            f.write(bytes(d[0]))

## Conclusion

PostGIS is a brilliant tool for generating Mapbox vector tiles. Combined with Python powered static file generator and Nginx, it seems to become the only tool needed to get you going.
