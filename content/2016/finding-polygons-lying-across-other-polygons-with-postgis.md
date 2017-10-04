Title: Finding Polygons Lying across Other Polygons with PostGIS
Date: 2016-08-05 19:39
Tags: postgis, postgresql, sql
Category: SQL

Doing overlays (`ST_Intersection()`) in PostGIS based on spatial relationships (`ST_Intersects()`, `ST_Contains()`, &hellip;) is so easy it is not something you get particularly excited about.

Today I faced a bit more interesting task: **given two polygon layers, get me all the polygons from layer A such that they lie across the polygons from layer B and&hellip; a picture worth a thousand words, right?**

<div class="text-center"><img data-echo="/posts/assets/finding-polygons-lying-across-other-polygons-with-postgis/polygons.svg" /></div>

I hope you got the idea, it is fairly simple:

1. Intersect A (red, blue) with B (green)
2. Subtract the result of previous from layer A
3. Combine results from steps 1 and 2
4. Keep polygon only if its id occurs more than twice (that means it went straight through the layer B)
5. Profit!

<!-- codeblock -->

    :::sql
    WITH overlays AS (
    /* nothing fancy here */
        SELECT
            A.ogc_fid a_id,
            B.ogc_fid b_id,
            ST_Intersection(A.geom, B.geom) geom,
            ST_Area(ST_Intersection(A.geom, B.geom) area_shared
        FROM A
        JOIN B ON (ST_Intersects(A.geom, B.geom)
    ),
    diffs AS (
    /* note this is a 1:1 relationship in ST_Difference */
    /* a little hack is needed to prevent PostGIS from returning its usual difference mess */
        SELECT
            o.a_id,
            o.b_id,
            (ST_Dump(ST_Difference(ST_Buffer(A.geom, -0.0001), o.geom))).geom, -- ugly hack
            o.area_shared
        FROM overlays o
        JOIN A ON (o.a_id = A.id)
    ),

    merged AS (
    /* put those two result sets together */
        SELECT * FROM overlays
        UNION ALL
        SELECT * FROM diffs
    ),

    merged_reduced AS (
    /* get only those A polygons that consist of three parts at least for each intersection with B polygon */
      SELECT
        m.*
      FROM merged m
      JOIN (
        SELECT
          a_id,
          b_id
        FROM merged
        GROUP BY a_id, b_id
        HAVING COUNT(1) > 2
      ) a ON (a.a_id = m.a_id AND a.b_id = m.b_id)
    )
    /* do as you wish with the result */
    SELECT *
    FROM merged_reduced;

In my case, centerlines of layer B were also included and their length inside each intersection was used to divide the area of the smallest part with. It was fun, actually.
