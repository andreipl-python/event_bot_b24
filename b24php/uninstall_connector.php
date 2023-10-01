<?php
require_once('function.php');
{
	$connector_id = getConnectorID();
	$result = CRest::call(
		'imconnector.imconnector_unregister',
		[
			'ID' => $connector_id
			]
	);
    if (!empty($resultEvent['result']))
    {
        echo 'successfully';
    }
}

