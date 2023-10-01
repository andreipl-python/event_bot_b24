from typing import List

from asyncpg import Record


class UserMessages:

    def __init__(self):
        self.not_active_event = 'Мероприятие неактивно'

    @staticmethod
    def event_description(description: str) -> str:
        formatted_description = description.replace('<br>', '').replace('&nbsp;', '')
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
    def buy_event(is_active: bool) -> str:
        if is_active:
            return 'Сообщение-заглушка покупки'
        return 'Сообщение-заглушка неактивного мероприятия'
