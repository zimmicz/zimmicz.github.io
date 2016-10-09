Title: PostGIS: Rectangular Grid Creation
Date: 2015-03-24 17:47
Category: SQL
Tags: postgresql, postgis

Creating a rectangular grid to cover a given extent with same sized cells is one of the basic GIS tasks I've had to solve several times so far. I used QGIS or some Python to give me a bunch of `INSERT` statements to run in PostGIS database, now I've come with a final solution at last.

    CREATE OR REPLACE FUNCTION cm_grid(
        blx float8, -- bottom left x coordinate
        bly float8, -- bottom left y coordinate
        trx float8, -- top right x coordinate
        try float8, -- top right y coordinate
        xsize float8, -- cell width
        ysize float8, -- cell height
        srid integer DEFAULT 5514,
        OUT col varchar,
        OUT "row" varchar,
        OUT geom geometry
    ) RETURNS SETOF record AS
    $$
    DECLARE
        width float8; -- total area width
        height float8; -- total area height
        cols integer;
        rows integer;
    BEGIN
        width  := @($1 - $3); -- absolute value
        height := @($2 - $4); -- absolute value
        cols   := ceil(width / xsize);
        rows   := ceil(height / ysize);
        RETURN QUERY
            SELECT
                cast(
                    lpad((i)::varchar,
                    CASE WHEN
                        char_length(rows::varchar) > char_length(cols::varchar)
                            THEN  char_length(rows::varchar)
                            ELSE char_length(cols::varchar)
                    END,
                    '0')
                    AS varchar
                ) AS row,
                cast(
                    lpad((j)::varchar,
                    CASE WHEN
                        char_length(rows::varchar) > char_length(cols::varchar)
                            THEN  char_length(rows::varchar)
                            ELSE char_length(cols::varchar)
                    END,
                    '0') AS varchar
                ) AS col,
                ST_SetSRID(
                    ST_GeomFromText(
                        'POLYGON((' ||
                            array_to_string(
                                ARRAY[i * xsize + blx, j * ysize + bly],
                                ' '
                            ) || ',' ||
                            array_to_string(
                                ARRAY[i * xsize + blx, (j+1) * ysize + bly],
                                ' '
                            ) || ',' ||
                            array_to_string(
                                ARRAY[(i+1) * xsize + blx, (j+1) * ysize + bly],
                                ' '
                            ) || ',' ||
                            array_to_string(
                                ARRAY[(i+1) * xsize + blx, j * ysize + bly],
                                ' '
                            ) || ',' ||
                            array_to_string(
                                ARRAY[i * xsize + blx, j * ysize + bly],
                                ' '
                            ) || '
                        ))'
                    )
                , srid) AS geom
            FROM
                generate_series(0, cols) AS i,
                generate_series(0, rows) AS j;
    END;
    $$
    LANGUAGE plpgsql;

And you call it like this:

    CREATE TABLE grid AS
    SELECT *
    FROM cm_grid(-675593.69, -1057711.19, -672254.69, -1054849.19, 333.47, 333.47);

Few notes:

- it takes bounding box coordinates (bottom left, top right) for an extent,
- followed by cell width and height,
- and optional SRID (defaults to 5514 which is Czech national grid),
- each cell is indexed with `row` and `col` number

The messy `CASE` statement makes sure both `row` and `col` are of the same length. I used `array_to_string` for better readability. It might not be the fastest way, didn't do any benchmarks.
