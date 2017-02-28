Title: Executing dynamic SQL query right away
Date: 2017-02-28 20:30
Category: SQL
Tags: sql, postgresql

PostgreSQL 9.6 comes with a handy `psql` command called `\gexec` that *sends the current query input buffer to the server and treats the result as a SQL statement to be executed* (right, whatever). What that means is that instead of doing this

    :::bash
    psql -c "SELECT 'DROP TABLE ' || tablename FROM information_schema.tables WHERE table_name LIKE '%to_be_dropped%" | psql

you'll do that

    :::sql
    SELECT 'DROP TABLE ' || tablename FROM information_schema.tables WHERE table_name LIKE '%to_be_dropped%'\gexec

Brilliant.
