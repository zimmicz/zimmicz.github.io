Title: Upgrading PostgreSQL 9.5 to PostgreSQL 9.6 with PostGIS
Date: 2017-03-01 09:30
Category: SQL
Tags: sql, postgresql

Thanks to `pg_upgrade` tool the PostgreSQL upgrade on Ubuntu is pretty straightforward. Different PostGIS versions might cause troubles though. This post covers PostgreSQL 9.5, PostGIS 2.2 to PostgreSQL 9.6, PostGIS 2.3 migration.

First of all, install the PostgreSQL 9.6 with PostGIS 2.3.

    :::bash
    apt install postgresql-9.6 postgresql-9.6-postgis-2.3

Mind that newly installed database cluster runs on port `5433`.

If you run `pg_upgrade` at this stage, it will fail with the following error.

    :::bash
    could not load library "$libdir/postgis_topology-2.2":
    ERROR:  could not access file "$libdir/postgis_topology-2.2": No such file or directory

`pg_upgrade` can't run the upgrade because PostGIS versions don't match. Install the PostGIS 2.3 for PostgreSQL 9.5 and update extensions in all your databases.

    :::bash
    apt install postgresql-9.5-postgis-2.3

    :::sql
    ALTER EXTENSION postgis UPDATE;

With both clusters using the same PostGIS version, the upgrade can begin. First, stop them with

    :::bash
    service postgresql stop

Then, run the actual `pg_upgrade` command as `postgres` user. Make sure the `pg_hba.conf` file is set to allow local connections.

    :::bash
    /usr/lib/postgresql/9.6/bin/pg_upgrade \
    -b /usr/lib/postgresql/9.5/bin/ \
    -B /usr/lib/postgresql/9.6/bin/ \
    -d /var/lib/postgresql/9.5/main \
    -D /var/lib/postgresql/9.6/main \
    -o ' -c config_file=/etc/postgresql/9.5/main/postgresql.conf' \
    -O ' -c config_file=/etc/postgresql/9.6/main/postgresql.conf'

The following result means the upgrade was smooth.

    :::bash
    Performing Consistency Checks
    -----------------------------
    Checking cluster versions                                   ok
    Checking database user is the install user                  ok
    Checking database connection settings                       ok
    Checking for prepared transactions                          ok
    Checking for reg* system OID user data types                ok
    Checking for contrib/isn with bigint-passing mismatch       ok
    Checking for roles starting with 'pg_'                      ok
    Creating dump of global objects                             ok
    Creating dump of database schemas
                                                                ok
    Checking for presence of required libraries                 ok
    Checking database user is the install user                  ok
    Checking for prepared transactions                          ok

    If pg_upgrade fails after this point, you must re-initdb the
    new cluster before continuing.

    Performing Upgrade
    ------------------
    Analyzing all rows in the new cluster                       ok
    Freezing all rows on the new cluster                        ok
    Deleting files from new pg_clog                             ok
    Copying old pg_clog to new server                           ok
    Setting next transaction ID and epoch for new cluster       ok
    Deleting files from new pg_multixact/offsets                ok
    Copying old pg_multixact/offsets to new server              ok
    Deleting files from new pg_multixact/members                ok
    Copying old pg_multixact/members to new server              ok
    Setting next multixact ID and offset for new cluster        ok
    Resetting WAL archives                                      ok
    Setting frozenxid and minmxid counters in new cluster       ok
    Restoring global objects in the new cluster                 ok
    Restoring database schemas in the new cluster
                                                                ok
    Copying user relation files
                                                                ok
    Setting next OID for new cluster                            ok
    Sync data directory to disk                                 ok
    Creating script to analyze new cluster                      ok
    Creating script to delete old cluster                       ok

    Upgrade Complete
    ----------------
    Optimizer statistics are not transferred by pg_upgrade so,
    once you start the new server, consider running:
        ./analyze_new_cluster.sh

    Running this script will delete the old cluster's data files:
        ./delete_old_cluster.sh

The old cluster can be removed and the new one switched back to port `5432`. Run `/usr/lib/postgresql/9.6/bin/vacuumdb -p 5433 --all --analyze-in-stages` to collect statistics.
