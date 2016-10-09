Title: Installing PostGIS 2.2 with SFCGAL on Ubuntu-based OS
Date: 2015-10-29 22:00
Tags: postgresql, postgis, linux
Category: development

I've seen a bunch of questions on GIS StackExchange recently related to [SFCGAL](http://sfcgal.org/) extension for [PostGIS 2.2](http://postgis.net). Great news are it can be installed with one simple query `CREATE EXTENSION postgis_sfcgal`. Not so great news are you have to compile it from source for Ubuntu-based OS (14.04) as recent versions of required packages are not available in the repositories.

I tested my solution on elementary OS 0.3.1 based on Ubuntu 14.04. **And it works!** It installs PostgreSQL 9.4 from repositories together with GDAL and GEOS and some other libs PostGIS depends on. PostGIS itself, CGAL, Boost, MPFR and GMP are built from source.

Here comes the code (commented where needed).

    :::bash
    sudo -i
    echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" | tee -a /etc/apt/sources.list
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    apt-get update
    apt-get install -y postgresql-9.4 \
        postgresql-client-9.4 \
        postgresql-contrib-9.4 \
        libpq-dev \
        postgresql-server-dev-9.4 \
        build-essential \
        libgeos-c1 \
        libgdal-dev \
        libproj-dev \
        libjson0-dev \
        libxml2-dev \
        libxml2-utils \
        xsltproc \
        docbook-xsl \
        docbook-mathml \
        cmake \
        gcc \
        m4 \
        icu-devtools

    exit # leave root otherwise postgis will choke

    cd /tmp
    touch download.txt
    cat <<EOT >> download.txt
    https://gmplib.org/download/gmp/gmp-6.0.0a.tar.bz2
    https://github.com/Oslandia/SFCGAL/archive/v1.2.0.tar.gz
    http://www.mpfr.org/mpfr-current/mpfr-3.1.3.tar.gz
    http://downloads.sourceforge.net/project/boost/boost/1.59.0/boost_1_59_0.tar.gz
    https://github.com/CGAL/cgal/archive/releases/CGAL-4.6.3.tar.gz
    http://download.osgeo.org/postgis/source/postgis-2.2.0.tar.gz

    EOT

    cat download.txt | xargs -n 1 -P 8 wget # make wget a little bit faster

    tar xjf gmp-6.0.0a.tar.bz2
    tar xzf mpfr-3.1.3.tar.gz
    tar xzf v1.2.0.tar.gz
    tar xzf boost_1_59_0.tar.gz
    tar xzf CGAL-4.6.3.tar.gz
    tar xzf postgis-2.2.0.tar.gz

    CORES=$(nproc)

    if [[ $CORES > 1 ]]; then
        CORES=$(expr $CORES - 1) # be nice to your PC
    fi

    cd gmp-6.0.0
    ./configure && make -j $CORES && sudo make -j $CORES install

    cd ..
    cd mpfr-3.1.3
    ./configure && make -j $CORES && sudo make -j $CORES install

    cd ..
    cd boost_1_59_0
    ./bootstrap.sh --prefix=/usr/local --with-libraries=all && sudo ./b2 install # there might be some warnings along the way, don't panic
    echo "/usr/local/lib" | sudo tee /etc/ld.so.conf.d/boost.conf
    sudo ldconfig

    cd ..
    cd cgal-releases-CGAL-4.6.3
    cmake . && make -j $CORES && sudo make -j $CORES install

    cd ..
    cd SFCGAL-1.2.0/
    cmake . && make -j $CORES && sudo make -j $CORES install

    cd ..
    cd postgis-2.2.0
    ./configure \
        --with-geosconfig=/usr/bin/geos-config \
        --with-xml2config=/usr/bin/xml2-config \
        --with-projdir=/usr/share/proj \
        --with-libiconv=/usr/bin \
        --with-jsondir=/usr/include/json \
        --with-gdalconfig=/usr/bin/gdal-config \
        --with-raster \
        --with-topology \
        --with-sfcgal=/usr/local/bin/sfcgal-config && \
    make && make cheatsheets && sudo make install # deliberately one CPU only

    sudo -u postgres psql
    sudo -u postgres createdb spatial_template
    sudo -u postgres psql -d spatial_template -c "CREATE EXTENSION postgis;"
    sudo -u postgres psql -d spatial_template -c "CREATE EXTENSION postgis_topology;"
    sudo -u postgres psql -d spatial_template -c "CREATE EXTENSION postgis_sfcgal;"
    sudo -u postgres psql -d spatial_template -c "SELECT postgis_full_version();"