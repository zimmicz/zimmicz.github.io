Title: PostgreSQL Development History Revealed with PostgreSQL
Date: 2017-08-09 19:00
Category: SQL
Tags: postgresql, python
Image: https://www.zimmi.cz/posts/assets/postgresql-development-history-revealed-with-postgresql/plot2.png

I spend a lot of time reading [PostgreSQL docs](https://www.postgresql.org/docs/manuals/). It occurred to me just a few weeks ago that those versioned manuals are great opportunity to get an insight into PostgreSQL development history. Using PostgreSQL, of course.

## TOP 5 functions with the most verbose docs in each version

    :::sql
    SELECT
        version,
        string_agg(func, ' | ' ORDER BY letter_count DESC)
    FROM (
        SELECT
            version,
            func,
            letter_count,
            row_number() OVER (PARTITION BY version ORDER BY letter_count DESC)
        FROM postgresql_development.data
    ) a
    WHERE row_number <= 10
    GROUP BY version
    ORDER BY version DESC

Seems like a huge comeback for `CREATE TABLE`.

| VERSION | 1st | 2nd | 3rd | 4th | 5th |
|-----|----------------|----------------|----------------|----------------|----------------------------|
| 10.0 |  CREATE TABLE  |  ALTER TABLE  |  REVOKE  |  GRANT  |  SELECT  |
| 9.6 |  REVOKE  |  ALTER TABLE  |  GRANT  |  CREATE TABLE  |  SELECT  |
| 9.5 |  REVOKE  |  ALTER TABLE  |  GRANT  |  CREATE TABLE  |  SELECT  |
| 9.4 |  REVOKE  |  GRANT  |  ALTER TABLE  |  CREATE TABLE  |  SELECT  |
| 9.3 |  REVOKE  |  GRANT  |  CREATE TABLE  |  ALTER TABLE  |  ALTER DEFAULT PRIVILEGES  |
| 9.2 |  REVOKE  |  GRANT  |  CREATE TABLE  |  ALTER TABLE  |  ALTER DEFAULT PRIVILEGES  |
| 9.1 |  REVOKE  |  GRANT  |  CREATE TABLE  |  ALTER TABLE  |  ALTER DEFAULT PRIVILEGES  |
| 9.0 |  REVOKE  |  GRANT  |  CREATE TABLE  |  ALTER TABLE  |  ALTER DEFAULT PRIVILEGES  |
| 8.4 |  REVOKE  |  GRANT  |  CREATE TABLE  |  ALTER TABLE  |  SELECT  |
| 8.3 |  REVOKE  |  CREATE TABLE  |  GRANT  |  ALTER TABLE  |  COMMENT  |
| 8.2 |  REVOKE  |  CREATE TABLE  |  GRANT  |  ALTER TABLE  |  SELECT  |
| 8.1 |  REVOKE  |  CREATE TABLE  |  GRANT  |  ALTER TABLE  |  SELECT  |
| 8 |  CREATE TABLE  |  REVOKE  |  GRANT  |  SELECT  |  ALTER TABLE  |
| 7.4 |  CREATE TABLE  |  REVOKE  |  ALTER TABLE  |  GRANT  |  SELECT  |
| 7.3 |  CREATE TABLE  |  SELECT  |  ALTER TABLE  |  REVOKE  |  GRANT  |
| 7.2 |  CREATE TABLE  |  SELECT INTO  |  SELECT  |  ALTER TABLE  |  CREATE TYPE  |
| 7.1 |  CREATE TABLE  |  SELECT INTO  |  SELECT  |  CREATE TYPE  |  ALTER TABLE  |
| 7.0 |  SELECT  |  SELECT INTO  |  CREATE TYPE  |  CREATE TABLE  |  COMMENT  |

## Number of functions available in each version

    :::sql
    SELECT
        version,
        count(func),
        sum(letter_count)
    FROM postgresql_development.data
    GROUP BY version ORDER BY version;

<div class="text-center"><img src="/posts/assets/postgresql-development-history-revealed-with-postgresql/plot1.png"/></div>

## The most verbose docs in each version

    :::sql
    SELECT DISTINCT ON (version)
        version,
        func,
        letter_count
    FROM postgresql_development.data
    ORDER BY version, letter_count DESC;

Poor `REVOKE`, the defeated champion.

<div class="text-center">
    <table style="margin-left:auto; margin-right: auto">
    <thead>
    <tr>
    <th><span class="caps">VERSION</span></th>
    <th><span class="caps">FUNCTION</span></th>
    <th><span class="caps">LETTER</span> <span class="caps">COUNT</span></th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td>10</td>
    <td><span class="caps">CREATE</span> <span class="caps">TABLE</span></td>
    <td>3142</td>
    </tr>
    <tr>
    <td>9.6</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2856</td>
    </tr>
    <tr>
    <td>9.5</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2856</td>
    </tr>
    <tr>
    <td>9.4</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2856</td>
    </tr>
    <tr>
    <td>9.3</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2856</td>
    </tr>
    <tr>
    <td>9.2</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2856</td>
    </tr>
    <tr>
    <td>9.1</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2508</td>
    </tr>
    <tr>
    <td>9</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2502</td>
    </tr>
    <tr>
    <td>8.4</td>
    <td><span class="caps">REVOKE</span></td>
    <td>2105</td>
    </tr>
    <tr>
    <td>8.3</td>
    <td><span class="caps">REVOKE</span></td>
    <td>1485</td>
    </tr>
    <tr>
    <td>8.2</td>
    <td><span class="caps">REVOKE</span></td>
    <td>1527</td>
    </tr>
    <tr>
    <td>8.1</td>
    <td><span class="caps">REVOKE</span></td>
    <td>1312</td>
    </tr>
    <tr>
    <td>8</td>
    <td><span class="caps">CREATE</span> <span class="caps">TABLE</span></td>
    <td>1251</td>
    </tr>
    <tr>
    <td>7.4</td>
    <td><span class="caps">CREATE</span> <span class="caps">TABLE</span></td>
    <td>1075</td>
    </tr>
    <tr>
    <td>7.3</td>
    <td><span class="caps">CREATE</span> <span class="caps">TABLE</span></td>
    <td>929</td>
    </tr>
    <tr>
    <td>7.2</td>
    <td><span class="caps">CREATE</span> <span class="caps">TABLE</span></td>
    <td>929</td>
    </tr>
    <tr>
    <td>7.1</td>
    <td><span class="caps">CREATE</span> <span class="caps">TABLE</span></td>
    <td>871</td>
    </tr>
    <tr>
    <td>7</td>
    <td><span class="caps">SELECT</span></td>
    <td>450</td>
    </tr>
    </tbody>
    </table>
</div>

## CREATE TABLE docs evolution

    :::sql
    SELECT
        version,
        letter_count
    FROM postgresql_development.data
    WHERE func = 'CREATE TABLE'
    ORDER BY func, version;

Something's going on in an upcoming 10.0 version.

<div class="text-center"><img src="/posts/assets/postgresql-development-history-revealed-with-postgresql/plot2.png"/></div>

All the data was obtained with the following Python script and processed inside the PostgreSQL database. Plots done with [Bokeh](http://bokeh.pydata.org/en/latest/), though I probably wouldn't use it again, the docs site is absurdly sluggish and the info is just all over the place.

<script src="https://gist.github.com/zimmicz/f69a5ce5d3cf3a220e171553c35e0391.js"></script>