<?php
require_once('function.php');
session_start();
$chatID = 'chat' . md5($_SERVER['HTTP_ORIGIN']) . md5(session_id());
$type = $_POST['type'];
$connector_id = getConnectorID();
$line_id = getLine();
/*
	simple example save chat, must lost any data
	recommend using database
*/
if ($type == 'chat_history'):
	$arChat = getChat($chatID);
	if (!empty($arChat)):
		foreach ($arChat as $item):?>
			<div class="col-12 alert alert-warning text-<?=(!empty($item['im'])) ? 'left' : 'right'?>"
				 style=" background-color: <?=(!empty($item['im'])) ? '#fbfbfb' : '#ccf2ff'?>">
				<?=convertBB($item['message']['text'])?>
			</div>
		<?php endforeach;
	endif;

elseif ($type == 'send_message'):
	$arMessage = [
		'user' => [
			'id' => $chatID,
			'name' => htmlspecialchars($_POST['name']),
		],
		'message' => [
			'id' => false,
			'date' => time(),
			'text' => htmlspecialchars($_POST['message']),
		],
		'chat' => [
			'id' => $chatID,
			'url' => htmlspecialchars($_SERVER['HTTP_REFERER']),
		],
	];
	$id = saveMessage($chatID, $arMessage);
	$result['error'] = 'error_save';
	if ($id !== false)
	{
		$arMessage['message']['id'] = $id;
		$result = CRest::call(
			'imconnector.send.messages',
			[
				'CONNECTOR' => $connector_id,
				'LINE' => $line_id,
				'MESSAGES' => [$arMessage],
			]
		);
	}
	echo json_encode(
		[
			'chat' => $chatID,
			'post' => $_POST,
			'result' => $result
		]
	);
endif;