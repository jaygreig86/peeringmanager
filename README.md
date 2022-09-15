# peeringmanager
This project comprises a simple web frontend created in PHP for managing a MySQL database of Peers and Customers with associated BGP Sessions and Routers.  

There's a separate backend coded in Python and BASH which can be scheduled to run on a cron to build and push configurations to routers.  Currently only tested with Arista EOS.

```
30 1 * * * /var/www/vhosts/peermanager/bgp/run.sh -r my1st.router.tld
0 1 * * * /var/www/vhosts/peermanager/bgp/run.sh -r my2nd.router.tld
```

Open Source and released under BSD 2-Clause licence

This is work in progress.


