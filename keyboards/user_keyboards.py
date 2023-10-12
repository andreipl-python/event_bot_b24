from operator import itemgetter
from typing import Optional, List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asyncpg import Record

from config_reader import config
from sql import Database


class SelectEventCallbackFactory(CallbackData, prefix='selectevent'):
    product_id: Optional[int] = None


class BuyEventCallbackFactory(CallbackData, prefix='buyevent'):
    product_id: Optional[int] = None


class BuyEventPayMethodFactory(CallbackData, prefix='paybymeth'):
    method: Optional[str] = None
    product_id: Optional[int] = None
    deal_id: Optional[int] = None


class UserKb(InlineKeyboardBuilder):

    async def get_products_kb(self, user_id: int) -> InlineKeyboardMarkup:
        admin_list = config.admin_ids.get_secret_value().split(',')
        async with Database() as db:
            products = await db.get_products()
            sorted_products = sorted(products, key=itemgetter('active_to'))
            for product in sorted_products:
                is_payed: List[Record] = await db.get_user_payed_deal_by_product_id(user_id, product.get('id'))
                button_text = product.get('name') if not is_payed else f'{product.get("name")} 🔋'
                self.button(
                    text=button_text,
                    callback_data=SelectEventCallbackFactory(product_id=product.get('id')))
        if str(user_id) in admin_list:
            self.button(text='⚙️ Панель администратора', callback_data='admin_panel')
        self.adjust(1)
        return self.as_markup()

    async def event_kb(self, product_id: int) -> InlineKeyboardMarkup:
        self.button(
            text='⚡️ Купить',
            callback_data=BuyEventCallbackFactory(product_id=product_id))
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def return_to_payment_methods(self, product_id: int, with_calendar: bool) -> InlineKeyboardMarkup:
        self.button(
            text='🔙 Методы оплаты',
            callback_data=BuyEventCallbackFactory(product_id=product_id))
        if with_calendar:
            self.button(
                text='🗓 Календарь событий',
                callback_data='start'
            )
        self.adjust(1)
        return self.as_markup()

    async def return_to_start_kb(self) -> InlineKeyboardMarkup:
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def payment_methods_kb(self, product_id: int, deal_id: int) -> InlineKeyboardMarkup:
        self.button(
            text='💳 Visa/Mastercard',
            callback_data=BuyEventPayMethodFactory(method='card', product_id=product_id, deal_id=deal_id))
        self.button(
            text='📲 Оплата BLIK',
            callback_data=BuyEventPayMethodFactory(method='blik', product_id=product_id, deal_id=deal_id))
        self.button(
            text='🏦 Перевод по номеру счёта',
            callback_data=BuyEventPayMethodFactory(method='bank', product_id=product_id, deal_id=deal_id))
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def reminder(self):
        self.button(
            text='🗓 Календарь событий',
            callback_data='start'
        )
        self.button(
            text='📞 Заказать звонок',
            callback_data='call_ask'
        )
        self.adjust(1)
        return self.as_markup()


class UserReplyKb(ReplyKeyboardBuilder):

    def ask_contact_kb(self) -> ReplyKeyboardMarkup:
        self.button(text='📲 Отправить контакт', request_contact=True)
        self.adjust(1)
        return self.as_markup(resize_keyboard=True)
