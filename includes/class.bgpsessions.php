<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

class bgpsessions extends peermanager {
    public $sessions;
    private $sessionid;
        
    function __construct(int $sessionid = 0)
    {
       parent::__construct();
       if ($sessionid)$this->sessionid = $sessionid;
       $this->sessions = $this->getSessions();
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

        return $resultarray;	
    }
    
    public function addSession(array $data)
    {
        //add BGP Session
        $pdo = parent::dbconnect();
        try {    
            $q = $pdo->prepare("INSERT INTO ipms_bgpsessions (peerid,address,type,password,routerid) VALUES (:peerid,:address,:type,:password,:routerid)");
            $q->bindParam(":peerid",$data['peerid']);
            $q->bindParam(":address",$data['address']);
            $q->bindParam(":type",$data['type']);
            $q->bindParam(":password",$data['password']);   
            $q->bindParam(":routerid",$data['routerid']);   
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
            parent::log_insert('Failed to delete session'.$this->sessions[$this->sesssionid]['address'].' '.$e,"Error",1);
            return -1;
        }        
        unset($q);
        $pdo = null;            
        parent::log_insert('BGP Session '.$this->sessions[$this->sesssionid]['address'].' deleted',"info",1);
    }  
}