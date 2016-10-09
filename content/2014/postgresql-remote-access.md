Title: PostgreSQL Remote Access
Date: 2014-09-17 17:04
Tags: postgresql, linux
Category: development

PostgreSQL is set to listen only to connections coming from localhost by default. I guess that's fine as far as you don't need access to the database from anywhere else (like your work network). If you do, you need to log via SSH or use some online database management tool (go for [Adminer](http://adminer.org) and forget about anything called php[pg|my]admin). Or you can set it up to access connections from other locations.

You need to:

1. set `listen_addresses` to `*` in your postgres.conf. That does not mean anyone can connect to your database, that means that the server will listen to connections coming from any available IP interface.
2. insert new entry into pg_hba.conf looking like this: `host database user xxx.xxx.xxx.xxx md5`. Now we're saying we only want connections coming from IP `xxx.xxx.xxx.xxx` accepted.
3. Add rule allowing the database server access to iptables. Number 5 says it will be the fifth rule in the order. It must come before the final REJECT ALL rule if present.

    `iptables -I INPUT 5 -p tcp --dport 5432 -s xxx.xxx.xxx.xxx -j ACCEPT`
4. Just to be sure noone else is able to connect, reject all on port 5432.

    `iptables -I INPUT 6 -p tcp --dport 5432 -j REJECT`

You're set to remotely connect to your database server.
