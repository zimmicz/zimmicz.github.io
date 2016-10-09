Title: Blogging On Docker: Piecrust To The Rescue
Date: 2014-09-11 20:16
Category: development
Tags: docker, linux

I love blogging. I hate blogging systems. I hate content management systems. I just want to blog. That's what [PieCrust](http://bolt80.com/piecrust/) is all about - it lets you blog.

It is powerful static website generator perfect for my needs (and for yours as well?). Blogging with PieCrust is really a piece of cake:

1. prepare post
2. serve site
3. bake site
4. send it off to the public

I love having clean OS. That's what [Docker](http://docker.com) is all about - for me. Running PieCrust on Docker is really easy, it does not clutter your PC and it just works.

If you ever want to use PieCrust on Docker, why don't you start with this code?
    FROM centos:centos6

    RUN rpm -Uvh http://mirror.webtatic.com/yum/el6/latest.rpm
    RUN rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    RUN rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-6.rpm

    RUN yum --enablerepo=remi,remi-php55 install -y php php-mbstring php-opcache php-cli php-pear php-common && yum clean all
    RUN php -r "readfile('https://getcomposer.org/installer');" | php
    RUN echo "date.timezone = Europe/Prague" >> /etc/php.ini
    RUN mv composer.phar /usr/bin/composer
    RUN php -r "eval('?>'.file_get_contents('http://backend.bolt80.com/piecrust/install'));"
    RUN mv piecrust.phar /usr/bin/chef

    CMD ["/bin/bash"]

Running `sudo docker build --tag=piecrust .` will result in having docker container ready to run. Just run `sudo docker run -it -p 8080:8080 -v /host_piecrust_path/:/container_path piecrust /bin/bash` in terminal. While in container terminal, run `chef serve -n -p 8080 -a 0.0.0.0` and visit [http://localhost:8080](http://localhost:8080). You should see your PieCrust site up and running.

The last command tells chef to serve your site on port 8080 (which should be free unless you're running Tomcat or something like that) and make it listen on every available network interface. If you used 127.0.0.1 instead, you would never reach your site from outside the container.

See? Easy.
