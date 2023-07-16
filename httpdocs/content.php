<?php

/* 
 * Copyright (c) 2022, jgreig
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 * * Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */


require('libs/Smarty.class.php');
require("includes/class.init.php");
include("includes/class.routers.php");
include("includes/class.routertypes.php");
include("includes/class.bgppeers.php");
include("includes/class.bgpsessions.php");

$peermanager = new peermanager;

if ($peermanager->isloggedin){
    switch($_REQUEST['function']){
        case "viewbgppeers":
            // Lets fetch any alerts that need to be displayed to the user first
            $peermanager->assign('alerts', $peermanager->alert_notifications);
            // Now acknowledge them so they don't keep showing after they've been seen
            $peermanager->log_acknowledge_last_alerts();            
            
            // Output the BGP Peer content page            
            $bgppeers = new bgppeers;
            $peermanager->assign('bgppeers', $bgppeers->peers);
            $peermanager->assign('settings', $peermanager->settings);
            $peermanager->outputAdminArea('bgppeers.tpl');
            break;
        
        case "addbgppeer":
            // Process adding bgp peers            
            $bgppeers = new bgppeers;
            $bgppeers->addPeer(array('asn' => postVar('asn'),
                                'description' => postVar('description'),
                                'import' => postVar('import'),
                                'export' => postVar('export'),
                                'ipv4_limit' => postVar('ipv4_limit'),
                                'ipv6_limit' => postVar('ipv6_limit')));
            break;        
        
        case "updatebgppeer":
            // Process adding bgp peers            
            $bgppeers = new bgppeers(intval(postVar('peerid')));
            $bgppeers->updatePeer(array('description' => postVar('description'),
                                'import' => postVar('import'),
                                'export' => postVar('export'),
                                'ipv4_limit' => postVar('ipv4_limit'),
                                'ipv6_limit' => postVar('ipv6_limit')));
            break;                
        
        case "deletebgppeer":
            // Process adding routers   
            $bgppeers = new bgppeers(intval(getVar('peerid')));
            $bgppeers->deletePeer();
            break;         
        
        case "buildfilters":
            // Process adding routers   
            $bgppeers = new bgppeers(intval(getVar('peerid')));
            $bgppeers->buildFilters();
            break;                 

        case "viewbgpsessions":
            // Lets fetch any alerts that need to be displayed to the user first
            $peermanager->assign('alerts', $peermanager->alert_notifications);
            // Now acknowledge them so they don't keep showing after they've been seen
            $peermanager->log_acknowledge_last_alerts();            
            
            // Output the BGP Session content page            
            $bgpsessions = new bgpsessions;
            $bgppeers = new bgppeers;
            $routers = new routers;
            $peermanager->assign('routers', $routers->routers);            
            $peermanager->assign('bgpsessions', $bgpsessions->sessions);
            $peermanager->assign('bgppeers', $bgppeers->peers);            
            $peermanager->outputAdminArea('bgpsessions.tpl');
            break;
        
        case "addbgpsession":
            // Process adding bgp session            
            $bgpsessions = new bgpsessions;
            $bgpsessions->addSession(array('peerid' => postVar('peerid'),
                                'address' => postVar('address'),
                                'password' => postVar('password'),
                                'type' => postVar('type'),
                                'routerid' => postVar('routerid')));
            break;      

        case "deletebgpsession":
            // Process deleting a session
            $bgpsessions = new bgpsessions(intval(getVar('sessionid')));
            $bgpsessions->deleteSession();
            break;       

        case "resetbgpsession":
            // Process resetting a session
            $bgpsessions = new bgpsessions(intval(getVar('sessionid')));
            $bgpsessions->resetSession();
            break;            
                
        
        case "viewrouters":
            // Lets fetch any alerts that need to be displayed to the user first
            $peermanager->assign('alerts', $peermanager->alert_notifications);
            // Now acknowledge them so they don't keep showing after they've been seen
            $peermanager->log_acknowledge_last_alerts();            
            
            // Output the Router content page            
            $routers = new routers;
            $routertypes = new routertypes;
            $peermanager->assign('routers', $routers->routers);
            $peermanager->assign('routertypes', $routertypes->routertypes);
            $peermanager->outputAdminArea('routers.tpl');
            break;
        
        case "addrouter":
            // Process adding routers            
            $routers = new routers;
            $routers->addRouter(postVar('hostname'),intval(postVar('routertypeid')));
            break;
        
        case "deleterouter":
            // Process adding routers   
            $routers = new routers(intval(getVar('routerid')));
            $routers->deleteRouter();
            break;        
        
        case "viewlogs":
            $peermanager->getLogs();
            $peermanager->assign('logs', $peermanager->getLogs());
            $peermanager->outputAdminArea('logs.tpl');
            break;

        case "updatesettings":
            $peermanager->settings = $_POST;
            $peermanager->updateSettings();
            break;
        
        case "viewsettings":
            // Lets fetch any alerts that need to be displayed to the user first
            $peermanager->assign('alerts', $peermanager->alert_notifications);
            // Now acknowledge them so they don't keep showing after they've been seen
            $peermanager->log_acknowledge_last_alerts();     
            
            $peermanager->assign('settings', $peermanager->settings);
            $peermanager->outputAdminArea('settings.tpl');
            break;        
        
        default:
            $peermanager->outputAdminArea('index.tpl');
            break;
    }
} else {
    echo '<meta http-equiv="Refresh" content="0;/index.php">';
}
exit(0);


?>
