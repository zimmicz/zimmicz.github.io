Title: PostGIS Case Study: Vozejkmap Open Data (Part II)
Date: 2015-02-21 20:54
Tags: postgresql, postgis
Category: SQL

[In the first part of my little case study]({{ pcposturl(2014, 12, 02, 'postgis-case-study-vozejkmap-open-data-part-i') }}) I downloaded [vozejkmap.cz](http://vozejkmap.cz) dataset and imported it into the PostGIS database. Having spatial data safely stored the time comes to get it onto the map. Libraries used are:

- [Leaflet](http://leafletjs.com)
- [Leaflet.awesome-markers](https://github.com/lvoogdt/Leaflet.awesome-markers)
- [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster)

I teach cartography visualization classes this semester and this map should serve well as an example of what can be done with online maps.

## Retrieving data from the PostGIS database

Our goal is to build the whole map as a static HTML page without any backend logic. Thus, data needs to be extracted from the database into the format readable with Leaflet - [GeoJSON](http://geojson.org/).

That's fairly easy with the [postgresonline.com tutorial](http://www.postgresonline.com/journal/archives/267-Creating-GeoJSON-Feature-Collections-with-JSON-and-PostGIS-functions.html). It took me quite a time to find out what the following query does. Splitting it into smaller chunks helped a lot.

    SELECT row_to_json(fc)
    FROM (
    SELECT 'FeatureCollection' AS type,
        array_to_json(array_agg(f)) AS features
        FROM (SELECT 'Feature' AS type,
            ST_AsGeoJSON(lg.geom)::json As geometry,
            row_to_json((SELECT l FROM (SELECT id, title, location_type, description, author_name, attr1, attr2, attr3) AS l
      )) AS properties
    FROM vozejkmap AS lg ) AS f )  AS fc \g /path/to/file.json;

To get all rows with `type`, `geometry` and `properties` columns (these are the ones defined in GeoJSON specification, see the link above), run this:

    SELECT 'Feature' AS type,
                ST_AsGeoJSON(lg.geom)::json As geometry,
                row_to_json((SELECT l FROM (SELECT id, title, location_type, description, author_name, attr1, attr2, attr3) AS l
          )) AS properties
        FROM vozejkmap AS lg

`array_agg()` squashes all the rows into an array while `array_to_json()` returns the array as JSON.

    SELECT 'FeatureCollection' AS type,
        array_to_json(array_agg(f)) AS features
        FROM (SELECT 'Feature' AS type,
            ST_AsGeoJSON(lg.geom)::json As geometry,
            row_to_json((SELECT l FROM (SELECT id, title, location_type, description, author_name, attr1, attr2, attr3) AS l
      )) AS properties
    FROM vozejkmap AS lg ) AS f

In the last step (the whole code as shown above) `row_to_json` returns the result as JSON.

### Caveats

If you run this code from the psql console, be sure you

- set *show only row* to true with `\t`
- set *expanded output* to false with `\x off`

If you don't, you'll have lots of hyphens and column names saved to the json file.

## Leaflet map

Map JavaScript is rather simple with ~30 lines of code (not taking styles into account). Thanks to the great plugins it is easy to show ~7,600 points on the map real quick.

I didn't do much customization apart from styling markers and binding popups.

<img src="{filename}/assets/postgis-case-study-vozejkmap-open-data-part-ii/map.png" title="vozejkmap.cz data map" class="img-responsive centered">

## What's next

1. [Turf](http://turfjs.org) which means I need to think of what could be fun to do with this data
2. Layers switching
3. Map key (by extending L.Control)

The code is still [available at my GitHub](https://github.com/zimmicz/vozejkmap-to-postgis).
