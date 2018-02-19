Title: PostgreSQL Backup and Recovery Orchestration: Recovery
Date: 2018-02-16 16:00
Category: SQL
Tags: postgresql, linux
Series: PostgreSQL Backup and Recovery Orchestration
Image: https://www.zimmi.cz/posts/assets/postgresql-backup-and-recovery-orchestration/postgresql_recovery.jpg

PostgreSQL continuous backups are very powerful, if you know how to use them for recovery. There's nothing else to do to be sure about that other than **actually trying it**. Personally, I see recovery as a single process with two possibly different outcomes:

* you're recovering to the same state your cluster is/was in (because of a hardware failure, provider switch, &hellip;) - it's more of a data migration, but you need your backup anyway
* you're doing a point-in-time-recovery (someone dropped the wrong table, data got corrupted, &hellip;)

Both scenarios follow the same steps and differ slighty at the end.

1. Stop the PostgreSQL cluster.
2. Copy the current `PGDATA_DIR` somewhere safe, just in case you screw up.
3. Replace the `PGDATA_DIR` with the full backup. If you start the cluster right away, it will boot to the last full backup state (in my case, missing a week of WAL segments tops).

## General recovery

In this case, you're trying to recover as far as possible. With previous steps done succesfully, the next follow:

* Copy all archived WAL segments created after the last full backup to `PGDATA_DIR/pg_xlog`. These can be found with `find -newer` command run against the corresponding `.backup` file in your `wal-archive/u/p` directory.
* If your full backup strategy includes `recovery.conf` file creation, you cane safely move it or remove it.
* Start the database cluster again. It is going to boot to the last working state.

If you're about to migrate your data, you might be better off with simple `pg_dump`, `pg_dumpall` and `pg_restore` commands rather than using full backup/WAL segments combination.


## Point-in-time-recovery

PostgreSQL's PITR can help you restore your accidentally deleted/corrupted data. After the first three steps mentioned above, you should follow with these:

* Copy all archived segments created after the last full backup somewhere the PostgreSQL user can read them (`/your-wal-recovery-folder/` for example).
* Set up the `recovery.conf` file properly. If you know something nasty happened at 2018-01-29 08:00:00, try to recover right to that point (or to any other, as [described in the documentation](https://www.postgresql.org/docs/9.6/static/recovery-target-settings.html)).

<!-- -->
    :::bash
    restore_command = 'cp /your-wal-recovery-folder/%f "%p"'
    recovery_target_time = '2018-01-29 08:00:00'

* Start the database cluster again. It is going to boot to the last full backup and then play all the WAL segments until the recovery target. Depending on how many WAL segments are about to be used, this might take a while.

## Pitfalls

You don't want to find yourself in the middle of the biggest database failure of the century just to find out your **backups don't work**, and even if they did, you would have **no idea how to use them**. Or, even worse, there are no backups at all, because your **backup strategy has been failing silently** without a single notice for several months.

## Tips

Try to recover from your backups once in a while.

I forget things and make mistakes. We all do. That's why I built an ensemble that takes care of our database automatically. Nothing fancy, just a bunch of good old Bash scripts managed with systemd rathern than cron. Next time, I'd like to show you the code and walk you through our current setup.
