#!/usr/bin/env python

import MySQLdb as mdb
import configparser
import ipaddr
import sys
import subprocess
import os
import re

############################
# Config Section Start     #
############################

config_location = os.path.abspath(os.getcwd()).rstrip("/bgp") + "/httpdocs/configs/global.conf"

############################
# Config Section End       #
############################

# init empty config var
config = False

############################
# Logging function         #
############################

def log(type = "info",message = ""):
     global config
     con = None
     try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])

         cur = con.cursor(mdb.cursors.DictCursor)
         cur.execute("INSERT INTO ipms_logs (userid,type,logentry,datetime) VALUES (1,'%s','%s',NOW())" % (type,message))
         con.commit()
         print("%s: %s" % (type,message))
     except mdb.Error as e:

         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)

     finally:

         if con:
             con.close()


############################
# Run Main()               #
############################

def main(run_on_only = ""):
     global config
     config  = configparser.ConfigParser()
     config.sections()

     # Try reading the config file

     try:
        config.read(config_location)
     except configparser.Error as e:
        log("Error","Error reading config %d: %s\r\n" % (e.args[0], e.args[1]))
        sys.exit(1)

     con = None
     try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])

         cur = con.cursor(mdb.cursors.DictCursor)

         # Are we running this on one router or all routers

         if len(run_on_only):
              cur.execute("SELECT * FROM ipms_routers WHERE hostname = '%s'" % (run_on_only))
         else:
              cur.execute("SELECT * FROM ipms_routers")
         routers = cur.fetchall()

         for router in routers:
             log("info","Building peer config for %s" % (router['hostname']))
             cur.execute("SELECT * FROM ipms_bgppeers")
             peers = cur.fetchall()
             for peer in peers:
                 build_configuration(peer,router)

     except mdb.Error as e:

         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)

     finally:

         if con:
             con.close()

###################################
# Validate the session IP address #
###################################

def validate_session(session):
    # We first perform a number of validation checks before we build any configuration
    # 1) is the session address a valid IP
    # If all these pass, we then build the configuration

    try:
        # Check that the IP address retrieved from the database is a valid IP
        peer_ip = ipaddr.IPAddress(session['address'].decode('ascii'))
    except ValueError:
        log("Error","%s in %s is not a valid IP" % (session['address'].decode('ascii'), session['asn']))
        sys.exit(2)

    return True

###################################
# Build the configuration         #
###################################

def build_configuration(peer,router):
    global config
    asn = "AS" + str(peer['asn'])

    # We need to parse the AS-SET import line as peeringdb sometimes has extra
    # details there that we don't need at the moment
    peer_import_raw = peer['import']
    peer_import = re.sub('.*::','',peer_import_raw)

    con = None
    try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])

         cur = con.cursor(mdb.cursors.DictCursor)

         cur.execute("SELECT * FROM ipms_bgpsessions LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgppeers.peerid = %d AND ipms_bgpsessions.routerid = %d AND ipms_bgpsessions.type = 'customer'" % (peer['peerid'],router['routerid']))

         rows = cur.fetchall()

         bgppeers = ""  # Variable that will hold the BGP Peer config before it's pushed out to file
         maps = ""      # Variable that will hold the route maps before it's pushed out to file
         Active = False
         for row in rows:
             session_address = row['address'].decode('ascii')
             if validate_session(row) is not True:
               log("Error","The address is not valid.  We cannot reach %s" % (session_address))
               continue
             log("Info","Building peer config for %s - %s" % (asn,session_address))

             # We set active to True because there's an active session for this peer
             # on the current router.  We do not want to write config for a peer
             # that does not exist on this router.
             Active = True

                       #########################
                       # Build IPv6            #
                       #########################

             if ':' in session_address:
                           bgppeers += """
router bgp %s
neighbor %s remote-as %s
neighbor %s description %s
neighbor %s shut
address-family ipv6
neighbor %s activate
neighbor %s send-community
neighbor %s maximum-routes %s
neighbor %s route-map %s-INv6 in
neighbor %s route-map %s-OUTv6 out
""" % (config['ipms']['asn'],session_address,asn.strip("AS"),session_address,peer['description'],session_address,session_address,session_address,session_address,peer['ipv6_limit'],session_address,asn,session_address,asn)

                           routemap = """
route-map %s-OUTv6 permit 10
 match community SUPERNETS
!
route-map %s-OUTv6 permit 20
 match community CUSTOMER
!
route-map %s-OUTv6 permit 30
 match community PEERS
!
route-map %s-OUTv6 permit 40
 match community TRANSIT
!
""" % (asn,asn,asn,asn)
                           routemap += """
route-map %s-INv6 permit 9
 match as-path %s
 match ipv6 address prefix-list blackhole
 match community NULL-ROUTE
!""" % (asn,asn)
                           routemap += """
route-map %s-INv6 permit 10
 match as-path %s
 match ipv6 address prefix-list %s-ipv6-in
 set local-preference 120
 set weight 10
 set community %s:101 %s:%s
!""" % (asn,asn,asn,config['ipms']['asn'],config['ipms']['asn'],asn.strip("AS"))

                          # Check whether we already have this route map
                           if routemap not in maps:
                               maps += routemap

                       #########################
                       # Build IPv4            #
                       #########################

             if '.' in session_address:
                           bgppeers += """
router bgp %s
neighbor %s remote-as %s
neighbor %s description %s
neighbor %s shut
address-family ipv4
neighbor %s activate
neighbor %s send-community
neighbor %s maximum-routes %s
neighbor %s route-map %s-IN in
neighbor %s route-map %s-OUT out
""" % (config['ipms']['asn'],session_address,asn.strip("AS"),session_address,peer['description'],session_address,session_address,session_address,session_address,peer['ipv4_limit'],session_address,asn,session_address,asn)
                           routemap = """
route-map %s-OUT permit 10
 match community SUPERNETS
!
route-map %s-OUT permit 20
 match community CUSTOMER
!
route-map %s-OUT permit 30
 match community PEERS
!
route-map %s-OUT permit 40
 match community TRANSIT
!
""" % (asn,asn,asn,asn)

                           routemap += """
route-map %s-IN permit 9
 match as-path %s
 match ip address prefix-list blackhole
 match community NULL-ROUTE
!""" % (asn,asn)

                           routemap += """
route-map %s-IN permit 10
 match as-path %s
 match ip address prefix-list %s-ipv4-in
 set local-preference 120
 set weight 10
 set community %s:101 %s:%s
!""" % (asn,asn,asn,config['ipms']['asn'],config['ipms']['asn'],asn.strip("AS"))

                          # Check whether we already have this route map
                           if routemap not in maps:
                               maps += routemap

             if row['password']:
                           bgppeers += """neighbor %s password %s
""" % (session_address,row['password'])


    except mdb.Error as e:
         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)
    finally:
         if con:
             con.close()

    configlocation = config['ipms']['bgp_directory'] + router['hostname'] + '/config/'


    # First check if the router folder exists, if not we create it
    if not os.path.isdir(configlocation):
        try:
             os.makedirs(configlocation)
        except OSError:
             print("Error: Something went wrong, cannot create router director")
             sys.exit(2)
    if Active is True:
        maps += """

ip prefix-list %s-ipv4-in source flash:/bgp/%s.ipv4
ipv6 prefix-list %s-ipv6-in source flash:/bgp/%s.ipv6
ip as-path access-list %s source flash:/bgp/%s.aspaths
""" % (asn,asn,asn,asn,asn,asn)

        f = open(configlocation + asn,'w')
        f.write(maps)
        f.write(bgppeers)
        f.close()

        log("info","Built peer configuration for " + asn + " sucessfully")

############################
# Lets call main() and run #
############################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

