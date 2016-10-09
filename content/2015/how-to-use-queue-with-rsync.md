Title: How to Use Queue with Rsync
Date: 2015-10-01 07:51
Tags: linux, bash
Category: automation

Having more than 120K 5MB+ images that should be moved to the server is a great oportunity for some automatic bash processing. It might be good idea to use [ImageMagick](http://www.imagemagick.org/script/index.php) [convert tool](http://www.imagemagick.org/script/convert.php) to make images smaller in a simple for loop. [GNU Parallel](http://www.gnu.org/software/parallel/) can significantly increase the performance by running one job per CPU core.

    :::bash
    parallel --verbose convert {} -quality 40% {} ::: *.jpg

The `parallel` modifies several images per second. Uploading these right away seems to be the next step. But how do you tell `rsync` to check for modified files every now and then? Another for loop mixed with `sleep` would work, but it just doesn't feel right.

Luckily, there's a [`inotifywait`](http://linux.die.net/man/1/inotifywait) tool capable of watching changes to files and taking actions based on those changes.

    :::bash
    inotifywait -e close_write -m --format '%f' . | \
    while read file
    do
        echo $file
        rsync -OWRD0Pq --ignore-existing $file data@localhost
    done

By default, `inotifywait` stops after receiving a single event, while `-m` flag runs it indefinitely. `-e` flag defines an event to watch for, in my case that's a `close_write` event. The `inotifywait` output can be piped to `rsync` that takes care of syncing local files to remote server.

The last step, as usual, is profit.