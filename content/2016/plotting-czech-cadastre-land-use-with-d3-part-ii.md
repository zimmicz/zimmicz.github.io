Title: Plotting the Czech Cadastre Land Use with d3: Data Transformation (part II)
Date: 2016-11-14 18:30
Category: data
Tags: javascript, d3, postgresql, svg
URL: 2016/plotting-czech-cadastre-land-use-with-d3-data-transformation-part-ii
save_as: 2016/plotting-czech-cadastre-land-use-with-d3-data-transformation-part-ii/index.html

This post is the second part of the series summarizing the process of visualizing landuse data with bash, PostgreSQL and d3.js. Read other parts:

1. [Plotting the Czech Cadastre Land Use with d3: Data Extraction (part I)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-i.md)
2. you're reading it now
3. [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part III)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-iii.md)

## ETL process
Before the d3 viz can be crafted, it's necessary to:

1. extract CSV data from the URLs provided via the Atom feed
2. transform those data into a relational database, do some math
3. load data into a d3.js viz
4. profit (as usual)

### Extract
See [Plotting the Czech Cadastre Land Use with d3: Data Extraction (part I)]({filename}/2016/plotting-czech-cadastre-landuse-with-d3-part-i.md).

### Transform

Last time, I extracted the data from multiple CSV files to separate PostgreSQL tables named by `data_YYYYMMDD` pattern. My current goal is to transform it into the one big `data` table, where each row represents one cadastral area. Here's what I'm trying to achieve:

	:::bash
	-[ RECORD 1 ]----------+----------------------------------
	ku_kod                 | 600881
	ku_nazev               | Bantice
	celkova_vymera         | {3763255,3763255,3763256,3763256}
	celkovy_pocet_parcel   | {670,668,664,667}
	chmelnice_pp           | {0,0,0,0}
	chmelnice_pp_r         | {0.00,0.00,0.00,0.00}
	chmelnice_v            | {0,0,0,0}
	chmelnice_v_avg        | {0,0,0,0}
	chmelnice_v_r          | {0.00,0.00,0.00,0.00}
	lesni_pozemek_pp       | {25,25,25,25}
	lesni_pozemek_pp_r     | {3.73,3.74,3.77,3.75}
	lesni_pozemek_v        | {83879,83879,83879,83879}
	lesni_pozemek_v_avg    | {3355,3355,3355,3355}
	lesni_pozemek_v_r      | {2.23,2.23,2.23,2.23}
	orna_puda_pp           | {88,88,89,89}
	orna_puda_pp_r         | {13.13,13.17,13.40,13.34}
	orna_puda_v            | {3066230,3066230,3066230,3066230}
	orna_puda_v_avg        | {34844,34844,34452,34452}
	orna_puda_v_r          | {81.48,81.48,81.48,81.48}
	ostatni_plocha_pp      | {201,199,199,201}
	ostatni_plocha_pp_r    | {30.00,29.79,29.97,30.13}
	ostatni_plocha_v       | {283468,283468,283468,284562}
	ostatni_plocha_v_avg   | {1410,1424,1424,1416}
	ostatni_plocha_v_r     | {7.53,7.53,7.53,7.56}
	ovocny_sad_pp          | {0,0,0,0}
	ovocny_sad_pp_r        | {0.00,0.00,0.00,0.00}
	ovocny_sad_v           | {0,0,0,0}
	ovocny_sad_v_avg       | {0,0,0,0}
	ovocny_sad_v_r         | {0.00,0.00,0.00,0.00}
	ttp_pp                 | {44,44,44,45}
	ttp_pp_r               | {6.57,6.59,6.63,6.75}
	ttp_v                  | {49002,49002,49002,47908}
	ttp_v_avg              | {1114,1114,1114,1065}
	ttp_v_r                | {1.30,1.30,1.30,1.27}
	vinice_pp              | {1,1,1,1}
	vinice_pp_r            | {0.15,0.15,0.15,0.15}
	vinice_v               | {106178,106178,106178,106178}
	vinice_v_avg           | {106178,106178,106178,106178}
	vinice_v_r             | {2.82,2.82,2.82,2.82}
	vodni_plocha_pp        | {23,23,23,23}
	vodni_plocha_pp_r      | {3.43,3.44,3.46,3.45}
	vodni_plocha_v         | {27877,27877,27877,27877}
	vodni_plocha_v_avg     | {1212,1212,1212,1212}
	vodni_plocha_v_r       | {0.74,0.74,0.74,0.74}
	zahrada_pp             | {115,115,115,115}
	zahrada_pp_r           | {17.16,17.22,17.32,17.24}
	zahrada_v              | {77381,77381,77353,77353}
	zahrada_v_avg          | {673,673,673,673}
	zahrada_v_r            | {2.06,2.06,2.06,2.06}
	zastavena_plocha_pp    | {173,173,168,168}
	zastavena_plocha_pp_r  | {25.82,25.90,25.30,25.19}
	zastavena_plocha_v     | {69240,69240,69269,69269}
	zastavena_plocha_v_avg | {400,400,412,412}
	zastavena_plocha_v_r   | {1.84,1.84,1.84,1.84}

Several stats were calculated for each land use category (vinice &rarr; vineyard, ovocny_sad &rarr; orchard, ...):

* `v_r` suffix stands for land use area ratio
* `pp_r` suffix stands for land use parcel count ratio
* `v_avg` stands for average parcel area

All statistical columns are kept as PostgreSQL `ARRAY`s, ordered by dates (very handy for the future d3.js viz by the way).

>	Note that since the `FULL OUTER JOIN` is needed in the next step, SQLite can't be used. Pity though.

The whole transformation bash script is the plain:

	:::bash
	#!/bin/bash

	psql -qAt --no-psqlrc -f transform.sql | psql -qAt --no-psqlrc

The `transform.sql` file is used to build the dynamic SQL query, which - once built - is piped to another `psql` command. I admit, pipes are super awesome.

	:::sql
	WITH tables AS (
	-- FULL OUTER JOIN all the data_YYYYMMDD tables
    SELECT
        table_name,
        table_schema,
        'd' || id tbl,
        CASE WHEN id = 1
            THEN table_schema || '.' || table_name || ' d' || id
            ELSE 'FULL OUTER JOIN ' || table_schema || '.' || table_name || ' d' || id || ' ON (d1.ku_kod = d' || id || '.ku_kod)'
        END tbl_join
    FROM (
        SELECT
            table_name,
            table_schema,
            row_number() OVER (ORDER BY table_name) id
        FROM information_schema.tables
        WHERE table_name LIKE 'data_%'
            AND table_type = 'BASE TABLE'
            AND table_schema = 'public'
    ) a
	)
	-- create data table with the correct values order for each statistical column
	-- note that the whole process would crash if d1.ku_kod would be NULL -> @todo fix me
	SELECT 'DROP TABLE IF EXISTS data;
		CREATE TABLE data AS
		SELECT d1.ku_kod, d1.ku_nazev,'
	UNION ALL
	SELECT
	    array_to_string(array_agg(r), ', ') r
	FROM (
	    SELECT
		'ARRAY[' || array_to_string(array_agg(tables.tbl || '.' || columns.column_name ORDER BY tables.table_name), ', ') || ']' || ' ' || columns.column_name r
	    FROM tables
	    JOIN (
		SELECT
		    table_schema,
		    table_name,
		    column_name
		FROM information_schema.columns
		WHERE column_name NOT LIKE 'ku_%'
		ORDER BY ordinal_position
	    ) columns
		ON (tables.table_name = columns.table_name AND columns.table_schema = tables.table_schema)
	    GROUP BY columns.column_name
	) a
	UNION ALL
	SELECT 'FROM'
	UNION ALL
	SELECT tbl_join FROM tables;

`psql -qAt --no-psqlrc -f transform.sql` builds the actual query from the query above, `| psql -qAt --no-psqlrc` sends it to the database again. This part was really fun to implement!

I'm still considering to store diff values instead of absolute values in those `ARRAY`s - that would save some serious bandwidth!

## Load
See [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part III)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-iii.md).
