Title: Twitter REST API Data Mining on OpenShift (Part II)
Date: 2015-12-6 12:25
Tags: javascript, openshift, twitter
Category: development

Last time I described [the setup of my OpenShift Twitter crawler]({filename}../2015/twitter-rest-api-data-mining-on-openshift.md) and let it running and downloading data. It's been more than two months since I started and I got interesting amount of data. I also made a simple ETL process to load it into my local PostGIS database, which I'd like to cover in this post.

## Extract data

Each day is written to the separate sqlite file with a name like `tw_day_D_M_YYYY`. `Bash` is used to gzip all the files before downloading them from OpenShift.

    :::bash
    #!/bin/bash

    ssh openshift << EOF
        cd app-root/data
        tar czf twitter.tar.gz *.db
    EOF

    scp openshift:/var/lib/openshift/55e487587628e1280b0000a9/app-root/data/twitter.tar.gz ./data
    cd data &&
    tar -xzf twitter.tar.gz &&
    cd -

    echo "Extract done"

## Transform data

The transformation part operates on downloaded files and merges them into one big CSV file. That's pretty straightforward. Note that's quite simple with sqlite flags, some `sed` and `tail` commands.

    :::bash
    #!/bin/bash

    rm -rf ./data/csv
    mkdir ./data/csv

    for db in ./data/*.db; do
        FILENAME=$(basename $db)
        DBNAME=${FILENAME%%.db}
        CSVNAME=$DBNAME.csv
        echo "$DBNAME to csv..."
        sqlite3 -header -csv $db "select * from $DBNAME;" > ./data/csv/$CSVNAME
    done

    cd ./data/csv
    touch tweets.csv
    echo $(sed -n 1p $(ls -d -1 *.csv | head -n 1)) > tweets.csv # get column names

    for csv in tw_*.csv; do
        echo $csv
        tail -n +2 $csv >> tweets.csv # get all lines without the first one
    done

## Load data

In the last step, the data is loaded with SQL `\copy` command.

    :::bash
    #!/bin/bash

    export PG_USE_COPY=YES

    DATABASE=mzi_dizertace
    SCHEMA=dizertace
    TABLE=tweets

    psql $DATABASE << EOF
        DROP TABLE IF EXISTS $SCHEMA.$TABLE;
        CREATE UNLOGGED TABLE $SCHEMA.$TABLE (id text, author text, author_id text, tweet text, created_at text, lon float, lat float, lang text);
        \copy $SCHEMA.$TABLE FROM 'data/csv/tweets.csv' CSV HEADER DELIMITER ','
        ALTER TABLE $SCHEMA.$TABLE ADD COLUMN wkb_geometry geometry(POINT, 4326);
        UPDATE $SCHEMA.$TABLE SET wkb_geometry = ST_SetSRID(ST_MakePoint(lon, lat), 4326);
        CREATE INDEX ${TABLE}_geom_idx ON $SCHEMA.$TABLE USING gist(wkb_geometry);
        COMMIT;
    EOF

## First statistics

Some interesting charts and numbers follow.

<p class="text-center"><img title="Top 100 Twitter users in the Czech Republic" src="{filename}/assets/twitter-rest-api-data-mining-on-openshift-part-ii/authors.png" class="img-responsive centered"></p>

<p class="text-center"><img title="When people tweet in the Czech Republic" src="{filename}/assets/twitter-rest-api-data-mining-on-openshift-part-ii/hours.png" class="img-responsive centered"></p>

<p class="text-center"><img title="Languages on Twitter in the Czech Republic" src="{filename}/assets/twitter-rest-api-data-mining-on-openshift-part-ii/languages.png" class="img-responsive centered"></p>
