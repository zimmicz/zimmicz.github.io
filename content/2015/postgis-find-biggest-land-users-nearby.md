Title: PostGIS: Finding Biggest Land Users Nearby
Date: 2015-04-03 10:29
Category: SQL
Tags: postgresql, postgis

At [CleverMaps](http://clevermaps.cz) we heavily rely on the cadastre of real estate, which is probably the biggest data source in my country. Using their excellent knowledge of this data set, my teammates often supply me with all kinds of weird challenges.

## Give me the biggest land users nearby

*Find the biggest land users in surrounding cadastral communities for each cadastral community (~ 13K)* being the latest task, here's the query I tackled it with:

    WITH users_ AS (
        SELECT
            cad_code,
            id,
            zipcode,
            city,
            concat_ws(' ',street, concat_ws('/', house_number, street_number)) as street,
            name,
            'Users with more than 10 ha'::text note,
            SUM(acreage) area
            FROM land_blocks -- being a table with info about all the agricultural land blocks
            JOIN users u ON id_uz = id
            GROUP BY cad_code, u.id
            HAVING SUM(acreage) > 10
    ),
    ints AS (
        SELECT
            ku.cad_code as community,
            ku2.cad_code as surrounding,
            ku2.cad_name
        FROM cadastral_community ku
        JOIN cadastral_community ku2
            ON ST_Intersects(ku.geom, ku2.geom)
        WHERE ku.cad_code <> ku2.cad_code
    )
    SELECT
        DISTINCT ON (surrounding, cad_name, u.zipcode, u.city, u.street, u.name)
        surrounding,
        cad_name,
        u.zipcode,
        u.city,
        u.street,
        u.name,
        u.note,
        u.area
    FROM
        users_ u
    JOIN ints
        ON cad_code = community;

Few things to note:

* `concat_ws()` is a great function for joining values that might be `NULL`. If such a value is found, it is skipped and the function continues with the next one (if any). Thus, you'll never get a string ending with a trailing slash (`Street name 55/`).
* With `users_` CTE I get a list of owners having more than 10 hectares of land for each cadastral community. This gives me the inverse result of what I want (if I know the biggest owners in the cadastral community, I know these are the ones that should be listed for surrounding c. communities).
* This *putting-it-all-together* step is done with `ints` CTE that outputs the list of surrounding c. communities for each of them.
* `DISTINCT ON` cleans up the list so the same owners don't appear more than once for any given c. community.

Writing this makes me realize the list should be probably sorted by area so only the occurence with the biggest value is kept for each c. community. Simple `ORDER BY` should deal with this just fine. Or even more sophisticated, using `GROUP BY` to output the total acreage in all surrounding c. communities.
