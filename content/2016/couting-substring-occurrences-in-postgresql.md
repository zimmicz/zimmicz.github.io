Title: Counting substring occurrences in PostgreSQL
Date: 2016-12-19 17:50
Category: SQL
Tags: sql, postgresql

I got to count occurrences of */* character today and found out no built-in function exists in PostgreSQL, so here's my shot at it. Pretty simple, yet useful.

    :::sql
    CREATE OR REPLACE FUNCTION how_many(IN text, IN varchar, OUT integer)
    RETURNS integer
    AS
    $how_many$
        SELECT length($1) - length(replace($1, $2, ''));
    $how_many$
    LANGUAGE SQL
    SECURITY DEFINER;

    -- SELECT how_many('test', 't'); -- returns number 2