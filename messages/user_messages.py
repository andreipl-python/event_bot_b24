import json
import re
from typing import List

from aiogram.types import SuccessfulPayment
from asyncpg import Record

from config_reader import config
from sql import Database


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

    @staticmethod
    async def cabinet(user_id: int) -> str:
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')

        return ('Добро пожаловать в Ваш персональный кабинет!\n\n'
                'Здесь Вы можете легко управлять своими настройками и просматривать историю Ваших заказов.\n\n'
                'В разделе "📚 История заказов" Вы сможете окунуться в воспоминания о ваших предыдущих заказах. '
                'Там Вы найдете все детали о тех мероприятиях, которые Вы посещали, включая даты и другую интересную '
                'информацию.\n\n'
                'В разделе "⚙️ Настройки" Вы можете изменить свой текущий город.\n\n'
                f'В данный момент Ваш город - 🟢 <b>{user_city}</b>.\n\n'
                f'Чтобы видеть мероприятия в другом городе, просто перейдите в настройки и выберите свой любимый город.\n\n'
                f'Для начала работы выберите одну из доступных опций ниже 👇')

    @staticmethod
    async def settings(user_id: int) -> str:
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')

        return ('Ваши текущие настройки:\n\n'
                f'Ваш город - 🟢 <b>{user_city}</b>\n\n'
                f'<b>В этом разделе вы можете:</b>\n\n'
                f'"🌆 Изменить город"\n'
                f'<i>- Регулярно обновляя информацию, мы предоставляем Вам доступ к самым актуальным мастер-классам, '
                f'нетворкингам, бизнес ужинам и другим важным событиям, способным расширить ваше деловое общение и '
                f'помочь вам достичь успеха в Вашем городе. <code>📅 Календарь событий</code> предоставит Вам '
                f'расписание согласно выбранному городу.</i>')

    @staticmethod
    async def change_city(user_id: int) -> str:
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')

        return (f'Город, в котором мы проводим мероприятия для Вас:\n\n'
                f'🟢 <b>{user_city}</b>\n\n'
                'Нажмите на названии города, чтобы изменить 👇')

    @staticmethod
    def about_us() -> str:
        return ('🌟 Добро пожаловать в InsightClub 🌟\n\n'
                '🌍 Мы организуем нетворкинг-события, бизнес-ужины и мастермайнды в городах Польши для вашего роста и '
                'мотивации.\n\n'
                '💼 Наша миссия - соединять предпринимателей, профессионалов и творческих людей, создавая ценные связи '
                'и открывая новые возможности.\n\n'
                '🎉 Наши мероприятия - это источник вдохновения, взаимодействия и сотрудничества!\n\n'
                '🤝 Приходите, находите новых клиентов, знакомьтесь в атмосфере классного окружения.\n\n'
                '💌 Изучите разделы "🗓 Расписание" и "👑 Персональные рекомендации", чтобы узнать больше о наших '
                'событиях и присоединиться к сети профессионалов и предпринимателей!')

    @staticmethod
    async def personal_selection(user_id: int) -> str:
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
            user_city = user_data[0].get('city')

        return ('🔍 <b>Ваши персональные рекомендации</b> 🔍\n\n'
                f'Мы проанализировали заполненную анкету и учли все предпочтения, чтобы предложить наиболее подходящие '
                f'события.\n'
                f'Стремимся сделать ваше участие в <b>InsightClub</b> по-настоящему незабываемым и вдохновляющим на '
                f'новые идеи💡✨\n\n'
                f'Предлагаем индивидуальные рекомендации мероприятий в городе 🟢 <b>{user_city}</b>, которые идеально '
                f'соответствуют вашей деятельности и интересам👇\n\n'
                f'<i>Вы в любой момент можете изменить свой город и предпочтения в разделе:\n'
                '"⭐️ Главное меню" ➡️ "👤 Личный кабинет" ➡️ "⚙️ Настройки"</i>')

    @staticmethod
    def personal_selection_anketa() -> str:
        return ('🔍 <b>Ваши персональные рекомендации</b> 🔍\n\n'
                'Чтобы предложить вам индивидуальные рекомендации мероприятий, нам нужно узнать немного больше о ваших '
                'предпочтениях.\n'
                'Пройдите небольшую анкету из трех вопросов, и мы подберем для вас то, что будет интересным и полезным! '
                '🎉🌟\n\n'
                'Нажмите на кнопку "🔖 Начать заполнение анкеты" 👇')

    @staticmethod
    def anketa_step_1() -> str:
        return ('❓ <b>Укажите ваш вид деятельности</b>\n\n'
                '<i>Выберите один или несколько вариантов и нажмите кнопку "📨 Подтвердить"</i>')

    @staticmethod
    def anketa_step_2() -> str:
        return ('❓ <b>Выберите темы которые вам интересны</b>\n\n'
                '<i>Выберите один или несколько вариантов и нажмите кнопку "📨 Подтвердить"</i>')

    @staticmethod
    def anketa_step_3() -> str:
        return ('❓ <b>Укажите что вы продаете</b>\n\n'
                '<i>Выберите один или несколько вариантов и нажмите кнопку "📨 Подтвердить"</i>')

    @staticmethod
    async def end_of_anketa(user_id: int) -> str:
        products_custom_property_lvl2 = json.loads(config.products_custom_property_lvl2.get_secret_value())
        async with Database() as db:
            user_data: List[Record] = await db.get_user_data(user_id)
        user_activities_list = user_data[0].get('activities').split(',')
        products_activities_list = products_custom_property_lvl2.get('property102')
        user_topics_list = user_data[0].get('topics').split(',')
        products_topics_list = products_custom_property_lvl2.get('property104')
        user_sales_types_list = user_data[0].get('sales_types').split(',')
        products_sales_types_list = products_custom_property_lvl2.get('property106')

        user_activities_str = ', '.join(product_property['valueEnum'] for product_property in products_activities_list
                                        if product_property['value'] in user_activities_list)
        user_topics_str = ', '.join(product_property['valueEnum'] for product_property in products_topics_list
                                    if product_property['value'] in user_topics_list)
        user_sales_types_str = ', '.join(product_property['valueEnum'] for product_property in products_sales_types_list
                                         if product_property['value'] in user_sales_types_list)

        return ('🙌 Благодарим вас за заполнение анкеты! 📝 \n\n'
                '<b>Ваши ответы:</b>\n\n'
                f'<b>1. Вид деятельности:</b> {user_activities_str}\n'
                f'<b>2. Интересующие темы:</b> {user_topics_str}\n'
                f'<b>3. Что вы продаете:</b> {user_sales_types_str}\n\n'
                'Ваши ответы помогут нам лучше понять ваши предпочтения и предложить наиболее подходящие '
                'мероприятия. 💼🌟\n\n'
                'Теперь нажмите на кнопку "👑 Мероприятия для меня" и проверьте, что у нас для вас есть! 👇')

    @staticmethod
    def main_menu() -> str:
        return ('Привет!👋 Я бот компании InsightClub, эксперта в организации бизнес мероприятий, бизнес ужинов, '
                'нетворкингов и других интересных событий.\n\n'
                'Вот основные разделы, которые вы можете найти в меню:\n\n'
                '"🗓 Расписание" - узнайте о всех предстоящих мероприятиях в выбранном городе. Забронируйте и оплатите '
                'участие любым удобным для вас способом.\n\n'
                '"🎉 О нас" - узнайте больше о нашей компании и наших ценностях.\n\n'
                '"👑 Персональные рекомендации" - получайте персонализированные предложения о мероприятиях, '
                'соответствующих вашим личным предпочтениям.\n\n'
                '"👤 Личный кабинет" - управляйте своим профилем. В подразделе "📚 История заказов" вы найдете информацию о '
                'ваших предыдущих событиях (<i>*скоро будет доступно</i>), а в подразделе "⚙️ Настройки" вы сможете изменить город для поиска мероприятий и '
                'перепройти анкету предпочтений.\n\n'
                '"❓ Задать вопрос" - здесь вы можете связаться с представителем компании и задать любые вопросы, '
                'которые у вас возникли (<i>*скоро будет доступно</i>).')
