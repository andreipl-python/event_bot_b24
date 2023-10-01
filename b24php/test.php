<?php
require_once('function.php');
$connector_id = getConnectorID();
$line_id = getLine();
$chatID = $_POST['chat_id'];

//отправка сообщения в ОЛ
$arMessage = [
		'user' => [
			'id' => $chatID,
			'name' => $_POST['full_name'],
		],
		'message' => [
			'id' => 1,
			'date' => time(),
			'text' => htmlspecialchars($_POST['message']),
		],
		'chat' => [
			'id' => $chatID,
		],
	];
{
    $result = CRest::call(
        'imconnector.send.messages',
        [
            'CONNECTOR' => $connector_id,
            'LINE' => $line_id,
            'MESSAGES' => [$arMessage],
        ]
    );
}

header('Content-Type: application/json');
echo json_encode($result);