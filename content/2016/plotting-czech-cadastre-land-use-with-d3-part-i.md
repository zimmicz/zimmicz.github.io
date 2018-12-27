Title: Plotting the Czech Cadastre Land Use with d3: Data Extraction (part I)
Date: 2016-11-13 18:30
Category: data
Tags: javascript, d3, postgresql, svg
URL: 2016/plotting-czech-cadastre-land-use-with-d3-data-extraction-part-i
save_as: 2016/plotting-czech-cadastre-land-use-with-d3-data-extraction-part-i/index.html

This post is the first part of the upcoming series summarizing the process of visualizing landuse data with bash, PostgreSQL and d3.js. Read other parts:

1. you're reading it now
2. [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part II)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-ii.md)
3. [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part III)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-iii.md)

[Czech Office for Surveying, Mapping and Cadastre](http://cuzk.cz/en) has recently published lot of data via [Atom feed](http://atom.cuzk.cz). There's pretty small and a bit boring dataset included, featuring quarterly updated landuse-related values for all 13,091 cadastral areas:

* absolute number of land lots within given category (arable land, forests, etc.)
* absolute area of land lots within given category

Data are published as CSV files linked from the Atom feed. Sadly, they come windows-1250 encoded, using Windows line endings, with trailing semicolons and header rows using diacritics.

## ETL process
Before the d3 viz can be crafted, it's necessary to:

1. extract CSV data from the URLs provided via the Atom feed
2. transform those data into a relational database, do some math
3. load data into a d3.js viz
4. profit (as usual)

### Extract
	:::bash
	#!/bin/bash
	# extract.sh -f YYYYMMDD

	while [[ $# -gt 1 ]]
	do
	key="$1"

	case $key in
	    -f|--file)
	    FILE="$2"
	    shift # past argument
	    ;;
	    *)
		    # unknown option
	    ;;
	esac
	shift # past argument or value
	done

	URL=http://services.cuzk.cz/sestavy/UHDP/UHDP-
	CSVFILE=$FILE.csv
	CSVUTF8FILE=${CSVFILE%.*}.utf.csv
	URL+=$CSVFILE

	echo "downloading $URL"
	wget -q $URL -O $CSVFILE

	if [[ $? != 0 ]]; then
	    rm -f $CSVFILE
	    echo "download failed"
	    exit
	fi

	echo "converting to utf-8"
	iconv -f WINDOWS-1250 -t UTF-8 $CSVFILE -o $CSVUTF8FILE && \
	echo "modifying ${FILE}"
	sed -i 's/^M$//' $CSVUTF8FILE && \
	sed -i 's/\r$//' $CSVUTF8FILE && \
	sed -i 's/;*$//g' $CSVUTF8FILE && \
	sed -i '1d' $CSVUTF8FILE

	echo "importing to database"
	sed -e "s/\${DATE}/$FILE/g" extract.sql | psql -qAt --no-psqlrc

	rm $CSVFILE $CSVUTF8FILE

This script downloads CSV file, deals with all the pitfalls mentioned above and, when done, `copy` command within `extract.sql` loads the data into a `data_YYYYMMDD` table. Putting all the files into the one table would have saved me a lot of transformation SQL, yet it didn't feel quite right though.

## Transform
See [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part II)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-ii.md).

## Load
See [Plotting the Czech Cadastre Land Use with d3: Data Transformation (part III)]({filename}/2016/plotting-czech-cadastre-land-use-with-d3-part-iii.md).
