Title: PostgreSQL Backup and Recovery Orchestration: WAL Archiving
Date: 2018-02-10 11:00
Category: SQL
Status: draft
Tags: postgresql, linux
Series: PostgreSQL Backup and Recovery Orchestration
Image: https://www.zimmi.cz/posts/assets/qgis-plugin-development-attribute-transfer-plugin/qgis.png

Just a very few of my day-to-day work tasks can be accomplished without PostgreSQL. For years I've been a (power) user of this wonderful relational database, knowing almost nothing about how its internals really work. Faced with the need to build a PostgreSQL backup and recovery strategy, I've recently read up a lot on this topic.

As I don't find it very odd for a GIS person to be given such an extraordinary task, I hope this series might shed light on how to prepare and manage the backup/recovery process to those, who are up to such a task. I won't be discussing backup strategies based on `pg_backup` tool, as those don't offer neither continuous archivation, nor point-in-time-recovery (PITR) - those two features disqualifies it as [CleverMaps](https://www.clevermaps.cz) production backup strategy.

That leaves us with taking periodic base backups combined with WAL archivation, described on the text below.

## WAL archiving configuration

To properly set WAL archiving, three `postgresql.conf` settings has to be changed:

* `wal_level = replica`
* `archive_mode = on`
* `archive_command = test ! -f /backup/wal/%f && cp %p /backup/wal/%f`

Setting `wal_level` to `replica` writes enough information for WAL archiving. Turning on `archive_mode` will in turn run `archive_command` each time a WAL segment is completed. `archive_command` might be anything from simple `cp` to `rsync` or `aws s3 cp` commands. It is absolutely critical that the command returns non-zero exit code in case of failure (including when a file with the same name already exists in your backup folder).

That's it, after reloading PostgreSQL service, new WAL files should be copied to `/backup/wal` directory. The PostgreSQL process user (`1postgres` usually) has to be able to write to the location.

### Pitfalls

* If `archive_command` fails, WAL segment remains on your database drive. If it keeps failing long enough, you'll run out of space and the database will crash.
* If the backup location fills up, the above-mentioned happens as well.
* If you lose or corrupt any of the archived WAL segments, you won't be able to pass through. That's why you want to be sure what your `archive_command` actually does.

### Tip

It might be a real PITA (WAL fiddling included) to start a crashed database cluster with no space left. Keeping a dummy file in your `pg_xlog` location might save you a lot of trouble. Create one with following command.

:::bash
dd if=/dev/zero of=/path_to_your_database_cluster/pg_xlog/DO_NOT_MOVE_THIS_FILE bs=1MB count=300
