Title: PostgreSQL Backup and Recovery Orchestration: systemd Automation
Date: 2018-04-10 12:00
Category: SQL
Tags: postgresql, linux
Series: PostgreSQL Backup and Recovery Orchestration
Image: https://www.zimmi.cz/posts/assets/postgresql-backup-and-recovery-orchestration/postgresql_recovery.jpg

Posts in this series have described the basic automation of PostgreSQL backup/recovery strategy. The process itself consists of different periodic tasks that shouldn't be executed manually. There are essentially two tools dedicated to periodic task running in Linux: **cron** and **systemd**.

Cron used to be my first choice of automation in Linux, as it's very easy to use. On the other hand, it's quite messy (running `crontab -e` under different users to find out which one has the job defined) and a bit difficult to test - many times I ran into a situation when underlying bash script executed just fine, while cron job kept failing for reason unknown.

My own cron experience together with a few words from a workmate brought me into the arms of systemd, which is a Linux system and service manager. It's capable of running periodic tasks just like cron, yet making it more transparent.

## Important bits

Understanding the whole systemd is way out of scope of a poor GIS guy, yet I managed to tame three important parts of the ecosystem:

* services
* timers
* targets

### Services
Service is a configuration saved inside ".service" file specifying what you want systemd to do. Following code shows how you can tell systemd to vacuum your database once in a while.

    :::bash

    [Unit]
    Description=CR vacuumdb
    OnFailure=unit-status-mail@%n.service unit-status-slack@%n.service
    Wants=cr-sunday.timer

    [Service]
    User=postgres
    Group=postgres
    Type=simple
    ExecStart=/bin/bash /usr/local/sbin/pgsql-vacuumdb.sh --port %i

    [Install]
    WantedBy=cr-sunday.target

Unit files come with several handy features. First of all, they are orchestrated with `systemctl`. Second, any service configuration file containing `@` in its filename might be symlinked/copied and run for different instances. Third, notice `OnFailure` directive in the code above. If anything goes wrong, systemd might serve as a postman delivering the bad news. I set up both e-mail and Slack notifications and they've been working like a charm ever since.

On top of that, I find systemd orchestration much easier to test and maintain compared to cron.

With the above code saved in `/lib/systemd/system/pgsql-vacuumdb@.service`, you can copy the file to `/lib/systemd/system/pgsql-vacuumdb@5432.service`, `/lib/systemd/system/pgsql-vacuumdb@5432.service` etc. If you look at `ExecStart` part of the service file, you'll notice `%i` being used at the end - a [placeholder](https://www.freedesktop.org/software/systemd/man/systemd.unit.html) replaced with the string between `@` and `.service` in the filename.

This systemd service file is no more than a simple wrapper around the following bash code. We run three different database clusters on one machine and this approach makes their maintenance pretty comfortable.

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

What you get so far is the possibility to run `systemctl start pgsql-vacuumdb@5432` instead of calling the underlying bash code manually. Not much, really. That's where timers come to the party.

### Timers

Timer files ends with ".timer" and are responsible for running services on given time. The code below, coming from `/lib/systemd/system/cr-sunday.timer` file runs the `pgsql-vacuumdb` service every Sunday at 3:45 am.

    :::bash

    [Unit]
    Description=CR Sunday timer

    [Timer]
    OnCalendar=Sun *-*-* 03:45
    Persistent=yes
    Unit=cr-sunday.target

    [Install]
    WantedBy=multi-user.target

### Targets

Target files end with ".target" and are used to group units in general. In our case, the target file for vacuumdb service is as simple as the following code.

    :::bash
    [Unit]
    Description=CR Sunday target
    StopWhenUnneeded=yes

Targets might be called by other targets. Running `systemctl start cr-sunday.target` would eventually lead to running all the services wanted by that target.

As I already mentioned, I find systemd services easy to code and test. If any of them should fail, you'd find a message in syslog or via `systemctl status pgsql-vacuumdb`.
