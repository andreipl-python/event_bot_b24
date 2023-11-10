import json
from typing import List

from asyncpg import Record
from flask import Flask, request
from aiogram import Bot
from sql import Database
from b24_models import B24
from messages.user_messages import UserMessages

app = Flask(__name__)


@app.route("/index")
async def index():
    return "Working..."


@app.route("/iml", methods=['GET', 'POST'])
async def iml():
    im_link = request.args.get('iml')
    user_id = int(im_link.split('|')[-2])
    lead_id = int(request.args.get('lead_id').replace('L_', ''))
    try:
        async with Database() as db:
            await db.set_iml(user_id, im_link)
            await db.set_lead_id(user_id, lead_id)
        return "IML set successfully."
    except:
        return "IML set error"


@app.route("/msg", methods=['GET', 'POST'])
async def send_msg():
    bot = Bot(token='')
    data_bytes = request.data
    data_string = data_bytes.decode('utf-8')
    data_dict: dict = json.loads(data_string)
    print("Данные запроса:", data_dict)

    if data_dict['data']['event'] in ['ONIMBOTMESSAGEADD', 'ONIMBOTJOINCHAT']:
        return 'Ignored bot_message'

    # обработка команд
    if data_dict['data']['event'] == 'ONIMCOMMANDADD':
        # 14 TG-buttons stat
        if data_dict['data']['data']['COMMAND'].get('14'):
            user_id = data_dict['data']['data']['PARAMS']['CHAT_ENTITY_ID'].split('|')[-2]
            async with Database() as db:
                buttons_stat_data: List[Record] = await db.get_button_stat(int(user_id))
                await B24().send_message_to_ol(user_id, 'Система',
                                                      UserMessages().buttons_stat(buttons_stat_data))
                return 'Success command'

    # обработка сообщений из Б24
    msg_text = data_dict['data']['data']['MESSAGES'][0]['message']['text']
    chat_id = data_dict['data']['data']['MESSAGES'][0]['chat']['id']
    if not msg_text.startswith('/'):
        try:
            await bot.send_message(chat_id, msg_text)
        except Exception as e:
            await B24().send_message_to_ol(chat_id, 'Система',
                                           '[B]Сообщение не доставлено, вероятно пользователь заблокировал бота.[/B]')
        await bot.session.close()
    return "End of msg function"


@app.route("/metamsg", methods=['GET', 'POST'])
async def messaging_meta_webhook():
    print(request.args)
    print(request.data)
    return 'OK', 200


@app.route("/insta", methods=['GET', 'POST'])
async def messaging_insta_webhook():
    print(request.args)
    print(request.data)
    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9999)


