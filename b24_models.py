import json
from pprint import pprint
from typing import List

import aiohttp
import asyncio
from config_reader import config


class B24:
    def __init__(self):
        self.url = config.b24_url.get_secret_value()
        self.connector_url = config.connector_url.get_secret_value()

    async def get(self, method: str, connector: bool = False) -> dict:
        url = self.url if not connector else self.connector_url
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{url}{method}') as response:
                response_text = await response.text(encoding='utf-8')
                return json.loads(response_text)

    async def post(self, method: str, data: dict, connector: bool = False) -> dict:
        url = self.url if not connector else self.connector_url
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{url}{method}', json=data) as response:
                response_text = await response.text(encoding='utf-8')
                return json.loads(response_text)

    async def get_product_price(self, product_id: int) -> dict:
        """Получает цену товара"""
        data = {'id': product_id}
        result = await self.post('crm.product.get', data=data)
        return {'PRICE': result['result']['PRICE'], 'CURRENCY_ID': result['result']['CURRENCY_ID']}

    async def get_product_list(self) -> List[dict]:
        """Возвращает список товаров вида {'id', 'iblockId', 'name', 'detailText', 'dateActiveTo', 'dateActiveFrom'}"""
        data = {'select': ['id', 'iblockId', 'name', 'detailText', 'dateActiveTo', 'dateActiveFrom'],
                'filter': {'iblockId': 14, 'active': 'Y'}}
        response_data = await self.post('catalog.product.list', data=data)
        product_list = response_data['result']['products']
        for i in range(len(product_list)):
            product_list[i].update(await self.get_product_price(product_list[i].get('id')))
        return product_list

    async def make_new_contact(self, user_id: int, user_full_name: str, username: str, im_link: str) -> int:
        """Создает новый контакт в Б24, возвращает ID контакта"""
        data = {'fields':
                    {'NAME': user_full_name,
                     'OPENED': 'Y',
                     'ASSIGNED_BY_ID': 1,
                     'TYPE_ID': 'CLIENT',
                     'UF_CRM_1695708161': str(user_id),
                     'HAS_IMOL': 'Y',
                     'WEB': [{'VALUE': f'https://t.me/{username}', 'VALUE_TYPE': 'WORK', 'TYPE_ID': 'WEB'}],
                     'IM': [{'VALUE_TYPE': 'IMOL', 'VALUE': im_link, 'TYPE_ID': 'IM'}]}
                }
        response_data = await self.post('crm.contact.add', data=data)
        return response_data['result']

    async def find_contact_by_tg_id(self, user_id: int) -> str | None:
        """Ищет контакт в Б24 по TelegramID, возвращает ID контакта или None"""
        data = {'filter': {'UF_CRM_1695708161': str(user_id)}}
        response_data = await self.post('crm.contact.list', data=data)
        if response_data['result']:
            return response_data['result'][0]['ID']
        else:
            return None

    async def send_message_to_ol(self, user_id: int, full_name: str, message: str) -> dict:
        """Отправляет мессагу в ОЛ Б24"""
        data = {
            'chat_id': user_id,
            'full_name': full_name,
            'message': message
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.connector_url}test.php', data=data) as response:
                response_data = await response.json()
        return response_data

    async def update_lead_status(self, lead_id: int, new_status: str) -> dict:
        """Перемещает лид на указанную стадию
        Лид == NEW, В работе == IN_PROCESS, Выслано предложение == PROCESSED, Не целевой == JUNK
        Сконвертирован == CONVERTED"""
        data = {
            'id': lead_id,
            'fields': {
                'STATUS_ID': new_status
            }
        }
        return await self.post('crm.lead.update', data=data)

    async def update_lead_contact(self, lead_id: int, contact_id: int) -> dict:
        """Привязывает контакт к лиду"""
        data = {
            'id': lead_id,
            'fields': {
                'CONTACT_ID': contact_id
            }
        }
        return await self.post('crm.lead.update', data=data)

    async def add_new_deal(self, full_name: str, event_name: str, contact_id: int):
        """Создает новую сделку"""
        data = {
            'fields': {
                'TITLE': f'{full_name} - {event_name}',
                'TYPE_ID': 'SALE',
                'STAGE_ID': 'FINAL_INVOICE',
                'CONTACT_ID': contact_id,
                'ASSIGNED_BY_ID': 1,
                'IS_NEW': 'Y',
                'SOURCE_ID': '4|EXAMPLE_CONNECTOR_1'
            }
        }
        return await self.post('crm.deal.add', data=data)

    async def add_product_to_deal(self, deal_id: int, product_id: int, price: float):
        """Добавляет товар к сделке"""
        data = {
            'id': deal_id,
            'rows': [{'PRODUCT_ID': product_id, 'PRICE': price}]
        }
        return await self.post('crm.deal.productrows.set', data=data)

    async def update_deal_stage(self, deal_id: int, new_stage: str) -> dict:
        """Перемещает сделку на указанную стадию
        Успешная сделка == WON, Отказ == LOSE, Выставлен счет == FINAL_INVOICE, В работе == NEW"""
        data = {
            'id': deal_id,
            'fields': {
                'STAGE_ID': new_stage
            }
        }
        return await self.post('crm.deal.update', data=data)

    async def deactivate_product(self, product_id: int):
        """Деактивирует товар"""
        data = {
            'id': product_id,
            'fields': {
                'ACTIVE': 'N'
            }
        }
        return await self.post('crm.product.update', data=data)

    async def get_product_by_deal_id(self, deal_id: int) -> dict:
        """Получает товары сделки по её ID"""
        data = {'id': deal_id}
        return await self.post('crm.deal.productrows.get', data=data)

    async def get_deal_list_by_stage(self, stage: str) -> dict:
        """Получает все айдишники сделок в стадии
        Успешная сделка == WON, Отказ == LOSE, Выставлен счет == FINAL_INVOICE, В работе == NEW"""
        data = {
            'filter': {'STAGE_ID': stage},
            'select': ['ID']
        }
        return await self.post('crm.deal.list', data=data)

async def main():
    pprint(await B24().get_product_by_deal_id(200))

asyncio.run(main())
# # # # id чат бота 356
