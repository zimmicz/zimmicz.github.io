Title: PostgreSQL Backup and Recovery Orchestration: Bash Automation
Date: 2018-03-02 16:00
Category: SQL
Tags: postgresql, linux
Series: PostgreSQL Backup and Recovery Orchestration
Image: https://www.zimmi.cz/posts/assets/postgresql-backup-and-recovery-orchestration/postgresql_recovery.jpg

There is a bunch of periodic database-related tasks in a life of PostgreSQL administrator. Some should be done daily, others weekly, others can wait for a whole month. Many of them are essential for your database health. Forget to run such a task or screw up the run accidentally, and you'll be snowed under with fixing your database.

Those tasks are easily done with bash, which is the first step to full automation. Following tasks are perfect candidates to be implemented as bash scripts:

* full backups (both creation and removal)
* WAL backups (both creation and removal)
* vacuum
* pgBadger log analysis (both creation and removal)
* log maintenance (if you don't use log rotate)

<!-- -->

Full backup creation is just one example of how powerful bash can be.

    :::bash
    #!/bin/bash
    #
    # @author: Michal Zimmermann <michal.zimmermann@clevermaps.cz>
    # Creates base backup.

    CUR_DIR=$(dirname "$0")
    if [[ ! -f ${CUR_DIR}/pgsql-common.sh ]]
    then
        echo "pgsql-common.sh not found!"
        exit 1
    fi

    source "${CUR_DIR}/pgsql-common.sh"
    source "$CONFIG"

    if [[ -d ${CR_BASE_BACKUP_DIR}/${CR_LABEL} ]]
    then
        echo "${CR_BASE_BACKUP_DIR}/${CR_LABEL} already exists and is not empty!"
        exit 2
    fi

    pg_basebackup \
        --pgdata=${CR_BASE_BACKUP_DIR}/${CR_LABEL} \
        --format=plain \
        --write-recovery-conf \
        --wal-method=stream \
        --label=${CR_LABEL} \
        --checkpoint=fast \
        --progress \
        --verbose

    if [[ $? -gt 0 ]]
    then
        rm -rf ${CR_BASE_BACKUP_DIR}/${CR_LABEL}
        echo "pg_basebackup on ${CR_LABEL} failed!"
        exit 3
    fi

    tar -czf ${CR_BASE_BACKUP_DIR}/${CR_LABEL}.tar.gz ${CR_BASE_BACKUP_DIR}/${CR_LABEL} && rm -rf ${CR_BASE_BACKUP_DIR}/${CR_LABEL}

As you probably noticed, a `pgsql-common.sh` file is sourced at the beginning of the script. This script in turn just loads the proper config file that provides variables to other, devops, scripts. As you might need those variables in several of your scripts, it is a good idea to put their load to a separate file.

    :::bash
    #!/bin/bash
    #
    # @author: Michal Zimmermann <michal.zimmermann@clevermaps.cz>
    # Sourced in pgsql-*.sh scripts.

    while [[ $# > 0 ]]
    do
        key="$1"

        case $key in
            -c|--config)
                CONFIG="$2"
                shift
                ;;
            *)
                echo "Usage: `basename $0` --config|-c [config_file]"
                exit 1
                ;;
        esac
        shift
    done
    # /Input parameters

    if [[ -z "$CONFIG" ]]
    then
        echo "Config file is not set! See the script usage below."
        $0 *
        exit 2
    fi

    if [[ ! -f "$CONFIG" ]]
    then
        echo "$CONFIG not found!"
        exit 3
    fi

A config file might remain as simple as this:

    :::bash
    # Base backup location
    export CR_BASE_BACKUP_DIR="/mnt/backup/symap/base/"
    # WAL backup location
    export CR_WAL_BACKUP_DIR="/mnt/backup/symap/wal"
    # PostgreSQL WAL location
    export CR_PG_XLOG_DIR="/var/lib/postgresql/10/symap/pg_wal"
    export CR_PG_LOG_DIR="/var/lib/postgresql/10/symap/pg_log"
    # Base backup pattern (set to YYYYMMDD)
    export CR_LABEL=symap_$(date +%Y%m%d)
    export PGPORT=5432

Another, likely the simplest, example is a vacuumdb task:

    :::bash
    #!/bin/bash
    #
    # @author: Michal Zimmermann <michal.zimmermann@clevermaps.cz>
    # Vacuums the whole database cluster running on a given port.

    while [[ $# > 0 ]]
    do
        key="$1"

        case $key in
            -p|--port)
                PORT="$2"
                shift
                ;;
            *)
                echo "Usage: `basename $0` --port|-p [port_number]"
                exit 1
                ;;
        esac
        shift
    done

    if [[ -z "$PORT" ]]
    then
        echo "Port not provided!"
        $0 *
        exit 2
    fi

    /usr/bin/vacuumdb -U postgres -p $PORT --all --full --analyze


## Tips

* Always test your bash scripts before production deployment. Even a single line of code might lead to a very different, possibly unexpected, outcome.
* Try to stay as defensive as possible. Imagine a variable did not get sourced properly. Is it going to blow your database? Trust me, I know what I am talking about (see the tweet below).


<blockquote class="twitter-tweet" data-lang="cs"><p lang="en" dir="ltr">that feeling when you blog about keeping your <a href="https://twitter.com/hashtag/postgresql?src=hash&amp;ref_src=twsrc%5Etfw">#postgresql</a> data safe and few days later you accidentally bzip all postgres-owned files WHILE the database is running with untested <a href="https://twitter.com/hashtag/bash?src=hash&amp;ref_src=twsrc%5Etfw">#bash</a> script. What a <a href="https://twitter.com/hashtag/tuesday?src=hash&amp;ref_src=twsrc%5Etfw">#tuesday</a>!</p>&mdash; Michal Zimmermann (@zimmicz) <a href="https://twitter.com/zimmicz/status/968546584567996416?ref_src=twsrc%5Etfw">27. února 2018</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

## Pitfalls

You do not want to run your bash scripts by hand. You probably do not want them to be run by cron. You want to run them with systemd. More on this next time.
