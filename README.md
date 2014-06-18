#novadns

This is a script that will generate a /etc/hosts file based on the openstack instances for a tenant. It's probably not a good idea to do this, but we have a specific application on a single host that requires DNS resolution, and because our OpenStack cloud is multi-host, we don't get it for free (not that it is something to be relied on anyways, not until something like Designate is available.)

At any rate, for our application we need the instance hostnames in /etc/hosts with the right IP address. Note that this script doesn't deal with duplicate hostnames.

##Usage

Note that his repo is really designed to be packaged, so the packager will likely change the NOVADNS_HOME to where ever it gets installed, eg. /etc/novadns.

```bash
$ cp nova.conf.example nova.conf
$ vi nova.conf # enter openstack credentials
$ sudo start novadns
$ ps ax  |grep [n]ovadns
 3666 ?        Ss     0:01 /usr/bin/python /home/centos/novadns/novadns.py
 ```
