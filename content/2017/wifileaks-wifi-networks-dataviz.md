Title: Wifileaks Wi-Fi Networks Dataviz
Date: 2017-05-02 18:30
Category: GIS
Tags: qgis, visualization
Image: https://www.zimmi.cz/posts/assets/wifileaks-wifi-networks-dataviz/brno.png

[Wifileaks](http://www.wifileaks.cz) is a project by Jakub Čížek aimed to map the Czech wi-fi networks with Android/iOS app. The data gathered by people using the app [is available to download](http://download.wifileaks.cz/data/wifileaks_raw_170416.tar.gz) and features ~&nbsp;90,000,000 records, each representing the position of the cellphone when connecting to the network. Just about perfect to craft some maps!

<div class="text-center"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/cr.png"/></div>

## Using PostgreSQL cstore_fdw

I ran out of disk space immediately after loading the dataset into the PostgreSQL database. After fiddling around I remembered that columnar store should be a bit space-friendlier than the old fashioned relational database. Thus, I installed the [cstore_fdw](https://github.com/citusdata/cstore_fdw) by Citus Data in just few steps.

    :::bash
    sudo apt install libprotobuf-c-dev libprotobuf-c1 protobuf-c-compiler postgresql-server-dev-9.6
    git clone git@github.com:citusdata/cstore_fdw.git
    PATH=/usr/bin/:$PATH make
    PATH=/usr/bin/:$PATH make install

    # when the cstore_fdw installation finishes, add the following line to your postgresql.conf and restart the database cluster
    shared_preload_libraries = 'cstore_fdw'

This makes [another FDW available]({filename}../2016/testing-postgresql-ogr-fdw.md) to you inside the PostgreSQL. The actual foreign server has to be created before loading the data into a foreign table.

    :::bash
    cat <<END | psql -qAt --no-psqlrc
	    CREATE SERVER cstore_server FOREIGN DATA WRAPPER cstore_fdw;
	    CREATE SCHEMA data_cstore;
	    CREATE FOREIGN TABLE data_cstore.wifi (
    		id integer,
		    mac text,
		    ssid text,
		    signal_strength numeric,
		    security integer,
            lat numeric,
            lon numeric,
            alt numeric,
            unixtime bigint,
            filename text
	    )
	    SERVER cstore_server
	    OPTIONS (compression 'pglz');
    END

The foreign table **is 3&times; smaller** than it's standard counterpart. However, this comes with some costs:

- neither `UPDATE` nor `DELETE` can be used
- no `CREATE INDEX`
- no `SERIAL`

To overcome these shortcomings I used `COPY` statement to spit out the slightly modified table and immediately loaded it back in.

    :::bash
    cat <<END | psql -qAt --no-psqlrc
	COPY (
		SELECT
			row_number() OVER (),
			mac,
			ssid,
			signal_strength,
			security,
			split_part(filename, '_', 2)::integer,
			to_timestamp(unixtime),
			ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat, alt), 4326), 32633)
		FROM data_cstore.wifi
		WHERE lon BETWEEN 0 AND 20
			AND lat BETWEEN 18 AND 84
	) TO '/tmp/wifileaks.db' WITH CSV DELIMITER ';'
    	DROP SCHEMA IF EXISTS data_cstore CASCADE;

    DROP SCHEMA data_cstore;
	CREATE SCHEMA data_cstore;
	CREATE FOREIGN TABLE data_cstore.wifi (
		id integer,
		mac text,
		ssid text,
		signal_strength numeric,
		security integer,
		userid integer,
		unixtime timestamp without time zone,
		geom geometry(POINTZ, 32633)
	)
	SERVER cstore_server
	OPTIONS (compression 'pglz');
    END

## Putting the networks on the map

<table>
    <tr>
        <td><a href="/posts/assets/wifileaks-wifi-networks-dataviz/brno.png"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/brno.png"></a></td>
        <td><a href="/posts/assets/wifileaks-wifi-networks-dataviz/praha.png"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/praha.png"></a></td>
        <td><a href="/posts/assets/wifileaks-wifi-networks-dataviz/olomouc.png"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/olomouc.png"></a></td>
    </tr>
    <tr>
        <td><a href="/posts/assets/wifileaks-wifi-networks-dataviz/plzen.png"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/plzen.png"></a></td>
        <td><a href="/posts/assets/wifileaks-wifi-networks-dataviz/ostrava.png"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/ostrava.png"></a></td>
        <td><a href="/posts/assets/wifileaks-wifi-networks-dataviz/hradec_kralove.png"><img src="/posts/assets/wifileaks-wifi-networks-dataviz/hradec_kralove.png"></a></td>
    </tr>
</table>

As mentioned, each row of data represents the cellphone's location when connecting to a wi-fi network. To get real wi-fi transmitter position, I calculated the average of location of each cellphone ever connected (although the signal strength should be taken into account here as well).

    :::sql
    CREATE UNLOGGED TABLE data_cstore.wifi_avg_loc AS
	SELECT
		row_number() OVER () id,
		mac,
		ST_SetSRID(ST_MakePoint(x, y), 32633) geom
	FROM (
		SELECT
			mac,
			AVG(ST_X(geom)) x,
			AVG(ST_Y(geom)) y
		FROM data_cstore.wifi_loc
		GROUP BY 1
	) a;
