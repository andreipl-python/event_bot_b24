<?php
define('C_REST_CLIENT_ID','local.6511cdfe854bc7.10434790');//Application ID
define('C_REST_CLIENT_SECRET','c0w7e97pl2vl2YI23zcdSphkeX3u6i83145Hnq2wd9vg4IfveK');//Application key
//or
//define('C_REST_WEB_HOOK_URL','https://rudneva.bitrix24.pl/rest/12/33l45akc38679pu6/');//url on creat Webhook

//define('C_REST_CURRENT_ENCODING','windows-1251');
define('C_REST_IGNORE_SSL',true);//turn off validate ssl by curl
define('C_REST_LOG_TYPE_DUMP',true); //logs save var_export for viewing convenience
//define('C_REST_BLOCK_LOG',true);//turn off default logs
define('C_REST_LOGS_DIR', __DIR__ .'/logs/'); //directory path to save the log
