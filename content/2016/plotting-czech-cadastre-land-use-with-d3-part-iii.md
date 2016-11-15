Title: Plotting the Czech Cadastre Land Use with d3: Data Load (part III)
Date: 2016-11-15 18:30
Category: data
Tags: postgresql, d3, javascript, svg
URL: 2016/plotting-czech-cadastre-land-use-with-d3-data-load-part-iii/
save_as: 2016/plotting-czech-cadastre-land-use-with-d3-data-load-part-iii/index.html

This post is the second part of the series summarizing the process of visualizing landuse data with bash, PostgreSQL and d3.js. Read other parts:

1. [Plotting the Czech Cadastre Land Use with d3: Data Extraction (part I)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-i.md)
2. [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part II)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-ii.md)
3. you're reading it now

## ETL process
Before the d3 viz can be crafted, it's necessary to:

1. extract CSV data from the URLs provided via the Atom feed
2. transform those data into a relational database, do some math
3. load data into a d3.js viz
4. profit (as usual)

### Extract
See [Plotting the Czech Cadastre Land Use with d3: Data Extraction (part I)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-i.md).

### Transform

See [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part II)]({filename}../2016/plotting-czech-cadastre-land-use-with-d3-part-ii.md).

## Load

Thanks to the way I transformed the data, the whole load is done with simple

	:::bash
	#!/bin/bash

	touch ./data/data.js
	echo "let data =" > ./data/data.js

	(
	cat << EOF | psql -qAt --no-psqlrc
	    SELECT
	    array_to_json(array_agg(row_to_json(r)))
	    FROM (
		SELECT *
		FROM data
	    ) r
	EOF
	) >> ./data/data.js

That's the whole ETL process! Next time, I'll cover the d3.js viz.