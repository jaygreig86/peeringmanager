<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

class peermanager extends smarty {
    public $db_link;
    public $username;
    public $userid;
    public $userip;
    public $usertype;
    public $isloggedin = false;
    private $alerts;
    public $settings = array();             // Array for settings
    public $alert_notifications = array();
        
        function __construct()
        {
            if(session_status() == PHP_SESSION_NONE){
                session_start();
            }
            parent::__construct();
            $this->configLoad(dirname(__DIR__).'/configs/global.conf','ipms');
            $_path = $this->getConfigVars('path');
            $this->requireLogin();
            $this->force_compile = false;
            $this->debugging = false;
            $this->caching = false;
            $this->cache_lifetime = 120;    
            $this->setCompileDir($_path.'/templates_c');     
            
            // Load settings
            $this->getSettings();
            
            /* are there any errors the user should know about, i.e failed to delete a switch */
            $this->alerts = $this->log_retrieve_alerts();
            foreach ($this->alerts as $key => $value) {
                if ($this->alerts[$key]['type'] == 'Error') $alert_type = "alert-danger";
                else $alert_type = "alert-success";
                array_push($this->alert_notifications,array("message" => $this->alerts[$key]['logentry'], "type" => $alert_type));
            }   
        }
        /* Retrieve some settings from the database
         * this includes some defaults that users can customise
         */
        private function getSettings()
        {
            $pdo = $this->dbconnect();
            $q = $pdo->prepare("SELECT * FROM ipms_settings");
            $q->execute();
            $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
            $pdo=null;
            unset($q);
            
            foreach($resultarray as $k => $setting)
            {
                $this->settings +=[$setting['key'] => $setting['value']];
            }

            
        }

        private function requireLogin()
        {

            $pdo = $this->dbconnect();
		
	    if (!isset($_SESSION['username'])){
                // The user has not yet logged in, we need to process the passed login details.
                $q = $pdo->prepare("SELECT userid,username,usertype FROM ipms_users where username = :username AND password = MD5(:password)");
                $q->bindParam(':username', $_REQUEST['username']);
                $q->bindParam(':password', $_REQUEST['password']);
                $q->execute();
                $q->bindColumn(1,$this->userid);
                $q->bindColumn(2,$this->username);
                $q->bindColumn(3,$this->usertype);
                $q->fetch();
                $pdo=null;
                unset($q);
            	if (!$this->userid) {
                	unset($this->username);
                	unset($q);
                	return;
            	}
                $this->isloggedin = true;
	    }
            if ($this->isloggedin == false){
                // There's an active session already for the user but a new init call.
                $q = $pdo->prepare("SELECT userid,username,usertype FROM ipms_users where username = :username");
                $q->bindParam(':username', $_SESSION['username']);
                $q->execute();
                $q->bindColumn(1,$this->userid);
                $q->bindColumn(2,$this->username);
                $q->bindColumn(3,$this->usertype);
                $q->fetch();
                $pdo=null;
                unset($q);
            	if (!$this->userid) {
                	unset($this->username);
                	unset($q);
                	return;
            	}             
                $this->isloggedin = true;
            }
            
            $this->userip = $_SERVER["REMOTE_ADDR"];
            $this->assign('loggedin', true);
            $this->assign('username', $this->username);
            $this->assign('userid', $this->userid);
            $this->assign('usertype', $this->usertype);
            $this->assign('userip', $this->userip);
            if (!isset($_SESSION['username'])){
		//User initially logs in here
                if ($this->username) {
                    $this->log_insert("User $this->username Logged in","login");
                }                
                $_SESSION['username']=$this->username;
            }else $this->username = $_SESSION['username'];
        }
    
	function dbconnect($database = 'ipms')
	{            
            if (!isset($this->db_link)){
                $this->configLoad(dirname(__DIR__).'/configs/global.conf',$database);

		$dbhost = $this->getConfigVars('db_host');
		$dbuser = $this->getConfigVars('db_user');
		$dbpass = $this->getConfigVars('db_pass');
		$dbname = $this->getConfigVars('db_name');

                try {
                    $this->db_link = new PDO("mysql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);
                    $this->db_link->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                }catch (PDOException $e) {
                    echo $e->getmessage();
                }
             } 
		return $this->db_link;
	}        

	function outputAdminArea($template)
	{
		$this->display($template);
	}
        
        public function secondsToTime($seconds) {
            $dtF = new \DateTime('@0');
            $dtT = new \DateTime("@$seconds");
            return $dtF->diff($dtT)->format('%ad %Hh %I:%S');
        }

        public function bytesToSize($bytes) {
                $sizes = array('Bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps');
                if ($bytes == 0) return 'n/a';
                $i = intval(floor(log($bytes) / log(1024)));
                if ($i == 0) return $bytes . ' ' . $sizes[$i];
                return round(($bytes / pow(1024, $i)),1,PHP_ROUND_HALF_UP). ' ' . $sizes[$i];
        }
        
        /* call a remote API example usage
         * api_call("https://domain.com/api.php",$fields,$fields_string);
         */
	public function api_call($call,$fields,$fields_string){
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $call);
            curl_setopt($ch, CURLOPT_HEADER, 0);
            curl_setopt($ch, CURLOPT_POST, count($fields));
            curl_setopt($ch, CURLOPT_POSTFIELDS, $fields_string);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
            $output = curl_exec($ch);
            curl_close($ch);
            return $output;

        }
	public function log_insert($detail,$type = "info",$alert = 0)
	{
            $pdo = $this->dbconnect();
            
            $q = $pdo->prepare("INSERT INTO ipms_logs (userid,logentry,datetime,userip,alert,type) VALUES (:userid,:detail,now(),:userip,:alert,:type)");
            $q->bindParam(":userid",$this->userid);
            $q->bindParam(":detail",$detail);
            $q->bindParam(":userip",$this->userip);
            $q->bindParam(":alert",$alert);
            $q->bindParam(":type",$type);
            $q->execute();
            unset($q);
            $pdo = null;            
	}        
        
        /* acknowledge last alerts for user to avoid repeatedly showing them */
        public function log_acknowledge_last_alerts()
        {
            $pdo = $this->dbconnect();
            
            $q = $pdo->prepare("UPDATE ipms_logs SET acknowledged = 1 WHERE userid = :userid");
            $q->bindParam(":userid",$this->userid);
            $q->execute();
            unset($q);
            $pdo = null;     

            return;
        }        

        public function log_retrieve_alerts()
        {
            $pdo = $this->dbconnect();
            $q = $pdo->prepare("SELECT logentry,datetime,type
                    FROM ipms_logs WHERE userid = :userid AND alert = 1 AND acknowledged = 0");
            $q->bindParam(':userid',$this->userid);
            $q->execute();
            $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
            $pdo = null;

            return $resultarray;	
        }        
        // Any jobs that need to be performed externally
        // i.e deleting a peer at a file and router level
        // will be processed by a cron job
        public function addTask($job,$data)
	{
            $pdo = $this->dbconnect();
            
            $q = $pdo->prepare("INSERT INTO ipms_operations (job,data,date) VALUES (:job,:data,now())");
            $q->bindParam(":job",$job);
            $q->bindParam(":data",$data);
            $q->execute();
            unset($q);
            $pdo = null;            
	}        
        
        public function getLogs()
        {
            $pdo = $this->dbconnect();
            $q = $pdo->prepare("SELECT logid,logentry,datetime,type,userip,username
                    FROM ipms_logs LEFT JOIN ipms_users ON ipms_users.userid = ipms_logs.userid WHERE type <> 'login' ");
            $q->execute();
            $resultarray = $q->fetchAll(PDO::FETCH_ASSOC);
            $pdo = null;

            return $resultarray;
        }

	function logout()
	{
                $this->log_insert("User ".$this->username." Logged out","Info");
		session_unset();
		session_destroy();
		$this->assign('loggedin',false);
		$this->display('login.tpl');
		exit(0);
	}
    public function get_page(array $input, $pageNum, $perPage) {
        $start = ($pageNum - 1) * $perPage;
        $end = $start + $perPage;
        $count = count($input);

        // Conditionally return results
        if ($start < 0 || $count <= $start) {
            // Page is out of range
            return array();
        } else if ($count <= $end) {
            // Partially-filled page
            return array_slice($input, $start);
        } else {
            // Full page 
            return array_slice($input, $start, $end - $start);
        }
    }


}

function getVar($value,$default=''){
    if(isset($_GET[$value]) && $_GET[$value]!=''){
        return $_GET[$value];
    }
    else
    {
        return $default;
    }
}

function postVar($value,$default=''){
    if(isset($_POST[$value]) && $_POST[$value]!=''){
        return $_POST[$value];
    }
    else
    {
        return $default;
    }
}
?>