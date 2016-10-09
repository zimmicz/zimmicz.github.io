Title: Using PostgreSQL To Update Outdated Map Links
Date: 2015-02-16 18:38
Tags: postgresql, regex
Category: SQL

[We've rolled out](http://www.edpp.cz/pdb_mapa-povodnoveho-planu-mesta/) completely new map GUI at [edpp.cz](http://edpp.cz) built on top of [OpenLayers 3](http://ol3js.org). It looks great and has lots of functions both for BFU and power users. The only pitfall that came with moving away from OpenLayers 2 were remarkable differences in zoom levels between the old map and the new one.

Each of our maps is defined by our admins (center, zoom level, layers) at the map creation. Lots of links calling different views of map are created as well. They take form of `http://edpp.cz/some-map?0=0&1=0...zoom=5`. That `zoom=<Number>` started causing troubles immediately after the map switch. No way my workmates would update them one by one as there were ~4,500 of them. Sounds like a task for little bit of regular expressions and some SQL updates.

    UPDATE table
        SET column = regexp_replace(column, 'zoom=\d', 'zoom=' || subquery.zoom, 'g')
        FROM (
            SELECT regexp_replace(
                substring(column from 'zoom=\d'),
                'zoom=(\d)',
                '\1',
                'g')::integer + 2 AS zoom, guid
            FROM table) AS subquery
        WHERE column ~ 'zoom=\d'
            AND table.guid = subquery.guid

That's what I've come up with. It basically extracts the zoom level from the link, adds number two to its value and writes it back to the string.
