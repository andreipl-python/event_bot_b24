from typing import List

from aiogram.types import SuccessfulPayment
from asyncpg import Record


class UserMessages:

    def __init__(self):
        self.not_active_event = 'Мероприятие неактивно'

    @staticmethod
    def event_description(description: str) -> str:
        formatted_description = (description.replace('<br>', '').replace('&nbsp;', '')
                                 .replace('Дата', '🗓 Дата').replace('Время', '🕰 Время')
                                 .replace('Стоимость', '💰 Стоимость'))
        return formatted_description

    @staticmethod
    def buttons_stat(buttons_data: List[Record]) -> str:
        if buttons_data:
            msg_usual = '[B]Статистика нажатий пользователя по кнопкам мероприятий[/B]\n\n'
            msg_buying = '[B]Статистика нажатий пользователя по кнопкам покупки[/B]\n\n'
            for record in buttons_data:
                if record.get('button_name').find('Купить') == -1:
                    msg_usual += f'[I]{record.get("button_name")}[/I] ({record.get("count")})\n'
                else:
                    msg_buying += f'[I]{record.get("button_name")}[/I] ({record.get("count")})\n'
            return f'{msg_usual}\n{msg_buying}' if msg_buying.split('\n\n')[1] != '' else msg_usual
        return '[B]Пользователь не нажимал на кнопки мероприятий в чат-боте[/B]'

    @staticmethod
    def successful_payment(payment_data: SuccessfulPayment, product_name: str) -> str:
        currency = payment_data.currency
        total_amount = payment_data.total_amount
        deal_id = int(payment_data.invoice_payload.split(':')[1])
        provider_payment_charge_id = payment_data.provider_payment_charge_id
        return ('Спасибо за оплату!\n\n'
                '<b>Подробные данные вашего заказа:</b>\n'
                f'<b>Номер заказа</b>: <code>{deal_id}</code>\n'
                f'<b>Название мероприятия:</b>: <code>{product_name}</code>\n'
                f'<b>Стоимость</b>: <code>{total_amount/100} {currency}</code>\n'
                f'<b>Уникальный ID платежа:</b>: <code>{provider_payment_charge_id}</code>\n')
