Title: PostgreSQL Backup and Recovery Orchestration: WAL Archiving
Date: 2018-02-12 16:00
Category: SQL
Tags: postgresql, linux
Series: PostgreSQL Backup and Recovery Orchestration
Image: https://www.zimmi.cz/posts/assets/postgresql-backup-and-recovery-orchestration/postgresql_recovery.jpg

Just a very few of my day-to-day work tasks can be accomplished without PostgreSQL. For years I've been a (power) user of this wonderful relational database, knowing almost nothing about how its internals really work. Faced with the need to build a backup and recovery strategy, I've recently read up *a lot* on this topic.

As I don't find it very odd for a GIS person to be given such an extraordinary task (nobody wants to lose the priceless spatial data, right?), I hope this series might shed light on how to prepare and manage the backup/recovery process to those, who are up to such a task. I won't be discussing backup strategies based on `pg_backup` tool, as those don't offer neither continuous archivation, nor point-in-time-recovery (PITR) - those two features disqualifies it as [CleverMaps](https://www.clevermaps.cz) production backup strategy.

**That leaves us with taking periodic base backups combined with continuous WAL archivation, as described below.**

## Taking base backups

Archived WAL segments are worthless without a base backup they can be run on. It's crucial to have consistent, periodic base backups to keep your data safe.

[`pg_basebackup`](https://www.postgresql.org/docs/current/static/app-pgbasebackup.html) takes base backup of PostgreSQL cluster. Nothing fancy. Gzipping the output folder once the backup is done is definitely a good idea.

    :::bash
    pg_basebackup \
        --pgdata=/mnt/backup/base/backup_number \
        --format=plain \
        --write-recovery-conf \
        --xlog-method=stream \
        --label=${CR_LABEL} \
        --checkpoint=fast \
        --progress \
        --verbose

In our current environment, we take a base backup of each of our clusters once a week.

## WAL archiving configuration

To properly set WAL archiving, several `postgresql.conf` settings has to be adjusted:

* `wal_level = replica`
* `archive_mode = on`
* `archive_command = test ! -f /backup/wal/%f && cp %p /backup/wal/%f`

Setting `wal_level` to `replica` writes enough information for WAL archiving. Turning on `archive_mode` will run `archive_command` each time a WAL segment is completed. `archive_command` might be anything from simple `cp` to `rsync` or `aws s3 cp` commands. It is absolutely critical that the command returns **non-zero exit code** in case of failure (including when a file with the same name already exists in your backup folder).

That's it, after reloading PostgreSQL service, new WAL files should be copied to `/backup/wal` directory. The PostgreSQL process user (`postgres` usually) has to be able to write to the location.

### Pitfalls

* If `archive_command` fails, WAL segment remains on your database drive. If it keeps failing long enough, you'll run out of space and the database will crash.
* If the backup location fills up, the above-mentioned happens as well.
* If you lose or corrupt any of the archived WAL segments, you won't be able to pass through. That's why you want to be sure that your `archive_command` actually does what you think it does.

### Tips

It might be a real PITA (fiddling around WAL segments included) to start a crashed database cluster with no space left. Keeping a dummy file in your `pg_xlog` location might save you a lot of trouble. Create one with following command. If you run out of space, remove this file and you get 300 MB for free. Don't forget to recreate it after you start the cluster.

    :::bash
    dd if=/dev/zero of=/path_to_your_database_cluster/pg_xlog/DO_NOT_MOVE_THIS_FILE bs=1MB count=300

There's no need to keep archived WAL segments forever. They're only needed until you take another base backup. Again, deleting WAL segments manually (or using `find ! -newer previous_base_backup.tar.gz`) might lead to accidental corruption of your backups. It's much safer to use [`pg_archivecleanup`](https://www.postgresql.org/docs/9.6/static/pgarchivecleanup.html) pointed to your WAL backup folder, referencing the last **sucessful** full backup. Below is the script we use to keep our WAL backup folder of reasonable size, keeping the last three full backups.

    :::bash
    # Find base_backup files not older than 3 weeks
    # Sort by date
    # Use the oldest one as a reference
    OLDEST_BASE_BACKUP=$(basename $(find ${CR_WAL_BACKUP_DIR}/u/p/ -type f -iname "*.backup" -mtime -21 -print0 | \
    xargs -0 ls -t | \
    tail -n 1))

    # Find all subfolders
    # Except the u/p backup subfolder
    # Execute pg_archivecleanup for each of the subfolders
    find $CR_WAL_BACKUP_DIR \
        -type d \
        -not -path "${CR_WAL_BACKUP_DIR}u*" \
        -exec pg_archivecleanup -d {} $OLDEST_BASE_BACKUP \;

Functional backups are crucial part of a solid backup/recovery system. They're still just one half of that system, though. **If not tested thoroughly**, they're even less than that. More on testing backups and recovering from failures next time.
