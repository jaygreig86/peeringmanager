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


class routers extends peermanager {
    public $routers;
    private $routerid;
        
    function __construct(int $routerid = 0)
    {
       parent::__construct();
       if ($routerid)$this->routerid = $routerid;
       $this->getRouters();
    }
    
    private function getRouters()
    {
        $pdo = parent::dbconnect();
        $q = $pdo->prepare("SELECT * FROM ipms_routers LEFT JOIN ipms_routertypes ON ipms_routers.routertypeid = ipms_routertypes.routertypeid");
        $q->execute();
        $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
        $pdo = null;
        foreach ($resultarray as $result) {
            $this->routers[$result['routerid']] = $result;
        }

        return;
    }
    
    public function addRouter(string $hostname,int $routertypeid)
    {
        //add router
        $pdo = parent::dbconnect();
        try {
            $q = $pdo->prepare("INSERT INTO ipms_routers (hostname,routertypeid) VALUES (:hostname,:routertypeid)");
            $q->bindParam(":hostname",$hostname);
            $q->bindParam(":routertypeid",$routertypeid);
            $q->execute();
        }
        catch (PDOException $e)
        {
            parent::log_insert('Failed to add router'.$hostname.' '.$e,"Error",1);
            return -1;
        }             
        unset($q);
        $pdo = null;            
        parent::log_insert('Router '.$hostname.' added',"info",1);
    }
    
    public function deleteRouter()
    {
        //delete router
        $pdo = parent::dbconnect();
        try {
            $q = $pdo->prepare("DELETE FROM ipms_routers WHERE routerid = :routerid");
            $q->bindParam(":routerid",$this->routerid);
            $q->execute();
        }
        catch (PDOException $e)
        {
            parent::log_insert('Failed to delete peer'.$this->peers[$this->peerid]['asn'].' '.$e,"Error",1);
            return -1;
        }        
        unset($q);
        $pdo = null;            
        parent::log_insert('Router '.$this->routers[$this->routerid]['hostname'].' deleted',"info",1);
    }
    public function updateRouter()
    {
        //delete stuff
    }     
}