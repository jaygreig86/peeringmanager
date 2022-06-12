<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

class routers extends peermanager {
    public $routers;
    private $routerid;
        
    function __construct(int $routerid = 0)
    {
       parent::__construct();
       if ($routerid)$this->routerid = $routerid;
       $this->routers = $this->getRouters();
    }
    
    private function getRouters()
    {
        $pdo = parent::dbconnect();
        $q = $pdo->prepare("SELECT * FROM ipms_routers LEFT JOIN ipms_routertypes ON ipms_routers.routertypeid = ipms_routertypes.routertypeid");
        $q->execute();
        $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
        $pdo = null;

        return $resultarray;	
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