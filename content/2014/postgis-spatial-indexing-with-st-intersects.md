Title: PostGIS Spatial Indexing With ST_Intersects
Date: 2014-11-23 10:05
Tags: postgis
Category: SQL

[PostGIS docs](http://postgis.net/docs/ST_Intersects.html) clearly states that:
    > This function call will automatically include a bounding box comparison that will make use of any indexes that are available on the geometries.

That means (or at least I think so) that you shouldn't bother with using [operators](http://postgis.net/docs/reference.html#Operators) before calling this function.

[I was preparing](http://slides.com/michalzimmermann) my second lecture on PostGIS and I was experimenting a bit and came up with an interesting thing on this matter:

Let's have two SQL relations, `roads` and `regions`. I would like to retrieve every road that intersects a certain region. Spatial indexes were built beforehand on both tables.

First try:

    EXPLAIN ANALYZE SELECT roads.* FROM roads
    JOIN regions ON ST_Intersects(roads.geom, regions.geom)
    WHERE regions."NAZEV" = 'Jihomoravský';`

And here comes the result:

    Nested Loop  (cost=4.85..324.26 rows=249 width=214) (actual time=45.102..5101.472 rows=74253 loops=1)
    ->  Seq Scan on regions  (cost=0.00..12.62 rows=1 width=32) (actual time=0.015..0.018 rows=1 loops=1)
         Filter: (("NAZEV")::text = 'Jihomoravský'::text)
         Rows Removed by Filter: 13
    ->  Bitmap Heap Scan on roads  (cost=4.85..311.38 rows=25 width=214) (actual time=45.079..4931.495 rows=74253 loops=1)
         Recheck Cond: (geom && regions.geom)
         Rows Removed by Index Recheck: 154841
         Filter: _st_intersects(geom, regions.geom)
         Rows Removed by Filter: 71212
         ->  Bitmap Index Scan on roads_idx  (cost=0.00..4.85 rows=75 width=0) (actual time=40.142..40.142 rows=145465 loops=1)
               Index Cond: (geom && regions.geom)
    Total runtime: 5181.459 ms

I was pretty satisfied with the result, I kept digging deeper though.

Second try:

    EXPLAIN ANALYZE SELECT roads.* FROM roads
    JOIN regions ON roads.geom && regions.geom
    WHERE regions."NAZEV" = 'Jihomoravský' AND ST_Intersects(roads.geom, regions.geom);

And the result:

    Nested Loop  (cost=0.29..21.19 rows=1 width=214) (actual time=3.041..3850.302 rows=74253 loops=1)
    ->  Seq Scan on regions  (cost=0.00..12.62 rows=1 width=32) (actual time=0.021..0.024 rows=1 loops=1)
         Filter: (("NAZEV")::text = 'Jihomoravský'::text)
         Rows Removed by Filter: 13
    ->  Index Scan using roads_idx on roads  (cost=0.29..8.55 rows=1 width=214) (actual time=2.938..3681.432 rows=74253 loops=1)
         Index Cond: ((geom && regions.geom) AND (geom && regions.geom))
         Filter: _st_intersects(geom, regions.geom)
         Rows Removed by Filter: 71212
    Total runtime: 3930.270 ms

Now there's a significant difference between total runtimes of both queries and - more important - also a difference between their query plans. The latter is like **20 % faster**.

I'm puzzled about this behavior and would appreciate any thoughts on this. Reach me at [Twitter](http://twitter.com/zimmicz), [LinkedIn](https://www.linkedin.com/pub/michal-zimmermann/29/8/b30) or e-mail (zimmicz[at]gmail.com).
