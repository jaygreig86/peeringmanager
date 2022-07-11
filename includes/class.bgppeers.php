<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

class bgppeers extends peermanager {
    public $peers;
    private $peerid;
        
    function __construct(int $peerid = 0)
    {
       parent::__construct();
       if ($peerid)$this->peerid = $peerid;
       $this->getPeers();
    }
    
    private function getPeers()
    {
        $pdo = parent::dbconnect();
        $q = $pdo->prepare("SELECT * FROM ipms_bgppeers ORDER BY description");
        $q->execute();
        $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
        $pdo = null;
        foreach ($resultarray as $result) {
            $this->peers[$result['peerid']] = $result;
        }

        return;
    }
    
    public function addPeer(array $data)
    {
        //add peer
        $pdo = parent::dbconnect();
        try {
            $q = $pdo->prepare("INSERT INTO ipms_bgppeers (asn,description,import,export,ipv4_limit, ipv6_limit) VALUES (:asn,:description,:import,:export,:ipv4_limit,:ipv6_limit)");
            $q->bindParam(":asn",$data['asn']);
            $q->bindParam(":description",$data['description']);
            $q->bindParam(":import",$data['import']);
            $q->bindParam(":export",$data['export']);
            $q->bindParam(":ipv4_limit",$data['ipv4_limit']);
            $q->bindParam(":ipv6_limit",$data['ipv6_limit']);        
            $q->execute();
        }
        catch (PDOException $e)
        {
            parent::log_insert('Failed to add peer'.$data['asn'].' '.$e,"Error",1);
            return -1;
        }        
        unset($q);
        $pdo = null;            
        parent::log_insert('BGP Peer AS'.$data['asn'].' added',"info",1);
    }
    
    public function deletePeer()
    {
        //delete peer
        $pdo = parent::dbconnect();
        try {   
            $q = $pdo->prepare("DELETE FROM ipms_bgppeers WHERE peerid = :peerid");
            $q->bindParam(":peerid",$this->peerid);
            $q->execute();
        }
        catch (PDOException $e)
        {
            parent::log_insert('Failed to delete peer'.$this->peers[$this->peerid]['asn'].' '.$e,"Error",1);
            return -1;
        }
        unset($q);
        $pdo = null;            
        parent::addTask("delete_peer",$this->peers[$this->peerid]['asn']);
        parent::log_insert('BGP Peer '.$this->peers[$this->peerid]['asn'].' deleted',"info",1);
    }  
}