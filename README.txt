======================
Vagrant + fabric + LXC
======================

This repository is a quick start to test / build a Debian Squeeze LXC environment.

Keywords :

* Debian Squeeze
* LXC


Instructions
============

First read `Vagrant + fabric bootstrap < http://harobed.github.com/vagrant-fabric-bootstrap/ >`_.

Next, configure LXC Host :

::

    $ bin/fab vagrant install

Create a new container (named by default ``my_container``) :

::

    $ bin/fab vagrant create_container


You can also destroy this container :

::

    $ bin/fab vagrant destroy_container


Play with your container
========================

Start container :

::

    $ vagrant ssh
    vagrant@vagrant:~$ sudo su
    root@vagrant:/home/vagrant# lxc-start -n my_container -d

See if your container is started :

::

    root@vagrant:/home/vagrant# root@vagrant:/home/vagrant# lxc-ls 
    my_container
    my_container

* First line is the list of all container.
* Second list is the list of container started.

See the init log of your container :

::

    root@vagrant:/home/vagrant# cat /var/log/lxc/my_container.log 
    INIT: version 2.88 booting
    Using makefile-style concurrent boot in runlevel S.
    hostname: the specified hostname is invalid
    Activating swap...done.
    Cleaning up ifupdown....
    Setting up networking....
    Activating lvm and md swap...done.
    Checking file systems...fsck from util-linux-ng 2.17.2
    done.
    Mounting local filesystems...done.
    Activating swapfile swap...done.
    Cleaning up temporary files....
    Setting kernel variables ...done.
    Configuring network interfaces...done.
    Cleaning up temporary files....
    startpar: service(s) returned failure: hostname.sh ... failed!
    INIT: Entering runlevel: 3
    Using makefile-style concurrent boot in runlevel 3.
    Starting OpenBSD Secure Shell server: sshd.

    Debian GNU/Linux 6.0 my_container console

    my_container login: 

Connect to your container :

::

    root@vagrant:/home/vagrant# lxc-console -n my_container

    Type <Ctrl+a q> to exit the console

    root@:/dev# cd
    root@:~# 

Note : ``Type <Ctrl+a q> to exit the console``.
