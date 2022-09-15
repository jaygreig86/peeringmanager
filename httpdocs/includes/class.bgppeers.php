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
