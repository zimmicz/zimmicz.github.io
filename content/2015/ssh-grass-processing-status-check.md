Title: SSH GRASS Processing Status Check
Date: 2015-07-21 07:51
Tags: bash, linux
Category: development

I've been running some GRASS/PostGIS computations on a remote server that were taking hours to finish. Once in a while I checked for their state by issuing `tail log_XX.log` from my laptop to see if they were ready yet. It suddenly became pretty annoying to check five different logs every ten minutes.

Instead of waiting and checking the logs, I thought it would be great to automate this. And it would be awesome if checking was fun. So I wrote a simple routine that takes log number as an argument (every process logs to a separate logfile) and checks it every minute until it says *done*. Right after that `notify-send` gives me a neat popup and Queen starts playing their *We are the champions* thanks to `mpg123`.

    :::bash
    #!/usr/bin/env bash
    item=$1

    while true; do
        echo "############ ${item} ############"
        x=$(ssh user@remote.server "tail -n 30 path/to/my/log_${item}.log")

        if [[ $x == *"done"* ]]
            then
                notify-send -u critical "Finally ${item}"
                mpg123 -n 250 ~/Music/queen-we_are_the_champions.mp3
                exit
            else echo "Not yet"
        fi
        sleep 60
    done

What seemed to be really frustrating makes me happy right now. Unless Freddie starts singing in the middle of the night.
