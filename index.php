<?php

require('libs/Smarty.class.php');

require("includes/class.init.php");

$peermanager = new peermanager;

if ($peermanager->isloggedin){
	
	$peermanager->outputAdminArea('index.tpl');
	
} else $peermanager->outputAdminArea('login.tpl');


?>
