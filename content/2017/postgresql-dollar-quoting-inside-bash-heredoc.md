Title: PostgreSQL Dollar Quoting inside Bash Heredoc
Date: 2017-09-22 20:30
Category: SQL
Tags: sql, postgresql, bash
Image: https://www.zimmi.cz/posts/assets/postgresql-dollar-quoting-inside-bash-heredoc/bash.png

Yesterday I spent two very unpleasant hours debugging the weirdest SQL error I've seen in my life, running the below query (simplified for this post).

    :::sql
    psql -qAt --no-psqlrc <<BACKUP
    DO
    $$
    DECLARE r record;
    BEGIN
      RAISE INFO '%', 'info';
    END
    $$;
    BACKUP

Running this in your terminal will result in a nasty syntax error.

    :::bash
    ERROR:  syntax error at or near "1111"
    LINE 2: 1111
            ^
    ERROR:  syntax error at or near "RAISE"
    LINE 2:   RAISE INFO '%', 'info';
              ^
    ERROR:  syntax error at or near "1111"
    LINE 2: 1111;

You stare on the screen for a while, absolutely sure that number `1111` is nowhere close to the data you work with. You try again. Another error. You save the code into a file and try again. It works. What the _heck_? You try again using the bash heredoc. Another failure.

The minute you realize `$$` is being substituted with the ID of the current process, you feel like the dumbest person on Earth. Yet the happiest one at the same time.

The solution is trivial.

    :::sql
    psql -qAt --no-psqlrc <<BACKUP
    DO
    \$\$
    DECLARE r record;
    BEGIN
      RAISE INFO '%', 'info';
    END
    \$\$;
    BACKUP