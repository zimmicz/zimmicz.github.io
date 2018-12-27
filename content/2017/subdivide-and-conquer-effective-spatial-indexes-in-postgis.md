Title: Subdivide and Conquer: Effective Spatial Indexes in PostGIS
Date: 2017-01-10 21:45
Category: SQL
Tags: sql, postgresql, postgis

Spatial indexes are absolutely crucial part of any spatial database and - as I tend to say quite often - only a fool would try to query spatial data without building spatial indexes beforehand.

Spatial indexes are based on bounding box comparisons, which are generally very fast. Yet, there are situations when spatial indexes don't help much (or they don't help as much as they could, if you wish).

<div class="text-center"><img src="{static}/assets/subdivide-and-conquer-effective-spatial-indexes-in-postgis/index.svg" /></div>

Bounding box comparisons are effective with lots of small bounding boxes rather then few large ones. Why? See the picture above. The curved line (imagine it's a pipeline for example) clearly demonstrates when the spatial index/bounding box comparison might fall short of what you'd expect.

Once the bounding box gets really big, it intersects so many other geometries' bounding boxes that the whole comparison starts to slow down.

Luckily, PostGIS 2.2 introduced a [ST_Subdivide](http://postgis.net/docs/ST_Subdivide.html) function that can lend a helping hand in here.

Until today, we delivered the parcel geometries into our [real estate acquisition process system](https://www.symap.cz) with the following query, that takes all the geometries from the `req_geom` table (pipelines, remember?) and intersects them with cadastral parcels. The second part of the query adds those parcels that haven't been digitalized and were created manually by one of my workmates.

    :::sql
    INSERT INTO requested_parcels (uid, par_id)
    SELECT
        reqs.uid,
        b.id par_id
     FROM
        running_requests reqs
     JOIN
        req_geom a ON (reqs.uid = a.uid)
     JOIN
        pargeo b ON (ST_Intersects(a.geom, b.geom))
     UNION
     SELECT
        reqs.uid,
        a.idpar::numeric
     FROM
        running_requests reqs
     JOIN
         req_man a ON (reqs.uid = a.uid);

 It's a perfectly standard query that intersects several request geometries with ~20M parcels, nothing really fancy. Except that it takes 25 minutes to finish. Why? Pipelines, remember?

 Yet, the query below takes only 30 seconds to finish (that's a huge time saver considering that the whole process used to take ~40 minutes)! Why? Because the `ST_Subdivide` effectively shrinks the `req_geom` geometries until they have 50 vertices each at most. Such small geometries are perfect input for the bounding box comparison. Remember to call `DISTINCT` when using `ST_Subdivide`, you'd probably get duplicate parcel ids otherwise.

 I also replaced the `UNION` with the [`WHERE NOT EXISTS`]({filename}../2015/postgresql-in-vs-exists.md) expression, as it's reasonable to assume that numeric ids comparison will be faster.

    :::sql
    INSERT INTO requested_parcels (uid, par_id)
    SELECT DISTINCT
        reqs.uid,
        b.id par_id
     FROM
        running_requests reqs
     JOIN
        (
            SELECT
                uid,
                ST_Subdivide(geom, 50) geom
            FROM
                req_geom
         ) a ON (reqs.uid = a.uid)
     JOIN
         pargeo b ON (ST_Intersects(a.geom, b.geom));

     INSERT INTO requested_parcels (uid, par_id)
     SELECT
         reqs.uid,
         a.idpar::numeric
     FROM
         running_requests reqs
     JOIN
         req_man a ON (reqs.uid = a.uid)
     WHERE NOT EXISTS (
         SELECT 1
         FROM pozadovane_parcely pp
         WHERE pp.par_id = a.idpar
      );
