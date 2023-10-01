<?php
include_once('crest.php');
function getConnectorID()
{
	return 'example_connector_1';
}
function getChat($chatID)
{
	$result = [];
	if (file_exists(__DIR__ . '/chats/' . $chatID . '.txt'))
	{
		$result = json_decode(file_get_contents(__DIR__ . '/chats/' . $chatID . '.txt'), 1);
	}
	return $result;
}

function saveMessage($chatID, $arMessage)
{
	$arMessages = getChat($chatID);
	$count = count($arMessages);
	$arMessages['message' . $count] = $arMessage;
	if (file_put_contents(__DIR__ . '/chats/' . $chatID . '.txt', json_encode($arMessages)))
	{
		$return = $count;
	}
	else
	{
		$return = false;
	}
	return $return;
}

function getLine()
{
	return file_get_contents(__DIR__ . '/line_id.txt');
}
function setLine($line_id)
{
	return file_put_contents(__DIR__ . '/line_id.txt', intVal($line_id));
}
function convertBB($var)
{
	$search = array(
		'/\[b\](.*?)\[\/b\]/is',
		'/\[br\]/is',
		'/\[i\](.*?)\[\/i\]/is',
		'/\[u\](.*?)\[\/u\]/is',
		'/\[img\](.*?)\[\/img\]/is',
		'/\[url\](.*?)\[\/url\]/is',
		'/\[url\=(.*?)\](.*?)\[\/url\]/is'
	);
	$replace = array(
		'<strong>$1</strong>',
		'<br>',
		'<em>$1</em>',
		'<u>$1</u>',
		'<img src="$1" />',
		'<a href="$1">$1</a>',
		'<a href="$1">$2</a>'
	);
	$var = preg_replace($search, $replace, $var);
	return $var;
}

