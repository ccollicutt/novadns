#novadns

This is a script that is used to generate a /etc/hosts file based on the openstack instances for a tenant. It's probably not a good idea to do this, but we have a specific application that requires DNS resolution, and because our OpenStack cloud is multi-host, we don't get it for free, not that it is something to be relied on anyways.

At any rate, for our application, we need the instance names in /etc/hosts with the right IP address. This script doesn't deal with duplicate hostnames either.