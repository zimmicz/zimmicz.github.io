Title: PostGIS Case Study: VozejkMap Open Data (Part I)
Date: 2014-12-02 17:59
Tags: postgresql, postgis
Category: SQL

[VozejkMap.cz](http://www.vozejkmap.cz) is a Czech **open data** iniatitive that collects data about wheelchair accessible places, e.g. pubs, toilets, cafes etc. As part of being open, they offer a [JSON data download](http://www.vozejkmap.cz/opendata/). JSON is a great text format, not so great spatial format (leaving GeoJSON aside) though. Anyway, nothing that [PostGIS](http://posts.zimmi.cz/tag/postgis/) wouldn't be able to take care of.

### Let's get some data
Using curl or wget, let's download the JSON file:

    wget -O /tmp/locations.json http://www.vozejkmap.cz/opendata/locations.json

We need to split them into rows to load each point into one row:

    sed -i 's/\},{/\n},{/g' /tmp/locations.json

If you peep into the file, you'll see lots of unicode characters we don't want to have in our pretty little table. Here's how we get rid of them:

    echo -en "$(cat /tmp/locations.json)"

### Let's load the data
Let's just be nice and leave the public schema clean.

    CREATE SCHEMA vozejkmap;
    SET search_path=vozejkmap, public;

Load the data:

    CREATE TABLE vozejkmap_raw(id SERIAL PRIMARY KEY, raw text);
    COPY vozejkmap_raw(raw) FROM '/tmp/locations.json' DELIMITERS '#' ESCAPE '\' CSV;

A few notes:

1.  I'm using `/tmp` folder to avoid any permission-denied issues when opening the file from `psql`.
2. By setting `DELIMITERS` to `#` we tell PostgreSQL to load whole data into one column, because it is safe to assume there is no such character in our data.
3. `ESCAPE` needs to be set because there is one trailing quote in the dataset.

### Let's get dirty with spatial data

Great, now what? We loaded all the data into one column. That is not very useful, is it? How about splitting them into separate columns with this query? Shall we call it a `split_part` hell?

    CREATE TABLE vozejkmap AS
    SELECT
        id,
        trim(
            split_part(
                split_part(
                    raw, 'title:', 2
                ),
                ',location_type:', 1
            )
        ) AS title,

        trim(
            split_part(
                split_part(
                    raw, 'location_type:', 2
                ),
                ',description:', 1
            )
        )::integer AS location_type,

        trim(
            split_part(
                split_part(
                    raw, 'description:', 2
                ),
                ',lat:', 1
            )
        ) AS description,

        cast( trim(
            split_part(
                split_part(
                    raw, 'lat:', 2
                ),
                ',lng:', 1
            )
        ) AS double precision) AS lat,

        cast( trim(
            split_part(
                split_part(
                    raw, 'lng:', 2
                ),
                ',attr1:', 1
            )
        )  AS double precision) AS lng,

        trim(
            split_part(
                split_part(
                    raw, 'attr1:', 2
                ),
                ',attr2:', 1
            )
        )::integer AS attr1,

        trim(
            split_part(
                split_part(
                    raw, 'attr2:', 2
                ),
                ',attr3:', 1
            )
        ) AS attr2,

        trim(
            split_part(
                split_part(
                    raw, 'attr3:', 2
                ),
                ',author_name:', 1
            )
        ) AS attr3,

        trim(
            split_part(
                split_part(
                    raw, 'author_name:', 2
                ),
                ',}:', 1
            )
        ) AS author_name

    FROM vozejkmap_raw;

It just splits the JSON data and creates table out of it according to the [VozejkMap.cz data specification](http://www.vozejkmap.cz/opendata/). Before going on we should create a table with location types to join their numeric codes to real names:

    CREATE TABLE location_type (
        id integer PRIMARY KEY,
        description varchar(255)
    );

    INSERT INTO location_type VALUES(1, 'Kultura');
    INSERT INTO location_type VALUES(2, 'Sport');
    INSERT INTO location_type VALUES(3, 'Instituce');
    INSERT INTO location_type VALUES(4, 'Jídlo a pití');
    INSERT INTO location_type VALUES(5, 'Ubytování');
    INSERT INTO location_type VALUES(6, 'Lékaři, lékárny');
    INSERT INTO location_type VALUES(7, 'Jiné');
    INSERT INTO location_type VALUES(8, 'Doprava');
    INSERT INTO location_type VALUES(9, 'Veřejné WC');
    INSERT INTO location_type VALUES(10, 'Benzínka');
    INSERT INTO location_type VALUES(11, 'Obchod');
    INSERT INTO location_type VALUES(12, 'Banka, bankomat');
    INSERT INTO location_type VALUES(13, 'Parkoviště');
    INSERT INTO location_type VALUES(14, 'Prodejní a servisní místa Škoda Auto');

Let's build some geometry column, constraints and indexes. And don't forget to get rid of all the mess (the `vozejkmap_raw` table).

    DROP TABLE vozejkmap_raw;
    ALTER TABLE vozejkmap ADD PRIMARY KEY(id);
    -- 4326 geometry is not very useful for measurements, I might get to that next time
    ALTER TABLE vozejkmap ADD COLUMN geom geometry(point, 4326);
    ALTER TABLE vozejkmap ADD CONSTRAINT loctype_fk FOREIGN KEY(location_type); REFERENCES location_type(id);

    UPDATE vozejkmap SET geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326);

**And here we are, ready to use our spatial data!**

Feel free to [grab the code](https://github.com/zimmicz/vozejkmap-to-postgis) at GitHub.
