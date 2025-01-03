#!/usr/bin/env python

import MySQLdb as mdb
import configparser
import ipaddr
import sys
import subprocess
import os
import re

class peermanager:
    
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
        "PRIVATE": [ipaddr.IPNetwork('92.60.104.0/24'),ipaddr.IPNetwork('45.146.144.31/32'),ipaddr.IPNetwork('45.146.144.32/32')]


    }
    irr = "whois.radb.net"
    ############################
    # Config Section End       #
    ############################


    # init empty config var.  This is treated as a global and used throughout
    config = False
    available_exports = False

    def __init__(self,config_location = ""):
         if (config_location == ""):
            config_location = os.path.abspath(os.getcwd()).rstrip("/bgp") + "/httpdocs/configs/global.conf"
         self.config  = configparser.ConfigParser()
         self.config.sections()

         # Try reading the config file

         try:
            self.config.read(config_location)
         except configparser.Error as e:
            self.log("Error","Error reading config %d: %s\r\n" % (e.args[0], e.args[1]))
            sys.exit(1)
         if "ipms" not in self.config:
            print("Error: Failed to retrieve configuration file")
            sys.exit(1)


         self.available_exports = [i.strip("'") for i in self.config['ipms'].get('exports').split(",")]

    ############################
    # Logging function         #
    ############################

    def log(self,type = "info",message = ""):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

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
    # Run build_peers()        #
    ############################

    def build_peers(self,run_on_only = ""):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             # Are we running this on one router or all routers?

             if len(run_on_only):
                  cur.execute("SELECT * FROM ipms_routers WHERE hostname = '%s'" % (run_on_only))
             else:
                  cur.execute("SELECT * FROM ipms_routers")
             routers = cur.fetchall()

             for router in routers:
                 self.log("info","Building peer config for %s" % (router['hostname']))
                 cur.execute("SELECT * FROM ipms_bgppeers")
                 peers = cur.fetchall()
                 for peer in peers:
                     self.build_peer_configuration(peer,router)

         except mdb.Error as e:

             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)

         finally:

             if con:
                 con.close()

    ############################
    # Run Build Filters        #
    ############################

    def build_filters(self,run_on_only = "",peerid = ""):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             # Are we running this on one router or all routers

             if len(run_on_only):
                  cur.execute("SELECT * FROM ipms_routers WHERE hostname = '%s'" % (run_on_only))
             else:
                  cur.execute("SELECT * FROM ipms_routers")

             routers = cur.fetchall()

             for router in routers:
                 if len(peerid):
                      cur.execute("SELECT * FROM ipms_bgppeers WHERE peerid IN (SELECT peerid FROM ipms_bgpsessions WHERE routerid = %d) AND peerid = %s" % (router['routerid'],peerid))
                 else:
                      cur.execute("SELECT * FROM ipms_bgppeers WHERE peerid IN (SELECT peerid FROM ipms_bgpsessions WHERE routerid = %d)" % (router['routerid']))
                 peers = cur.fetchall()
                 for peer in peers:
                     self.build_filter_configuration(peer,router)

         except mdb.Error as e:

             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)

         finally:

             if con:
                 con.close()
             return 0

    ############################
    # Run Build Customers      #
    ############################

    def build_customers(self,run_on_only = ""):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             # Are we running this on one router or all routers

             if len(run_on_only):
                  cur.execute("SELECT * FROM ipms_routers WHERE hostname = '%s'" % (run_on_only))
             else:
                  cur.execute("SELECT * FROM ipms_routers")
             routers = cur.fetchall()

             for router in routers:
                 self.log("info","Building customer config for %s" % (router['hostname']))
                 cur.execute("SELECT * FROM ipms_bgppeers")
                 peers = cur.fetchall()
                 for peer in peers:
                     self.build_customer_configuration(peer,router)

         except mdb.Error as e:

             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)

         finally:

             if con:
                 con.close()

    ###################################
    # Validate the session IP address #
    ###################################

    def validate_session(self,session):
        # We first perform a number of validation checks before we build any configuration
        # 1) is the session address a valid IP
        # 2) Is the session address part of a valid internet exchange
        # 3) Is the export valid?
        # If all these pass, we then build the configuration

        try:
            # Check that the IP address retrieved from the database is a valid IP
            peer_ip = ipaddr.IPAddress(session['address'].decode('ascii'))
        except ValueError:
            self.log("Error","%s in %s is not a valid IP" % (session['address'].decode('ascii'), session['asn']))
            sys.exit(2)

        valid = False
        for exchange in self.connected_exchanges:
            for network in self.connected_exchanges[exchange]:
                 if peer_ip in network:
                      if session['export'] in self.available_exports:
                           valid = True

        if not valid:
             return False
             # We flag an invalid peer on the peermanager and log to the database
        else:
             return True

    ###################################
    # Validate the customer IP        #
    ###################################

    def validate_customer(self,session):
        # We first perform a number of validation checks before we build any configuration
        # 1) is the session address a valid IP
        # If all these pass, we then build the configuration

        try:
            # Check that the IP address retrieved from the database is a valid IP
            peer_ip = ipaddr.IPAddress(session['address'].decode('ascii'))
        except ValueError:
            self.log("Error","%s in %s is not a valid IP" % (session['address'].decode('ascii'), session['asn']))
            sys.exit(2)

        return True


    ###################################
    # Build peer configuration        #
    ###################################

    def build_peer_configuration(self,peer,router):
        asn = "AS" + str(peer['asn'])

        # We need to parse the AS-SET import line as peeringdb sometimes has extra
        # details there that we don't need at the moment
        peer_import_raw = peer['import']
        peer_import = re.sub('.*::','',peer_import_raw)
        
        con = None
        try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             cur.execute("SELECT * FROM ipms_bgpsessions LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgppeers.peerid = %d AND ipms_bgpsessions.routerid = %d AND type = 'peer'" % (peer['peerid'],router['routerid']))

             rows = cur.fetchall()

             bgppeers = ""  # Variable that will hold the BGP Peer config before it's pushed out to file
             maps = ""      # Variable that will hold the route maps before it's pushed out to file
             Active = False
             for row in rows:
                 session_address = row['address'].decode('ascii')
                 if self.validate_session(row) is not True:
                   self.log("Error", "The address is not valid.  We cannot reach %s" % (session_address))
                   continue
                 self.log("Info","Building peer config for %s - %s" % (asn,session_address))

                 # We set active to True because there's an active session for this peer
                 # on the current router.  We do not want to write config for a peer
                 # that does not exist on this router.
                 Active = True

                 for exchange in self.connected_exchanges:
                   for network in self.connected_exchanges[exchange]:
                       if ipaddr.IPAddress(session_address) in network:
                           if ':' in session_address:
                               bgppeers += """
    router bgp %s
    neighbor %s remote-as %s
    neighbor %s description %s
    !neighbor %s shut
    neighbor %s send-community
    neighbor %s maximum-routes %s
    address-family ipv6
    neighbor %s activate
    neighbor %s route-map %s-%s-INv6 in
    neighbor %s route-map PEER-%s-OUTv6 out
    """ % (self.config['ipms']['asn'],session_address,asn.strip("AS"),session_address,peer['description'],session_address,session_address,session_address,peer['ipv6_limit'],session_address,session_address,asn,exchange,session_address,exchange)

                               routemap = """
    route-map %s-%s-INv6 permit 10
     match as-path %s
     match ipv6 address prefix-list %s-ipv6-in
     sub-route-map GENERIC-%s-INv6
    !""" % (asn,exchange,asn,asn,exchange)
                               if routemap not in maps:
                                   maps += routemap

                           if '.' in session_address:
                               bgppeers += """
    router bgp %s
    neighbor %s remote-as %s
    neighbor %s description %s
    !neighbor %s shut
    neighbor %s send-community
    neighbor %s maximum-routes %s
    address-family ipv4
    neighbor %s activate
    neighbor %s route-map %s-%s-IN in
    neighbor %s route-map PEER-%s-OUT out
    """ % (self.config['ipms']['asn'],session_address,asn.strip("AS"),session_address,peer['description'],session_address,session_address,session_address,peer['ipv4_limit'],session_address,session_address,asn,exchange,session_address,exchange)

                               routemap = """
    route-map %s-%s-IN permit 10
     match as-path %s
     match ip address prefix-list %s-ipv4-in
     sub-route-map GENERIC-%s-IN
    !""" % (asn,exchange,asn,asn,exchange)
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

        configlocation = self.config['ipms']['bgp_directory'] + router['hostname'] + '/config/'


        # First check if the router folder exists, if not we create it
        if not os.path.isdir(configlocation):
            try:
                 os.makedirs(configlocation)
            except OSError:
                 print("Error: Something went wrong, cannot create router director")
                 sys.exit(2)
        if Active is True:
            maps += """
    bash touch /mnt/flash/bgp/%s.ipv4
    bash touch /mnt/flash/bgp/%s.ipv6
    bash touch /mnt/flash/bgp/%s.aspaths
    ip prefix-list %s-ipv4-in source flash:/bgp/%s.ipv4
    ipv6 prefix-list %s-ipv6-in source flash:/bgp/%s.ipv6
    ip as-path access-list %s source flash:/bgp/%s.aspaths
    """ % (asn,asn,asn,asn,asn,asn,asn,asn,asn)

            f = open(configlocation + asn,'w')
            f.write("conf t")
            f.write(maps)
            f.write(bgppeers)
            f.close()

            self.log("info","Built peer configuration for " + asn + " sucessfully")

    ###################################
    # Build Filters                   #
    ###################################

    def build_filter_configuration(self,peer,router):
        asn = "AS" + str(peer['asn'])
        configlocation = self.config['ipms']['bgp_directory'] + router['hostname'] + '/config/'
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
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

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
             
             print("Info: Generating Filters using IRR %s" % (self.irr))
             for row in rows:
                session_address = row['address'].decode('ascii')
                if row['type'] == "peer":
                   if self.validate_session(row) is not True:
                     self.log("Error","The address is not valid.  We cannot reach %s" % (session_address))
                     continue
                elif row['type'] == "customer":
                   if self.validate_customer(row) is not True:
                     self.log("Error","The address is not valid.  We cannot reach %s" % (session_address))
                     continue
                if '.' in session_address and ActiveV4 == False:
                    try:
                        print("Generating IPv4 prefix lists for: %s" % (asn))
                        cmd = "/usr/bin/env bgpq4 -h %s  -A -4 -m 24 -R 24 %s | sed 's/ip prefix-list NN //'|grep -v 'no ip prefix-list NN'> %s%s.ipv4" % (self.irr,peer_import,configlocation,asn)
                        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                    except ValueError as err:
                        print("ERROR: %s" % (err))
                        sys.exit(2)
                    ActiveV4 = True
                if ':' in session_address and ActiveV6 == False:
                    try:
                        print("Generating IPv6 prefix lists for: %s" % (asn))
                        cmd = "/usr/bin/env bgpq4 -h %s -A -6 -m 48 %s | sed 's/ipv6 prefix-list NN //'|grep -v 'no ipv6 prefix-list NN'> %s%s.ipv6" % (self.irr,peer_import,configlocation,asn)
                        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                    except ValueError as err:
                        print("ERROR: %s" %s (err))
                        sys.exit(2)
                    ActiveV6 = True
                if ActivePeer == False:
                    try:
                        print("Generating AS Path lists for: %s" % (asn))
                        cmd = "/usr/bin/env bgpq4 -h %s -f %s %s | sed 's/ip as-path access-list NN //'| grep -v 'no ip as-path' | sed 's/(_\[0-9\]+)/_./' > %s%s.aspaths" % (self.irr,asn.strip("AS"), peer_import,configlocation,asn)
                        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                    except ValueError as err:
                        print("ERROR: %s" %s (err))
                        sys.exit(2)
                    ActivePeer = True
             self.log("info","Filters updated for " + asn + " successfully")
             return 0

        except mdb.Error as e:
             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)
        finally:
             if con:
                 con.close()

    ###################################
    # Build customer configuration    #
    ###################################

    def build_customer_configuration(self,peer,router):
        asn = "AS" + str(peer['asn'])

        # We need to parse the AS-SET import line as peeringdb sometimes has extra
        # details there that we don't need at the moment
        peer_import_raw = peer['import']
        peer_import = re.sub('.*::','',peer_import_raw)

        con = None
        try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             cur.execute("SELECT * FROM ipms_bgpsessions LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgppeers.peerid = %d AND ipms_bgpsessions.routerid = %d AND ipms_bgpsessions.type = 'customer'" % (peer['peerid'],router['routerid']))

             rows = cur.fetchall()

             bgppeers = ""  # Variable that will hold the BGP Peer config before it's pushed out to file
             maps = ""      # Variable that will hold the route maps before it's pushed out to file
             Active = False
             for row in rows:
                 session_address = row['address'].decode('ascii')
                 if self.validate_customer(row) is not True:
                   self.log("Error","The address is not valid.  We cannot reach %s" % (session_address))
                   continue
                 self.log("Info","Building customer config for %s - %s" % (asn,session_address))

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
    neighbor %s send-community
    !neighbor %s shut
    address-family ipv6
    neighbor %s activate
    neighbor %s maximum-routes %s
    neighbor %s route-map %s-INv6 in
    neighbor %s route-map %s-OUTv6 out
    """ % (self.config['ipms']['asn'],session_address,asn.strip("AS"),session_address,peer['description'],session_address,session_address,session_address,session_address,peer['ipv6_limit'],session_address,asn,session_address,asn)
                               routemap = ""
                               if row['send'] == "full" or row['send'] == "customers_peers" or row['send'] == "customers_peers_default" or row['send'] == "customers_default" or row['send'] == "customers_only":
                                   routemap += """
    route-map %s-OUTv6 permit 10
     match community SUPERNETS
    !
    route-map %s-OUTv6 permit 20
     match community CUSTOMER
    !""" % (asn,asn)
                               if row['send'] == "full" or row['send'] == "customers_peers" or row['send'] == "customers_peers_default":
                                   routemap += """
    route-map %s-OUTv6 permit 30
     match community PEERS
    !""" % (asn)
                               if row['send'] == "full":
                                   routemap += """
    route-map %s-OUTv6 permit 40
     match community TRANSIT
    !
    """ % (asn)
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
    !""" % (asn,asn,asn,self.config['ipms']['asn'],self.config['ipms']['asn'],asn.strip("AS"))

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
    neighbor %s send-community
    !neighbor %s shut
    address-family ipv4
    neighbor %s activate
    neighbor %s maximum-routes %s
    neighbor %s route-map %s-IN in
    neighbor %s route-map %s-OUT out
    """ % (self.config['ipms']['asn'],session_address,asn.strip("AS"),session_address,peer['description'],session_address,session_address,session_address,session_address,peer['ipv4_limit'],session_address,asn,session_address,asn)
                               routemap = ""
                               if row['send'] == "full" or row['send'] == "customers_peers" or row['send'] == "customers_peers_default" or row['send'] == "customers_default" or row['send'] == "customers_only":
                                   routemap += """
    route-map %s-OUT permit 10
     match community SUPERNETS
    !
    route-map %s-OUT permit 20
     match community CUSTOMER
    !""" % (asn,asn)
                               if row['send'] == "full" or row['send'] == "customers_peers" or row['send'] == "customers_peers_default":
                                   routemap += """
    route-map %s-OUT permit 30
     match community PEERS
    !""" % (asn)
                               if row['send'] == "full":
                                   routemap += """
    route-map %s-OUT permit 40
     match community TRANSIT
    !
    """ % (asn)

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
    !""" % (asn,asn,asn,self.config['ipms']['asn'],self.config['ipms']['asn'],asn.strip("AS"))

                              # Check whether we already have this route map
                               if routemap not in maps:
                                   maps += routemap

                 if row['send'] == "default_only" or row['send'] == "customers_default" or row['send'] == "customers_peers_default":
                               bgppeers += """neighbor %s default-originate always
    """ % (session_address)

                 if row['password']:
                               bgppeers += """neighbor %s password %s
    """ % (session_address,row['password'])


        except mdb.Error as e:
             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)
        finally:
             if con:
                 con.close()

        configlocation = self.config['ipms']['bgp_directory'] + router['hostname'] + '/config/'


        # First check if the router folder exists, if not we create it
        if not os.path.isdir(configlocation):
            try:
                 os.makedirs(configlocation)
            except OSError:
                 print("Error: Something went wrong, cannot create router director")
                 sys.exit(2)
        if Active is True:
            maps += """
    bash touch /mnt/flash/bgp/%s.ipv4
    bash touch /mnt/flash/bgp/%s.ipv6
    bash touch /mnt/flash/bgp/%s.aspaths
    ip prefix-list %s-ipv4-in source flash:/bgp/%s.ipv4
    ipv6 prefix-list %s-ipv6-in source flash:/bgp/%s.ipv6
    ip as-path access-list %s source flash:/bgp/%s.aspaths
    """ % (asn,asn,asn,asn,asn,asn,asn,asn,asn)

            f = open(configlocation + asn,'w')
            f.write("conf t")
            f.write(maps)
            f.write(bgppeers)
            f.close()

            self.log("info","Built peer configuration for " + asn + " sucessfully")

    ############################
    # Reconfigure Peer         #
    ############################

    def reconfigure_peer(self,job = None):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])
             cur = con.cursor(mdb.cursors.DictCursor)
             cur.execute("SELECT ipms_bgpsessions.peerid,asn,ipv4_limit,ipv6_limit,description,hostname,type,ipms_routers.routerid,import FROM ipms_bgpsessions LEFT JOIN ipms_routers ON ipms_bgpsessions.routerid = ipms_routers.routerid LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgpsessions.peerid = %s GROUP BY hostname" % (job['data']))
             peers = cur.fetchall()
             for peer in peers:
                 if peer['type'] == "customer":
                     self.build_customer_configuration(peer,router={'hostname':peer['hostname'],'routerid':peer['routerid']})
                 elif peer['type'] == "peer":
                     self.build_peer_configuration(peer,router={'hostname':peer['hostname'],'routerid':peer['routerid']})
                 try:
                     self.log("Info", "Pushing config changes via clogin for peer AS%s to %s" % (peer['asn'],peer['hostname']))
                     cmd = "/usr/local/rancid/bin/clogin -x %s%s/config/AS%s %s" % (self.config['ipms']['bgp_directory'],peer['hostname'],peer['asn'],peer['hostname'])
                     self.log("Info", "Command - %s" % (cmd))
                     response = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT)
                     self.log("Info","Peer AS%s on %s reconfigured" % (peer['asn'],peer['hostname']))
                 except ValueError as err:
                     self.log("Error","Error reconfiguring peer AS%s on %s - %s" % (peer['asn'],peer['hostname'],err))
                 except subprocess.CalledProcessError as err:
                     self.log("Error","Error reconfiguring peer AS%s on %s - %s" % (peer['asn'],peer['hostname'],err.output))
                 except FileNotFoundError as err:
                     self.log("Error","Error reconfiguring peer AS%s on %s - %s" % (peer['asn'],peer['hostname'],err.strerror))

         except mdb.Error as e:
             self.log("Error", "Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)

         finally:
             if con:
                 con.close()
             return 0

    ############################
    # Reset Session            #
    ############################

    def reset_session(self,job = None):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])
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
                     self.log("Error","Error resetting session %s on %s - %s" % (session_address,session['hostname'],err))
                 else:
                     self.log("Info","Session %s on %s reset" % (session_address,session['hostname']))
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

    def update_operation(self,job):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])
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
    # Push Filters             #
    ############################

    def push_filters(self,peerid = ""):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             cur.execute("SELECT asn,hostname FROM ipms_bgpsessions LEFT JOIN ipms_routers ON ipms_bgpsessions.routerid = ipms_routers.routerid LEFT JOIN ipms_bgppeers ON ipms_bgppeers.peerid = ipms_bgpsessions.peerid WHERE ipms_bgpsessions.peerid = %s" % (peerid))

             dataset = cur.fetchall()

             for data in dataset:
                  asn = "AS" + str(data['asn'])
                  files = self.config['ipms']['bgp_directory'] + data['hostname'] + '/config/' + asn + ".*"
                  
                  # Push the filter files to the router
                  try:
                      self.log("Info","SSH Copying files %s" % (files))
                      cmd = "/usr/bin/scp %s rancid@%s:/mnt/flash/bgp/" % (files,data['hostname'])
                      response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                      self.log("Info","SSH Copying successful")
                  except ValueError as err:
                      self.log("Error","Error copy files for peer AS%s on %s - %s" % (data['asn'],data['hostname'],err))
                  except subprocess.CalledProcessError as err:
                      self.log("Error","Error copy files for peer AS%s on %s - %s" % (data['asn'],data['hostname'],err.output))
                  except FileNotFoundError as err:
                      self.log("Error","Error copy files for peer AS%s on %s - %s" % (data['asn'],data['hostname'],err.strerror))

                  # Need to refresh the filters
                  try:
                      self.log("Info","Refreshing IPv4 Filters %s" % (files))
                      cmd = "/usr/local/rancid/bin/clogin -c 'refresh ip prefix-list %s-ipv4-in' %s" % (asn,data['hostname'])
                      response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                      self.log("Info","IPv4 Filter refresh successful")
                      self.log("Info","Refreshing IPv4 Filters %s" % (files))
                      cmd = "/usr/local/rancid/bin/clogin -c 'refresh ip prefix-list %s-ipv6-in' %s" % (asn,data['hostname'])
                      response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                      self.log("Info","IPv6 Filter refresh successful")
                      self.log("Info","Refreshing AS Path Filters %s" % (files))
                      cmd = "/usr/local/rancid/bin/clogin -c 'refresh ip as-path access-list %s' %s" % (asn,data['hostname'])
                      response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
                      self.log("Info","AS Path Filter refresh successful")
                  except ValueError as err:
                      self.log("Error","Error refreshing filters for peer AS%s on %s - %s" % (data['asn'],data['hostname'],err))
                  except subprocess.CalledProcessError as err:
                      self.log("Error","Error refreshing filters for peer AS%s on %s - %s" % (data['asn'],data['hostname'],err.output))
                  except FileNotFoundError as err:
                      self.log("Error","Error refreshing filters for peer AS%s on %s - %s" % (data['asn'],data['hostname'],err.strerror))
         except mdb.Error as e:

             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)

         finally:

             if con:
                 con.close()
             return 0

    ############################
    # Run Tasks                #
    ############################

    def run_tasks(self):
         con = None
         try:
             con = mdb.connect(self.config['ipms']['db_host'], self.config['ipms']['db_user'], self.config['ipms']['db_pass'], self.config['ipms']['db_name'])

             cur = con.cursor(mdb.cursors.DictCursor)

             # Get the last 10 minutes of operations

             cur.execute("SELECT * FROM ipms_operations WHERE status = 'Pending' AND date >= now() - INTERVAL 10 minute")

             jobs = cur.fetchall()

             for job in jobs:
                 resp = -1
                 if job['job'] == 'update_peer':
                      resp = self.reconfigure_peer(job)
                 elif job['job'] == 'reset_session':
                      resp = self.reset_session(job)
                 elif job['job'] == 'build_filters':
                      resp = self.build_filters("",job['data'])
                 elif job['job'] == 'push_filters':
                      resp = self.push_filters(job['data'])
                 if resp == 0:
                      self.update_operation(job)
         except mdb.Error as e:

             print("Error %d: %s" % (e.args[0], e.args[1]))
             sys.exit(1)

         finally:

             if con:
                 con.close()
