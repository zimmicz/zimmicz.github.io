Title: Twitter REST API Data Mining on OpenShift (Part I)
Date: 2015-11-6 22:00
Tags: javascript, openshift, twitter
Category: development

More than a year ago I wrote about [analyzing Twitter languages with Streaming API]({filename}/2014/analyzing-twitter-languages-with-streaming-api.md). Back then I kept my laptop running for a week to download data. Not a comfortable way, especially if you decide to get more data. One year uptime doesn't sound like anything you want to be part of. [OpenShift](https://www.openshift.com/) by Red Hat seems to be almost perfect replacement. Almost.

## OpenShift setup

I started with Node.js application running on one small gear. Once running, you can easily `git push` the code to your OpenShift repo and login via SSH. I quickly found simple copy-pasting my local solution wasn't going to work. and fixed it with some minor tweaks. That's where the fun begins...

> I based the downloader on Node.js a year ago. Until now I still don't get how that piece of software works. Frankly, I don't really care as long as it works.

### Pitfalls

If your application doesn't generate any traffic, **OpenShift turns it off**. It wakes up once someone visits again. I had no idea about that and spent some time trying to stop that behavior. Obviously, I could have scheduled a cron job on my laptop pinging it every now and then. Luckily, OpenShift can run cron jobs itself. All you need is to embed a cron cartridge into the running application (and install a bunch of ruby dependencies beforehand).

    :::bash
    rhc cartridge add cron-1.4 -a app-name

Then create `.openshift/cron/{hourly,daily,weekly,monthly}` folder in the git repository and put your script running a simple curl command into one of those.

    :::bash
    curl http://social-zimmi.rhcloud.com > /dev/null

Another problem was just around the corner. Once in a while, the app stopped writing data to the database without saying a word. What helped was restarting it - the only automatic way to do so being a `git push` command. Sadly, I haven't found a way to restart the app from within itself; it probably can't be done.

When you `git push`, the gear stops, builds, deploys and restarts the app. By using hot deployment you can minimize the downtime. Just put the `hot_deploy` file into `.openshift/markers` folder.

    :::bash
    git commit --allow-empty -m "Restart gear" && git push

This solved the problem until I realize that **every restart deleted all the data** collected so far. If your data are to stay safe and sound, **save them in `process.env.OPENSHIFT_DATA_DIR`** (which is `app-root/data`).

### Anacron to the rescue

How do you push an empty commit once a day? With cron of course. Even better, **anacron**.

    :::bash
    mkdir ~/.anacron
    cd ~/.anacron
    mkdir cron.daily cron.weekly cron.monthly spool etc

    cat <<EOT > ~/.anacron/etc/anacrontab

    SHELL=/bin/sh
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/$HOME/bin
    HOME=$HOME
    LOGNAME=$USER

    1 5  daily-cron nice run-parts --report $HOME/.anacron/cron.daily
    7 10 weekly-cron nice run-parts --report $HOME/.anacron/cron.weekly
    @monthly 15 monthly-cron nice run-parts --report $HOME/.anacron/cron.monthly

    EOT

    cat <<EOT >> ~/.zprofile # I use zsh shell
    rm -f $HOME/.anacron/anacron.log
    /usr/sbin/anacron -t /home/zimmi/.anacron/etc/anacrontab -S /home/zimmi/.anacron/spool &> /home/zimmi/.anacron/anacron.log

    EOT

Anacron is to laptop what cron is to 24/7 running server. It just runs automatic jobs when the laptop is running. If it's not and the job should be run, it runs it once the OS boots. Brilliant idea.

It runs the following code for me to keep the app writing data to the database.

    :::bash
    #!/bin/bash

    workdir='/home/zimmi/documents/zimmi/dizertace/social'
    logfile=$workdir/restart-gear.log
    date > $logfile

    {
    HOME=/home/zimmi
    cd $workdir && \
    git merge origin/master && \
    git commit --allow-empty -m "Restart gear" && \
    git push && \
    echo "Success" ;
    } >> $logfile 2>&1

**UPDATE:** Spent a long time debugging the "Permission denied (publickey)."-like errors. What seems to help is:

1. Use id_rsa instead of any other SSH key
2. Put a new entry into the `~/.ssh/config` file

I don't know which one did the magic though.

I've been harvesting Twitter for a month with about 10-15K tweets a day (only interested in the Czech Republic).
<sup>1</sup>&frasl;<sub>6</sub> to <sup>1</sup>&frasl;<sub>5</sub> of them is located with latitude and longitude. More on this next time.
        
        
