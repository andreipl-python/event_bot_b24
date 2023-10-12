import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from aiogram import Bot
from asyncpg import Record

from b24_models import B24
from messages.user_messages import UserMessages
from keyboards.user_keyboards import UserKb
from sql import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)


async def update_products():
    while True:
        async with Database() as db:
            product_list = await B24().get_product_list()
            await db.update_table_products(product_list)
        logger = logging.getLogger('update_products')
        logger.info('Update table products successfully')
        await asyncio.sleep(900)


async def deactivate_products():
    while True:
        logger = logging.getLogger('deactivate_products')
        product_list = await B24().get_product_list()
        for product in product_list:
            time_now = datetime.now()+timedelta(hours=2)
            active_to = datetime.strptime(product.get('dateActiveTo').split('+')[0], '%Y-%m-%dT%H:%M:%S')
            if time_now > active_to:
                await B24().deactivate_product(product.get('id'))
                logger.info(f'Deactivate product ID {product.get("id")}, {product.get("name")}')
                deal_list = await B24().get_deal_list_by_stage('FINAL_INVOICE')
                for deal_data in deal_list['result']:
                    deal_productrow = await B24().get_product_by_deal_id(deal_data['ID'])
                    try: deal_product_id = deal_productrow['result'][0]['PRODUCT_ID']
                    except Exception: continue
                    if deal_product_id == product.get('id'):
                        await B24().update_deal_stage(int(deal_data['ID']), 'LOSE')
                        logger.info(f'Lose deal ID {deal_data["ID"]}')
                        await asyncio.sleep(2)
        logger.info('Deactivate products successfully')
        await asyncio.sleep(1800)


async def reminder(bot: Bot):
    logger = logging.getLogger('reminder')
    while True:
        async with Database() as db:
            user_list: List[Record] = await db.get_user_list_for_reminder()
            for user in user_list:
                try:
                    await bot.send_message(chat_id=user.get('user_id'), text=UserMessages().reminder,
                                            reply_markup=await UserKb().reminder())
                    await db.add_reminder_time(user.get('user_id'))
                    await B24().send_message_to_ol(user.get('user_id'), 'Система',
                                                   'Отправлено автоматическое напоминание стимуляция')
                    logger.info(f'Reminder sent to UserId {user.get("user_id")}')
                except Exception:
                    await db.add_reminder_time(user.get('user_id'))
                    await db.set_bot_blocked(user.get('user_id'), True)
                    await B24().send_message_to_ol(user.get('user_id'), 'Система',
                                                   '[B]Напоминание не доставлено, вероятно пользователь заблокировал бота.[/B]')
        logger.info(f'Sent {len(user_list)} reminders.')
        await asyncio.sleep(3600)


