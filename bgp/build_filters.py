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

# Define the connected IXPs
# Any IP addresses not within these networks are not accepted

connected_exchanges = {
    "LINX2": [ipaddr.IPNetwork('195.66.236.0/22'),
              ipaddr.IPNetwork('2001:7F8:4:1::AFD6:1/64')],
        "LONAP": [ipaddr.IPNetwork('5.57.80.0/22'),
                ipaddr.IPNetwork('2001:7f8:17::/48')],
    "LINX1": [ipaddr.IPNetwork('195.66.224.0/21'),
              ipaddr.IPNetwork('2001:7F8:4::AFD6:1/64')],
    "PRIVATE": [ipaddr.IPNetwork('92.60.104.0/24')]


}
config_location = os.path.abspath(os.getcwd()).rstrip("/bgp") + "/httpdocs/configs/global.conf"

############################
# Config Section End       #
############################

# init empty config var
config = False
available_exports = False

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
     except mdb.Error as e:

         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)

     finally:

         if con:
             con.close()

############################
# Main function            #
############################

def main(run_on_only = ""):
     global config
     global available_exports
     config  = configparser.ConfigParser()
     config.sections()
     try:
        config.read(config_location)
     except configparser.Error as e:
        print("Error: reading config %d: %s\r\n" % (e.args[0], e.args[1]))
        sys.exit(1)

     if "ipms" not in config:
        print("Error: Failed to retrieve configuration file")
        sys.exit(1)

     available_exports = [i.strip("'") for i in config['ipms'].get('exports').split(",")]

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
             cur.execute("SELECT * FROM ipms_bgppeers WHERE peerid IN (SELECT peerid FROM ipms_bgpsessions WHERE routerid = %d)" % (router['routerid']))
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
    # 2) Is the session address part of a valid internet exchange
    # 3) Is the export valid?
    # If all these pass, we then build the configuration

    try:
        # Check that the IP address retrieved from the database is a valid IP
        peer_ip = ipaddr.IPAddress(session['address'].decode('ascii'))
    except ValueError:
        print("ERROR: %s in %s is not a valid IP" % (session['address'].decode('ascii'), session['asn']))
        sys.exit(2)

    valid = False
    for exchange in connected_exchanges:
        for network in connected_exchanges[exchange]:
             if peer_ip in network:
                  if session['export'] in available_exports:
                       valid = True
    if not valid:
         return False
         # We flag an invalid peer on the peermanager and log to the database
    else:
         return True

###################################
# Build the configuration         #
###################################

def build_configuration(peer,router):
    global config
    asn = "AS" + str(peer['asn'])
    configlocation = config['ipms']['bgp_directory'] + router['hostname'] + '/config/'
    # First check if the router folder exists, if not we create it
    if not os.path.isdir(configlocation):
        try:
             os.makedirs(configlocation)
        except OSError:
             print("Error: Something went wrong, cannot create router directory")
             sys.exit(2)



    # We need to parse the AS-SET import line as peeringdb sometimes has extra
    # details there that we don't need at the moment
    peer_import_raw = peer['import']
    peer_import = re.sub('.*::','',peer_import_raw)


    con = None
    try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])

         cur = con.cursor(mdb.cursors.DictCursor)

         cur.execute("SELECT * FROM ipms_bgpsessions LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgppeers.peerid = %d AND ipms_bgpsessions.routerid = %d" % (peer['peerid'],router['routerid']))

         rows = cur.fetchall()

         # We set these variables to false to begin with
         # Once an active session is found we set these to True
         # to achieve 2 goals.  1) to only build if there's a valid session
         # 2) to prevent it duplicating work (running the prefix gen for aspaths x times over)

         ActiveV4 = False
         ActiveV6 = False
         ActivePeer = False

         for row in rows:
             session_address = row['address'].decode('ascii')
             if validate_session(row) is not True:
               log("Error","The address is not valid.  We cannot reach %s" % (session_address))
               continue

             for exchange in connected_exchanges:
               for network in connected_exchanges[exchange]:
                   if ipaddr.IPAddress(session_address) in network:
                       if '.' in session_address and ActiveV4 == False:
                           try:
                               print("Generating IPv4 prefix lists for: %s" % (asn))
                               cmd = "/usr/bin/env bgpq3 -h rr.ntt.net -A -4 -m 24 -R 24 %s | sed 's/ip prefix-list NN //'|grep -v 'no ip prefix-list NN'> %s%s.ipv4" % (peer_import,configlocation,asn)
                               response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                           except ValueError as err:
                               print("ERROR: %s" % (err))
                               sys.exit(2)
                           ActiveV4 = True
                       if ':' in session_address and ActiveV6 == False:
                           try:
                               print("Generating IPv6 prefix lists for: %s" % (asn))
                               cmd = "/usr/bin/env bgpq3 -h rr.ntt.net -A -6 -m 48 %s | sed 's/ipv6 prefix-list NN //'|grep -v 'no ipv6 prefix-list NN'> %s%s.ipv6" % (peer_import,configlocation,asn)
                               response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                           except ValueError as err:
                               print("ERROR: %s" %s (err))
                               sys.exit(2)
                           ActiveV6 = True
                       if ActivePeer == False:
                           try:
                               print("Generating AS Path lists for: %s" % (asn))
                               cmd = "/usr/bin/env bgpq3 -h rr.ntt.net -3 -f %s %s | sed 's/ip as-path access-list NN //'| grep -v 'no ip as-path' | sed 's/(_\[0-9\]+)/_./' > %s%s.aspaths" % (asn.strip("AS"), peer_import,configlocation,asn)
                               response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                           except ValueError as err:
                               print("ERROR: %s" %s (err))
                               sys.exit(2)
                           ActivePeer = True
         log("info","Filters updated for " + asn + " successfully")
         return 0

    except mdb.Error as e:
         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)
    finally:
         if con:
             con.close()


############################
# Lets call main() and run #
############################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

