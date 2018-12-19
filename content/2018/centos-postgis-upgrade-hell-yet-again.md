Title: CentOS PostGIS Upgrade Hell... Yet Again
Date: 2018-12-19 10:00
Category: SQL
Tags: postgresql,postgis
URL: 2018/centos-postgis-upgrade-hell-yet-again
save_as: 2018/centos-postgis-upgrade-hell-yet-again/index.html

[PostGIS upgrades used to be a nightmare](https://www.zimmi.cz/posts/2017/upgrading-postgresql-95-to-postgresql-96-with-postgis/). Broken dependencies, version mismatches, you name it. Upgrading PostgreSQL 10 with PostGIS 2.4 to PostgreSQL 11 on CentOS has been my mission impossible for two days. And it doesn't seem to come to an end.

## What? Why?

We're running fairly large spatially enabled PostgreSQL 10 database cluster. To keep up with pretty fast development, I was hoping to `pg_upgrade` it to PostgreSQL 11.

## Tried and failed
I've been trying different upgrade strategies with PostgreSQL 11 already running to no avail. Here comes the list.

### Install PostGIS 2.4 to PostgreSQL 11 and pg_upgrade

    :::bash
    yum install postgis24_11
    systemctl stop postgresql-11

    su postgres
    /usr/pgsql-11/bin/pg_upgrade \
      --check \
      -b /usr/pgsql-10/bin/ -B /usr/pgsql-11/bin/ \
      -d /var/lib/pgsql/10/data -D /var/lib/pgsql/11/data \
      --link \
      -U root \
      -o ' -c config_file=/var/lib/pgsql/10/data/postgresql.conf' -O ' -c config_file=/var/lib/pgsql/11/data/postgresql.conf'

This results in:

> Your installation references loadable libraries that are missing from the
> new installation.  You can add these libraries to the new installation,
> or remove the functions using them from the old installation.  A list of
> problem libraries is in the file:
>    loadable_libraries.txt

`loadable_libraries.txt` says the following:

    :::bash
    could not load library "$libdir/postgis-2.4": ERROR:  could not load library "/usr/pgsql-11/lib/postgis-2.4.so": /usr/pgsql-11/lib/postgis-2.4.so: undefined symbol: geod_polygon_init

Duckduckgoing I found the related [PostgreSQL mailing list thread](https://www.postgresql.org/message-id/15450-a3638dc978caa94d@postgresql.org).

### Build and install PostGIS 2.4 from source to PostgreSQL 11 and pg_upgrade
The bug report says there's something wrong with `proj4` version, so I chose `proj49` and `geos37`.

    ::bash
    yum install proj49 proj49-devel
    wget https://download.osgeo.org/postgis/source/postgis-2.4.6.tar.gz
    tar -xzvf postgis-2.4.6.tar.gz
    cd postgis-2.4.6

    ./configure \
      --with-pgconfig=/usr/pgsql-11/bin/pg_config \
      --with-geosconfig=/usr/geos37/bin/geos-config \
      --with-projdir=/usr/proj49/

    make && make install

`CREATE EXTENSION postgis` fails with `could not load library "/usr/pgsql-11/lib/postgis-2.4.so": /usr/pgsql-11/lib/postgis-2.4.so: undefined symbol: geod_polygon_init`. Oh my.

### Install PostGIS 2.5 to PostgreSQL 10 and pg_upgrade
Running out of ideas, I tried to install PostGIS 2.5 to our PostgreSQL 10 cluster and pg_upgrade.

    ::bash
    yum install postgis25_10

The resulting error appeared almost instantly:

    ::bash
    Transaction check error:
    file /usr/pgsql-10/bin/shp2pgsql-gui from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/lib/liblwgeom.so from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/lib/postgis-2.4.so from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/address_standardizer.control from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/address_standardizer.sql from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/address_standardizer_data_us.control from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/address_standardizer_data_us.sql from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/postgis.control from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/postgis_sfcgal.control from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/postgis_tiger_geocoder.control from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64
    file /usr/pgsql-10/share/extension/postgis_topology.control from install of postgis25_10-2.5.1-1.rhel7.x86_64 conflicts with file from package postgis24_10-2.4.5-1.rhel7.x86_64

What the&hellip;

### Build and install PostGIS 2.5 from source to PostgreSQL 10 and pg_upgrade

    ::bash
    wget https://download.osgeo.org/postgis/source/postgis-2.5.1.tar.gz
    tar -xzvf postgis-2.5.1.tar.gz
    cd postgis-2.5.1

    ./configure \
      --with-pgconfig=/usr/pgsql-10/bin/pg_config \
      --with-geosconfig=/usr/geos37/bin/geos-config

    make && make install

`CREATE EXTENSION postgis` fails with `ERROR:  could not load library "/usr/pgsql-10/lib/postgis-2.5.so": /usr/pgsql-10/lib/postgis-2.5.so: undefined symbol: GEOSFrechetDistanceDensify`. Again? Really?

`GEOSFrechetDistanceDensify` was added in GEOS 3.7 (linked in `./configure`), yet `ldd /usr/pgsql-10/lib/postgis-2.5.so` says:

    ::bash
    linux-vdso.so.1 =>  (0x00007ffd4c5fa000)
    libgeos_c.so.1 => /usr/geos36/lib64/libgeos_c.so.1 (0x00007f68ddf5a000)
    libproj.so.0 => /lib64/libproj.so.0 (0x00007f68ddd07000)
    libjson-c.so.2 => /lib64/libjson-c.so.2 (0x00007f68ddafc000)
    libxml2.so.2 => /lib64/libxml2.so.2 (0x00007f68dd792000)
    libm.so.6 => /lib64/libm.so.6 (0x00007f68dd48f000)
    libSFCGAL.so.1 => /lib64/libSFCGAL.so.1 (0x00007f68dc9c0000)
    libc.so.6 => /lib64/libc.so.6 (0x00007f68dc5f3000)
    libgeos-3.6.3.so => /usr/geos36/lib64/libgeos-3.6.3.so (0x00007f68dc244000)
    libstdc++.so.6 => /lib64/libstdc++.so.6 (0x00007f68dbf3d000)
    libgcc_s.so.1 => /lib64/libgcc_s.so.1 (0x00007f68dbd27000)
    libdl.so.2 => /lib64/libdl.so.2 (0x00007f68dbb22000)
    libz.so.1 => /lib64/libz.so.1 (0x00007f68db90c000)
    liblzma.so.5 => /lib64/liblzma.so.5 (0x00007f68db6e6000)
    /lib64/ld-linux-x86-64.so.2 (0x000055960f119000)
    libCGAL.so.11 => /usr/lib64/libCGAL.so.11 (0x00007f68db4bd000)
    libCGAL_Core.so.11 => /usr/lib64/libCGAL_Core.so.11 (0x00007f68db284000)
    libmpfr.so.4 => /usr/lib64/libmpfr.so.4 (0x00007f68db029000)
    libgmp.so.10 => /usr/lib64/libgmp.so.10 (0x00007f68dadb0000)
    libboost_date_time-mt.so.1.53.0 => /usr/lib64/libboost_date_time-mt.so.1.53.0 (0x00007f68dab9f000)
    libboost_thread-mt.so.1.53.0 => /usr/lib64/libboost_thread-mt.so.1.53.0 (0x00007f68da988000)
    libboost_system-mt.so.1.53.0 => /usr/lib64/libboost_system-mt.so.1.53.0 (0x00007f68da783000)
    libboost_serialization-mt.so.1.53.0 => /usr/lib64/libboost_serialization-mt.so.1.53.0 (0x00007f68da517000)
    libpthread.so.0 => /lib64/libpthread.so.0 (0x00007f68da2fa000)
    librt.so.1 => /usr/lib64/librt.so.1 (0x00007f68da0f2000)

I'm nearly desperate after spending two days trying to break through. I have ~ 300 GB of PostgreSQL data to migrate to the current version and there seems to be no possible way to do it in CentOS.

One more thing to note: using `yum install postgis25_11` and `CREATE EXTENSION postgis` in v11 database fails with the exact same error like the one above. I really enjoy working with PostgreSQL and PostGIS, yet there's hardly something I fear more than trying to upgrade those two things together.

