Title: Looking for the Next Row with PostgreSQL
Date: 2016-1-23 16:45
Tags: postgresql, sql
Category: SQL

## Using JOIN clause

All my GIS life I've been using a simple `JOIN` clause to find a row with an `id = previous_id + 1`. In other words, imagine a simple table with no indices:

    :::sql
    CREATE TABLE test (id integer);
    INSERT INTO test SELECT i FROM generate_series(1,10000000) i;

Let's retrieve next row for each row in that table:

    :::sql
    SELECT a.id, b.id
    FROM test a
    LEFT JOIN test b ON (a.id + 1 = b.id); -- note the LEFT JOIN is needed to get the last row as well

Execution plan looks like this:

    :::sql
    Hash Join  (cost=311087.17..953199.41 rows=10088363 width=8) (actual time=25440.770..79591.869 rows=10000000 loops=1)
       Hash Cond: ((a.id + 1) = b.id)
       ->  Seq Scan on test a  (cost=0.00..145574.63 rows=10088363 width=4) (actual time=0.588..10801.584 rows=10000001 loops=1)
       ->  Hash  (cost=145574.63..145574.63 rows=10088363 width=4) (actual time=25415.282..25415.282 rows=10000001 loops=1)
             Buckets: 16384  Batches: 128  Memory Usage: 2778kB
             ->  Seq Scan on test b  (cost=0.00..145574.63 rows=10088363 width=4) (actual time=0.422..11356.108 rows=10000001 loops=1)
     Planning time: 0.155 ms
     Execution time: 90134.248 ms

If we add an index with `CREATE INDEX ON test (id)`, the plan changes:

    :::sql
    Merge Join  (cost=0.87..669369.85 rows=9999844 width=8) (actual time=0.035..56219.294 rows=10000001 loops=1)
       Merge Cond: (a.id = b.id)
       ->  Index Only Scan using test_id_idx on test a  (cost=0.43..259686.10 rows=9999844 width=4) (actual time=0.015..11101.937 rows=10000001 loops=1)
             Heap Fetches: 0
       ->  Index Only Scan using test_id_idx on test b  (cost=0.43..259686.10 rows=9999844 width=4) (actual time=0.012..11827.895 rows=10000001 loops=1)
             Heap Fetches: 0
     Planning time: 0.244 ms
     Execution time: 65973.421 ms

Not bad.

## Using window function

[Window functions](http://www.postgresql.org/docs/9.4/static/functions-window.html) are real fun. They're great if you're doing counts, sums or ranks by groups. And, to my surprise, they're great in finding next rows as well.

With the same `test` table, we retrieve next row for each row with the following query:

    :::sql
    SELECT id, lead(id) OVER (ORDER BY id)
    FROM test.test;

How does that score without an index? Better than the `JOIN` clause.

    :::sql
    WindowAgg  (cost=1581246.90..1756294.50 rows=10002720 width=4) (actual time=28785.388..63819.071 rows=10000001 loops=1)
       ->  Sort  (cost=1581246.90..1606253.70 rows=10002720 width=4) (actual time=28785.354..40117.899 rows=10000001 loops=1)
             Sort Key: id
             Sort Method: external merge  Disk: 136848kB
             ->  Seq Scan on test  (cost=0.00..144718.20 rows=10002720 width=4) (actual time=0.020..10797.961 rows=10000001 loops=1)
     Planning time: 0.242 ms
     Execution time: 73391.024 ms

And it works even better if indexed. It's actually ~1,5&times; faster than the `JOIN` way.

    :::sql
    WindowAgg  (cost=0.43..409770.03 rows=10002720 width=4) (actual time=0.087..35647.815 rows=10000001 loops=1)
       ->  Index Only Scan using test_id_idx on test  (cost=0.43..259729.23 rows=10002720 width=4) (actual time=0.059..11310.879 rows=10000001 loops=1)
             Heap Fetches: 0
     Planning time: 0.247 ms
     Execution time: 45388.202 ms

It reads well and the purpose of such a query is pretty obvious.