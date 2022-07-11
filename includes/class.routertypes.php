<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

class routertypes extends peermanager {
    public $routertypes;
    
        
    function __construct()
    {
       parent::__construct();
      $this->getRouterTypes();
    }
    
    private function getRouterTypes()
    {
        $pdo = parent::dbconnect();
        $q = $pdo->prepare("SELECT * FROM ipms_routertypes");
        $q->execute();
        $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
        $pdo = null;
        foreach ($resultarray as $result) {
            $this->routertypes[$result['routertypeid']] = $result;
        }

        return;
    }
}