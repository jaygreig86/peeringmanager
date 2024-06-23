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


class bgpsessions extends peermanager {
    public $sessions;
    private $sessionid;
        
    function __construct(int $sessionid = 0)
    {
       parent::__construct();
       if ($sessionid)$this->sessionid = $sessionid;
       $this->getSessions();
    }
    
    private function getSessions()
    {
        $pdo = parent::dbconnect();
        $q = $pdo->prepare("SELECT ipms_bgpsessions.*,asn,description,hostname FROM ipms_bgpsessions 
                LEFT JOIN ipms_bgppeers ON ipms_bgpsessions.peerid = ipms_bgppeers.peerid
                LEFT JOIN ipms_routers ON ipms_routers.routerid = ipms_bgpsessions.routerid");
        $q->execute();
        $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
        $pdo = null;
        foreach ($resultarray as $result) {
            $this->sessions[$result['sessionid']] = $result;
        }

        return;
    }
    
    public function addSession(array $data)
    {
        //add BGP Session
        $pdo = parent::dbconnect();
        try {    
            $q = $pdo->prepare("INSERT INTO ipms_bgpsessions (peerid,address,type,password,routerid,send) VALUES (:peerid,:address,:type,:password,:routerid,:send)");
            $q->bindParam(":peerid",$data['peerid']);
            $q->bindParam(":address",trim($data['address']));
            $q->bindParam(":type",$data['type']);
            $q->bindParam(":password",trim($data['password']));   
            $q->bindParam(":routerid",$data['routerid']);   
            $q->bindParam(":send",$data['send']);   
            $q->execute();
        }
        catch (PDOException $e)
        {
            parent::log_insert('Failed to add session'.$data['asn'].' '.$e,"Error",1);
            return -1;
        }
        unset($q);
        $pdo = null;            
        parent::log_insert('BGP Session '.$data['address'].' added',"info",1);
    }
    
    public function resetSession()
    {
        parent::addTask("reset_session",$this->sessionid);
        parent::log_insert('BGP Session '.$this->sessions[$this->sessionid]['address'].' reset initiated',"info",1);
    }     
    
    public function deleteSession()
    {
        //delete BGP Session
        $pdo = parent::dbconnect();
            
        try {  
            $q = $pdo->prepare("DELETE FROM ipms_bgpsessions WHERE sessionid = :sessionid");
            $q->bindParam(":sessionid",$this->sessionid);
            $q->execute();
        }
        catch (PDOException $e)
        {
            parent::log_insert('Failed to delete session'.$this->sessions[$this->sessionid]['address'].' '.$e,"Error",1);
            return -1;
        }        
        unset($q);
        $pdo = null;      
        parent::addTask("delete_session",$this->sessions[$this->sessionid]['address']);
        parent::log_insert('BGP Session '.$this->sessions[$this->sessionid]['address'].' deleted',"info",1);
    }  
}
