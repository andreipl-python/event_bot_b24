from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from sql import Database


class SelectEventCallbackFactory(CallbackData, prefix='selectevent'):
    product_id: Optional[int] = None


class BuyEventCallbackFactory(CallbackData, prefix='buyevent'):
    product_id: Optional[int] = None


class UserKb(InlineKeyboardBuilder):

    async def get_products_kb(self, user_id: int) -> InlineKeyboardMarkup:
        admin_list = config.admin_ids.get_secret_value().split(',')
        async with Database() as db:
            products = await db.get_products()
        sorted_products = sorted(products, key=lambda x: x['active_to'])
        for product in sorted_products:
            self.button(
                text=product.get('name'),
                callback_data=SelectEventCallbackFactory(product_id=product.get('id')))
        if str(user_id) in admin_list:
            self.button(text='⚙️ Панель администратора', callback_data='admin_panel')
        self.adjust(1)
        return self.as_markup()

    async def event_kb(self, product_id: int):
        self.button(
            text='⚡️ Купить',
            callback_data=BuyEventCallbackFactory(product_id=product_id))
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def buy_event_kb(self):
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def return_to_start_kb(self):
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()
