Title: PostgreSQL IN vs EXISTS
Date: 2015-10-09 09:00
Tags: sql
Category: development

Until recently, SQL `IN` and `EXISTS` were almost exactly the same to me. There is a significant difference both in execution plans and time of execution though, as I found out after not being able to speed up my workmate's query.

Assume two not-as-small-as-they-might-be tables:

    :::sql
    BEGIN;

    CREATE UNLOGGED TABLE test.small AS
    SELECT * FROM generate_series(0, 500000) id;

    CREATE UNLOGGED TABLE test.big AS
    SELECT (random() * 4000000)::integer id
    FROM generate_series(0, 4000000);

    COMMIT;

To find out what rows from `test.big` is missing in `test.small`, you'll use one of these queries:

    :::sql
    SELECT id
    FROM test.big
    WHERE id NOT IN (SELECT id FROM test.small);

                                QUERY PLAN
    -----------------------------------------------------------------------------------------
    Seq Scan on big  (cost=8463.01..42313.02 rows=1000000 width=4) (actual time=177.061..864.043 rows=1500894 loops=1)
        Filter: (NOT (hashed SubPlan 1))
        Rows Removed by Filter: 499107
        SubPlan 1
        ->  Seq Scan on small  (cost=0.00..7213.01 rows=500001 width=4) (actual time=0.045..34.727 rows=500001 loops=1)
        Total runtime: 904.413 ms
    (6 rows)


    SELECT id
    FROM test.big
    WHERE NOT EXISTS (
        SELECT 1
        FROM test.small
        WHERE test.big.id = test.small.id
    );
                                QUERY PLAN
    -----------------------------------------------------------------------------------------
    Hash Anti Join  (cost=15417.02..82100.58 rows=955189 width=4) (actual time=100.257..1240.343 rows=1500894 loops=1)
        Hash Cond: (big.id = small.id)
        ->  Seq Scan on big  (cost=0.00..28850.01 rows=2000001 width=4) (actual time=0.016..125.024 rows=2000001 loops=1)
        ->  Hash  (cost=7213.01..7213.01 rows=500001 width=4) (actual time=100.068..100.068 rows=500001 loops=1)
            Buckets: 65536  Batches: 2  Memory Usage: 8800kB
            ->  Seq Scan on small  (cost=0.00..7213.01 rows=500001 width=4) (actual time=0.011..35.543 rows=500001 loops=1)
    Total runtime: 1280.609 ms

That's not a significant difference in time execution, is it?

What if you want to find out what rows from `test.small` is missing in `test.big`?

    :::sql
    SELECT id
    FROM test.small
    WHERE id NOT IN (SELECT id FROM test.big);

                                    QUERY PLAN
    ---------------------------------------------------------------------------
    Seq Scan on small  (cost=0.00..12915788669.52 rows=250000 width=4)
        Filter: (NOT (SubPlan 1))
        SubPlan 1
        ->  Materialize  (cost=0.00..46663.01 rows=2000001 width=4)
            ->  Seq Scan on big  (cost=0.00..28850.01 rows=2000001 width=4)
    (5 rows)


    SELECT id
    FROM test.small
    WHERE NOT EXISTS (
        SELECT 1
        FROM test.big
        WHERE test.big.id = test.small.id
    );

                                   QUERY PLAN
    -------------------------------------------------------------------------
    Hash Anti Join  (cost=61663.02..180597.23 rows=1 width=4)
        Hash Cond: (small.id = big.id)
        ->  Seq Scan on small  (cost=0.00..7213.01 rows=500001 width=4)
        ->  Hash  (cost=28850.01..28850.01 rows=2000001 width=4)
            ->  Seq Scan on big  (cost=0.00..28850.01 rows=2000001 width=4)
    (5 rows)

It took me ~750 ms to get the result with `EXISTS` expression. I kept `IN` running whole night with no result. I'm not really sure why `IN` is so much slower, it might be caused by checks for `NULL` values. The speed is also related to the size of the subquery, thus the difference when tables were switched.

`LEFT JOIN` can be used to achieve the same result, I find its syntax less obvious though.

No indexes were built this time, I know they don't help the `IN` performance at all from my previous tests. Tested with PostgreSQL 9.3.9.