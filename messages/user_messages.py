import re
from typing import List

from aiogram.types import SuccessfulPayment
from asyncpg import Record


class UserMessages:

    def __init__(self):
        self.not_active_event = 'Мероприятие неактивно'
        self.reminder = ('👋Возможно вас что-то отвлекло…\n\n'
                         'Проверьте мероприятия, выберите нужное, нажмите кнопку "⚡️ Купить" и забронируйте место!\n\n'
                         'А если хотите получить консультацию нашего менеджера нажмите кнопку "📞 Заказать звонок" 👇')
        self.ask_phone = ("❇️ Чтобы мы могли с вами связаться, нажмите '📲 Отправить контакт'\n\n"
                          "❗ Кнопка под строкой сообщений\n"
                          "Если не видно кнопки, нажмите на квадратик с четырьмя точками, справа от строки сообщений.")
        self.successful_contact = '☀️ Спасибо! В ближайшее время мы вам позвоним!'

    @staticmethod
    def event_description(description: str) -> str:
        formatted_description = (
            description.replace('<br>', '').replace('&nbsp;', '')
            .replace('Дата', '🗓 Дата').replace('Время', '🕰 Время')
            .replace('Стоимость', '💰 Стоимость').replace('Локация', '📍 Локация')
            .replace('Длительность', '🕰 Длительность')
        )
        pattern = r"(Локация:)(.*?)(\s)(https://.+)"
        formatted_text = re.sub(pattern, r'\1<a href="\4">\2</a>', formatted_description)
        return formatted_text

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
    def other_payment(deal_id: int, event_name: str, product_price: float, method: str) -> str:
        order_part = ('Ваш заказ успешно сформирован!\n\n'
                      '<b>Подробные данные вашего заказа:</b>\n'
                      f'<b>Номер заказа</b>: <code>{deal_id}</code>\n'
                      f'<b>Название мероприятия:</b>: <code>{event_name}</code>\n'
                      f'<b>Стоимость</b>: <code>{product_price} PLN</code>\n\n')
        method_part = (f'❓ <b><u>Как оплатить</u></b>\n'
                       f'Оплатить с помощью BLIK вы можете по реквизитам (нажмите, чтобы скопировать):\n\n'
                       f'☎️ Номер телефона: <code>690265990</code>\n'
                       f'👤 Получатель: <code>Rudneva Volha</code>\n'
                       f'⚙️ Назначение платежа: <code>{deal_id}</code>\n\n') \
            if method == 'blik' else \
            (f'❓ <b><u>Как оплатить</u></b>\n'
             f'Оплатить с помощью перевода на банковский счёт вы можете по реквизитам (нажмите, чтобы скопировать):\n\n'
             f'#️⃣ Номер счета: <code>93 1090 2486 0000 0001 4922 9086</code>\n'
             f'👤 Получатель: <code>Rudneva Volha</code>\n'
             f'⚙️ Назначение платежа: <code>{deal_id}</code>\n\n')
        information_part = (f'‼️ Внимание ‼️ Назначение платежа обязательно должно быть заполнено! '
                            f'Иначе мы <u>не сможем обработать Ваш платеж!</u>\n\n'
                            f'Максимальный срок обработки платежа 24 часа, после успешной обработки - '
                            f'Вам придет подтверждение от бота.\nДо встречи на мероприятии!')
        return f'{order_part}{method_part}{information_part}'

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
                f'<b>Стоимость</b>: <code>{total_amount / 100} {currency}</code>\n'
                f'<b>Уникальный ID платежа:</b>: <code>{provider_payment_charge_id}</code>\n')

    @staticmethod
    def custom_send() -> str:
        return ("19.10 четверг в 18.00\n\n"
                "<b>Бизнес - ужин</b>\n\n"
                "Классная компания, окружение предпринимателей из Вроцлава, новые контакты и решение бизнес - запросов\n\n"
                "Темы для обсуждения:\n\n"
                "- развитие оффлайн бизнеса;\n"
                "- бухгалтерия и налоги;\n"
                "- маркетинг и продвижение;\n"
                "- планирование и делегирование;\n"
                "- подбор специалистов и подрядчиков;\n"
                "- продажи и привлечение клиентов;\n"
                "- выход на зарубежный рынок.\n\n"
                "🕰 Длительность: 2-2,5 часа\n"
                "💰 Стоимость: 50 зл\n"
                '📍 Локация: <a href="https://maps.app.goo.gl/q9pjcudCcBnvcHts5">Ristorante Pizzeria O Sole Mio, 16/17, Rynek, Wrocław</a>')
