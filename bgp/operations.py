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


# init empty config var.  This is treated as a global and used throughout
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
         print("%s: %s" % (type,message))
     except mdb.Error as e:

         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)

     finally:

         if con:
             con.close()

############################
# Reconfigure Peer         #
############################

def reconfigure_peer(job = None):
     global config
     con = None
     try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])
         cur = con.cursor(mdb.cursors.DictCursor)
         cur.execute("SELECT asn,hostname FROM ipms_bgpsessions LEFT JOIN ipms_routers ON ipms_bgpsessions.routerid = ipms_routers.routerid LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgpsessions.peerid = %s GROUP BY hostname" % (job['data']))
         peers = cur.fetchall()
         for peer in peers:
             try:
                 print("Running for %s %s" % (peer['asn'],peer['hostname']))
                 cmd = "/usr/local/rancid/bin/clogin -x bgp/%s/config/AS%s %s" % (peer['hostname'],peer['asn'],peer['hostname'])
                 response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
             except ValueError as err:
                 log("Error","Error reconfiguring peer AS%s on %s - %s" % (peer['asn'],peer['hostname'],err))
             else:
                 log("Info","Peer AS%s on %s reconfigured" % (peer['asn'],peer['hostname']))
     except mdb.Error as e:

         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)

     finally:

         if con:
             con.close()
         return 0

############################
# Reset Session            #
############################

def reset_session(job = None):
     global config
     con = None
     try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])
         cur = con.cursor(mdb.cursors.DictCursor)
         cur.execute("SELECT address,hostname,vendor FROM ipms_bgpsessions LEFT JOIN ipms_routers ON ipms_routers.routerid = ipms_bgpsessions.routerid LEFT JOIN ipms_routertypes ON ipms_routers.routertypeid = ipms_routertypes.routertypeid WHERE sessionid = %s" % (job['data']))
         sessions = cur.fetchall()
         for session in sessions:
             session_address = session['address'].decode('ascii')
             try:
                 print("Running for %s %s" % (session_address,session['hostname']))
                 if ':' in session_address:
                     cmd = "/usr/local/rancid/bin/clogin -c 'clear ipv6 bgp %s' %s" % (session_address,session['hostname'])
                 else:
                     cmd = "/usr/local/rancid/bin/clogin -c 'clear ip bgp %s' %s" % (session_address,session['hostname'])
                 response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
             except ValueError as err:
                 log("Error","Error resetting session %s on %s - %s" % (session_address,session['hostname'],err))
             else:
                 log("Info","Session %s on %s reset" % (session_address,session['hostname']))
     except mdb.Error as e:

         print("Error %d: %s" % (e.args[0], e.args[1]))
         sys.exit(1)

     finally:

         if con:
             con.close()
         return 0

############################
# Update Operation         #
############################

def update_operation(job):
     global config
     con = None
     try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])
         cur = con.cursor(mdb.cursors.DictCursor)
         cur.execute("UPDATE ipms_operations SET status = 'Completed' WHERE opid = %s" % (job['opid']))
         con.commit()
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
     global available_exports
     config  = configparser.ConfigParser()
     config.sections()

     # Try reading the config file

     try:
        config.read(config_location)
     except configparser.Error as e:
        log("Error","Error reading config %d: %s\r\n" % (e.args[0], e.args[1]))
        sys.exit(1)

     available_exports = [i.strip("'") for i in config['ipms'].get('exports').split(",")]

     con = None
     try:
         con = mdb.connect(config['ipms']['db_host'], config['ipms']['db_user'], config['ipms']['db_pass'], config['ipms']['db_name'])

         cur = con.cursor(mdb.cursors.DictCursor)

         # Get the last 10 minutes of operations

         cur.execute("SELECT * FROM ipms_operations WHERE status = 'Pending' AND date >= now() - INTERVAL 10 minute")

         jobs = cur.fetchall()

         for job in jobs:
             resp = -1
             if job['job'] == 'update_peer':
                  resp = reconfigure_peer(job)
             elif job['job'] == 'reset_session':
                  resp = reset_session(job)
             if resp == 0:
                  update_operation(job)
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

