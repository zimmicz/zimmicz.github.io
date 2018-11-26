Title: Implementing Linked List with PostgreSQL Recursive CTE
Date: 2018-11-26 21:00
Category: SQL
Tags: postgresql

I've been working on a book/storytelling pet project recently. Dealing with book events and keeping them in order was a task that was to be tackled sooner or later. While both frontend and backend of the app could deal with linked and ordered data, database might be just about the best place to do so.

## What you might need a linked list for

You have a set of chronological events. The set is not complete at the beginning and position of events might be changed (e.g. their neighbouring events might change in time).

## Implementation

Linked list is a perfect structure for such a case (see <a href="https://en.wikipedia.org/wiki/Linked_list">Wikipedia</a>). You can keep your data in tact using just id and previous/next id.

    :::sql
    CREATE TABLE public.events (
      id integer generated always as identity primary key,
      previous_id integer
    );

    COPY public.events (id, previous_id) FROM stdin;
    7	\N
    10	5
    5	1
    1	3
    3	8
    8	9
    9	2
    2	6
    6	4
    4	7
    \.

Generating the list of events in the right order is the matter of running one recursive CTE query.

    :::sql
    WITH RECURSIVE evt(id) AS (
    SELECT
        id,
        previous_id
    FROM events
    WHERE previous_id IS NULL
    UNION
    SELECT
        e.id,
        e.previous_id
    FROM events e
    JOIN evt ON (e.previous_id = evt.id)
    )
    SELECT * FROM evt;

It gathers the first event (the one having the previous pointer set to `NULL`) and iteratively adds the following ones. Note that this version is actually the _reverse_ implementation of the linked list, pointing to the previous instead of the next event. All it would take to change that, would be finding the event id not present in `previous_id` column as the first one instead of `WHERE previous_id IS NULL`.

With the data coming properly sorted to the client, all it has to do is rendering the list.

