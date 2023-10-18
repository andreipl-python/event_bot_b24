<?php
require_once('function.php');
$connector_id = getConnectorID();
$line_id = getLine();
$chatID = $_POST['chat_id'];

// if (is_string($_POST['msg'])) {
//     send_string_message_to_ol($chatID, $connector_id, $line_id);
// } elseif (array_key_exists('ATTACH', $_POST['msg'])) {
//     send_array_message_to_ol($chatID);
// }
//
// function send_string_message_to_ol($chatID, $connector_id, $line_id)
    {
    $arMessage = [
            'user' => [
                'id' => $chatID,
                'name' => $_POST['full_name'],
            ],
            'message' => [
                'id' => 1,
                'date' => time(),
                'text' => htmlspecialchars($_POST['msg']),
            ],
            'chat' => [
                'id' => $chatID,
            ],
        ];

    $result = CRest::call(
            'imconnector.send.messages',
            [
                'CONNECTOR' => $connector_id,
                'LINE' => $line_id,
                'MESSAGES' => [$arMessage],
            ]
        );

    header('Content-Type: application/json');
    echo json_encode($result);
    }


//     {
//     $result = CRest::call(
//             'imbot.message.add',
//             [
//                 'DIALOG_ID' => $chatID,
//                 'BOT_ID' => 356,
//                 'MESSAGE' => 'Пользователю отправлено сообщение',
//                 'ATTACH' => Array(
//                     'ID' => 1,
//                     'COLOR' => '#29619b',
//                     'BLOCKS'=> Array(
//                         'MESSAGE' => 'bla bla bla'
//                     )
//                 )
//             ]
//         );
//
//     header('Content-Type: application/json');
//     echo json_encode($result);
//     }


