import traceback
import textwrap

from aiogram import Router, Bot
from aiogram.types import ErrorEvent

router = Router()


@router.errors()
async def error_handler(exception: ErrorEvent, bot: Bot):
    # Получаем трейсбек
    traceback_str = traceback.format_exc()

    # Разбиваем трейсбек на строки
    lines = traceback_str.splitlines()

    # Разбиваем каждую строку на части по 4096 символов
    wrapped_lines = []
    for line in lines:
        wrapped_line = textwrap.wrap(line, width=4096, replace_whitespace=False)
        wrapped_lines.extend(wrapped_line)

    # Объединяем части строк в сообщения
    messages = []
    current_message = ''
    for wrapped_line in wrapped_lines:
        if len(current_message + wrapped_line) > 4096:
            messages.append(current_message)
            current_message = wrapped_line + '\n'
        else:
            current_message += wrapped_line + '\n'

    # Добавляем последнее сообщение
    messages.append(current_message)

    # Отправляем сообщения в телеграм
    for message in messages:
        await bot.send_message(6008255128, f'```{message}```', parse_mode='Markdown')
