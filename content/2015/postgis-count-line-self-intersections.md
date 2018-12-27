Title: PostGIS: Count Line Self-Intersections
Date: 2015-03-30 09:12
Tags: postgresql, postgis
Category: SQL

[Is there a way of using PostgreSQL + PostGIS for finding the number of self intersections in a linestring?](https://gis.stackexchange.com/questions/107927/counting-self-intersections-of-linestring-using-postgis/140674#140674) was a question that made me think of this problem. I came up with a solution that takes just a few lines of code.

Assume the following geometries:

    CREATE TABLE test2 (
        id integer NOT NULL,
        wkb_geometry geometry(LineString,5514)
    );
    COPY test2 (id, wkb_geometry) FROM stdin;
    1   01020000208A15000004000000CCDC7845E339EEBFF2003B4A8A08E1BFE4154DAB7C31DCBF24C2042773E3E53F2287BA2CC591E43F604749BFE3B2E2BF2AE9770A11B8F0BF9C91435D56C0C63F
    2   01020000208A1500000600000050212BF9E63EC03F1FA046FD69F1EA3F504D44212915EA3F74A99EDF44E3F33F2CE2805DFAB1F33F805D24B1B189DC3F9834DE5938C1F53FB56F1FBF8AAFEC3F24D0C85B4666EA3FF311B0D8D75BE93F306EAA073894D23FA841B27E3404F33F
    \.

<img src="{static}/assets/postgis-count-line-self-intersections/lines.png" title="Self-intersecting lines" class="img-responsive centered">

Note that those geometries are valid while not being simple, thus, `ST_IsValidReason()` wouldn't help much. What if we compared it to their single counterparts? Those would have had vertices at intersections. Once you know the original number of vertices and the number of simple geometry vertices, it is fairly easy to subtract those two.

    WITH noded AS (
    SELECT id, COUNT(id)
    FROM (
        SELECT DISTINCT (ST_DumpPoints(ST_Node(wkb_geometry))).geom, id
        FROM test
    ) tmp  group by id
    ),
    test AS (
        SELECT id, COUNT(id)
            FROM (
                SELECT DISTINCT (ST_DumpPoints(wkb_geometry)).geom, id
                FROM test
            ) tmp  group by id
    )

    SELECT noded.id, noded.count - test.count cnt FROM noded JOIN test USING (id);

This query gives you geometry id and the difference in number of vertices between the original and simple geometry. Note the `DISTINCT` in the `noded` CTE - with `ST_Node()` you get `one vertex x number of intersecting lines` for each intersection. `DISTINCT` gives you just one of them.

The query result on my `test` table:
<table>
    <tr>
        <th>id</th>
        <th>cnt</th>
    </tr>
    <tr>
        <td>1</td>
        <td>1</td>
    </tr>
    <tr>
        <td>2</td>
        <td>2</td>
    </tr>
</table>
