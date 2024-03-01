import json
from operator import itemgetter
from typing import Optional, List, Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asyncpg import Record

from config_reader import config
from sql import Database


class SelectEventCallbackFactory(CallbackData, prefix='selectevent'):
    product_id: int
    back_to_personal: Optional[bool] = None
    from_mm: Optional[bool] = None


class BuyEventCallbackFactory(CallbackData, prefix='buyevent'):
    product_id: Optional[int] = None


class BuyEventPayMethodFactory(CallbackData, prefix='paybymeth'):
    method: Optional[str] = None
    product_id: Optional[int] = None
    deal_id: Optional[int] = None


class ChangeCityFactory(CallbackData, prefix='changecity'):
    city_id: int


class AnketaStep1Factory(CallbackData, prefix='anketastep1'):
    active_id: str


class AnketaStep2Factory(CallbackData, prefix='anketastep2'):
    topic_id: str


class AnketaStep3Factory(CallbackData, prefix='anketastep3'):
    sale_type_id: str


class UserKb(InlineKeyboardBuilder):

    async def main_menu(self, user_id: int) -> InlineKeyboardMarkup:
        admin_list = config.admin_ids.get_secret_value().split(',')
        async with Database() as db:
            is_filled_out_the_form = await db.is_filled_out_the_form(user_id)
            personal_events_counter = await db.personal_events_counter(user_id) if is_filled_out_the_form else '❗️'
        self.button(
            text='💡 Консультация',
            callback_data=SelectEventCallbackFactory(product_id=326, from_mm=True)
        )
        self.button(
            text='🗓 Расписание',
            callback_data='calendar:mm'
        )
        self.button(
            text='🎉 О нас',
            callback_data='about_us'
        )
        self.button(
            text=f'👑 Персональные рекомендации [{personal_events_counter}]',
            callback_data='personal:mm'
        )
        self.button(
            text='👤 Личный кабинет',
            callback_data='cabinet'
        )

        self.button(
            text='❓ Задать вопрос',
            callback_data='question'
        )
        self.button(
            text='🪄 Как пользоваться ботом',
            callback_data='how_to'
        )
        if str(user_id) in admin_list:
            self.button(text='⚙️ Панель администратора', callback_data='admin_panel')
        self.adjust(1, 2, 1, 2, 1, 1)
        return self.as_markup()

    async def cabinet(self) -> InlineKeyboardMarkup:
        self.button(
            text='📚 История заказов',
            callback_data='history'
        )
        self.button(
            text='⚙️ Настройки',
            callback_data='settings'
        )
        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def settings(self) -> InlineKeyboardMarkup:
        self.button(
            text='🌆 Изменить город',
            callback_data='change_city'
        )
        self.button(
            text='🧬 Изменить анкету предпочтений',
            callback_data='anketa'
        )
        self.button(
            text='🔙 Личный кабинет',
            callback_data='cabinet'
        )
        self.button(
            text='⭐️ Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def personal_anketa(self) -> InlineKeyboardMarkup:
        self.button(
            text='🔖 Начать заполнение анкеты',
            callback_data='anketa'
        )
        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def change_city(self, user_id: int) -> InlineKeyboardMarkup:
        products_cities = json.loads(config.products_cities.get_secret_value())
        products_cities = {int(key): value for key, value in products_cities.items()}
        buttons_texts = {'Gdańsk': '🐳 Gdańsk', 'Poznań': '🐐 Poznań', 'Wrocław': '🌉 Wrocław'}
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')
        current_city_id = next((key for key, val in products_cities.items() if val == user_city), None)
        for city_id, city in products_cities.items():
            if city_id != current_city_id:
                self.button(text=buttons_texts.get(city), callback_data=ChangeCityFactory(city_id=city_id))

        self.button(
            text='🔙 Настройки',
            callback_data='settings'
        )
        self.button(
            text='⭐️ Главное меню',
            callback_data='start'
        )
        self.adjust(2, 1, 1)
        return self.as_markup()

    async def get_products_kb(self, user_id: int) -> InlineKeyboardMarkup:
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')

            products = await db.get_products(user_city)
            sorted_products = sorted(products, key=itemgetter('active_to'))
            for product in sorted_products:
                if product.get('id') != 326:
                    is_payed: List[Record] = await db.get_user_payed_deal_by_product_id(user_id, product.get('id'))
                    button_text = product.get('name') if not is_payed else f'{product.get("name")} 🔋'
                    self.button(
                        text=button_text,
                        callback_data=SelectEventCallbackFactory(product_id=product.get('id')))

        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def event_kb(self, product_id: int, back_to: bool = None) -> InlineKeyboardMarkup:
        self.button(
            text='⚡️ Купить' if product_id != 326 else '⚡️ Купить консультацию',
            callback_data=BuyEventCallbackFactory(product_id=product_id))
        if product_id != 326:
            self.button(
                text='🔙 Расписание' if not back_to else '🔙 Персональные рекомендации',
                callback_data='calendar' if not back_to else 'personal'
            )
        self.button(
            text='⭐️ Главное меню',
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
                callback_data='calendar'
            )
        self.adjust(1)
        return self.as_markup()

    async def return_to_calendar_kb(self) -> InlineKeyboardMarkup:
        self.button(
            text='🔙 Календарь событий',
            callback_data='calendar'
        )
        self.adjust(1)
        return self.as_markup()

    async def return_to_main_menu_kb(self) -> InlineKeyboardMarkup:
        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def about_us(self, user_id: int) -> InlineKeyboardMarkup:
        async with Database() as db:
            is_filled_out_the_form = await db.is_filled_out_the_form(user_id)
            personal_events_counter = await db.personal_events_counter(user_id) if is_filled_out_the_form else '❗️'
        self.button(
            text='🗓 Расписание',
            callback_data='calendar'
        )
        self.button(
            text=f'👑 Персональные рекомендации [{personal_events_counter}]',
            callback_data='personal'
        )
        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def payment_methods_kb(self, product_id: int, deal_id: int) -> InlineKeyboardMarkup:
        # self.button(
        #     text='💳 Visa/Mastercard',
        #     callback_data=BuyEventPayMethodFactory(method='card', product_id=product_id, deal_id=deal_id))
        self.button(
            text='📲 Оплата BLIK',
            callback_data=BuyEventPayMethodFactory(method='blik', product_id=product_id, deal_id=deal_id))
        self.button(
            text='🏦 Перевод по номеру счёта',
            callback_data=BuyEventPayMethodFactory(method='bank', product_id=product_id, deal_id=deal_id))
        self.button(
            text='🔙 Календарь событий',
            callback_data='calendar'
        )
        self.adjust(1)
        return self.as_markup()

    async def reminder(self):
        self.button(
            text='🗓 Календарь событий',
            callback_data='calendar'
        )
        self.button(
            text='📞 Заказать звонок',
            callback_data='call_ask'
        )
        self.adjust(1)
        return self.as_markup()

    async def anketa_step1(self, buttons_data: dict) -> InlineKeyboardMarkup:
        products_custom_property_lvl2 = json.loads(config.products_custom_property_lvl2.get_secret_value())
        target_list = products_custom_property_lvl2.get('property102')
        for active_id, status in buttons_data.items():
            text = 'None'
            for property_dict in target_list:
                if property_dict.get('value') == active_id:
                    text = property_dict.get('valueEnum')
                    break
            self.button(
                text=f'✅ {text}' if status else text,
                callback_data=AnketaStep1Factory(active_id=active_id)
            )
        self.button(
            text='📨 Подтвердить',
            callback_data='approve_anketa_step1'
        )
        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1, 1, 2, 1, 1)
        return self.as_markup()

    async def anketa_step2(self, buttons_data: dict) -> InlineKeyboardMarkup:
        products_custom_property_lvl2 = json.loads(config.products_custom_property_lvl2.get_secret_value())
        target_list = products_custom_property_lvl2.get('property104')
        for topic_id, status in buttons_data.items():
            text = 'None'
            for property_dict in target_list:
                if property_dict.get('value') == topic_id:
                    text = property_dict.get('valueEnum')
                    break
            self.button(
                text=f'✅ {text}' if status else text,
                callback_data=AnketaStep2Factory(topic_id=topic_id)
            )
        self.button(
            text='📨 Подтвердить',
            callback_data='approve_anketa_step2'
        )
        self.button(
            text='🔙 Предыдущий вопрос',
            callback_data='anketa'
        )
        self.adjust(2, 1, 1, 1, 2, 1, 1, 2, 1, 1)
        return self.as_markup()

    async def anketa_step3(self, buttons_data: dict) -> InlineKeyboardMarkup:
        products_custom_property_lvl2 = json.loads(config.products_custom_property_lvl2.get_secret_value())
        target_list = products_custom_property_lvl2.get('property106')
        for sale_type_id, status in buttons_data.items():
            text = 'None'
            for property_dict in target_list:
                if property_dict.get('value') == sale_type_id:
                    text = property_dict.get('valueEnum')
                    break
            self.button(
                text=f'✅ {text}' if status else text,
                callback_data=AnketaStep3Factory(sale_type_id=sale_type_id)
            )
        self.button(
            text='📨 Подтвердить',
            callback_data='approve_anketa_step3'
        )
        self.button(
            text='🔙 Предыдущий вопрос',
            callback_data='approve_anketa_step1'
        )
        self.adjust(2, 1, 1, 1)
        return self.as_markup()

    async def end_of_anketa(self, user_id: int) -> InlineKeyboardMarkup:
        async with Database() as db:
            is_filled_out_the_form = await db.is_filled_out_the_form(user_id)
            personal_events_counter = await db.personal_events_counter(user_id) if is_filled_out_the_form else '❗️'
        self.button(
            text=f'👑 Мероприятия для меня [{personal_events_counter}]',
            callback_data='personal'
        )
        self.button(
            text='⭐️ Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    async def get_personal_products_kb(self, user_id: int) -> InlineKeyboardMarkup:
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')
            products: List[Record] = await db.get_products(user_city)

            personal_products = []
            user_activities = set(user_data[0].get('activities').split(','))
            user_topics = set(user_data[0].get('topics').split(','))
            user_sales_types = set(user_data[0].get('sales_types').split(','))

            for product in products:
                activities = set(product.get('activities').split(','))
                topics = set(product.get('topics').split(','))
                sales_types = set(product.get('sales_types').split(','))

                if user_activities.intersection(activities) and user_topics.intersection(topics) \
                        and user_sales_types.intersection(sales_types):
                    personal_products.append(product)

            sorted_products = sorted(personal_products, key=itemgetter('active_to'))
            for product in sorted_products:
                is_payed: List[Record] = await db.get_user_payed_deal_by_product_id(user_id, product.get('id'))
                button_text = product.get('name') if not is_payed else f'{product.get("name")} 🔋'
                self.button(
                    text=button_text,
                    callback_data=SelectEventCallbackFactory(product_id=product.get('id'), back_to_personal=True)
                )

        self.button(
            text='🔙 Главное меню',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()


class UserReplyKb(ReplyKeyboardBuilder):
    def ask_contact_kb(self) -> ReplyKeyboardMarkup:
        self.button(text='📲 Отправить контакт', request_contact=True)
        self.adjust(1)
        return self.as_markup(resize_keyboard=True)
