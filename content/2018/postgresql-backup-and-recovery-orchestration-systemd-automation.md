Title: PostgreSQL Backup and Recovery Orchestration: systemd Automation
Status: draft
Date: 2018-04-05 16:00
Category: SQL
Tags: postgresql, linux
Series: PostgreSQL Backup and Recovery Orchestration
Image: https://www.zimmi.cz/posts/assets/postgresql-backup-and-recovery-orchestration/postgresql_recovery.jpg

Posts in this series have described the basic automation of PostgreSQL backup/recovery strategy. The process itself consists of different periodic tasks that shouldn't be executed manually. There are essentially two tools dedicated to periodic task running in Linux: **cron** and **systemd**.

Cron used to be my first choice of automation in Linux, as it's very easy to use. On the other hand, it's quite messy (running `crontab -e` under different users to find out which one has the job defined) and a bit difficult to test - many times I ran into a situation when underlying bash script executed just fine, while cron job kept failing for reason unknown.

My own cron experience together with a few words from a workmate brought me into the arms of systemd, which is a Linux system and service manager. It's capable of running periodic tasks just like cron, yet making it more transparent.

## Important bits

Understaning the whole systemd is way out of scope of a poor GIS guy, yet I managed to tame three important parts of the ecosystem:

* services
* timers
* targets

### Services

### Timers

### Targets

