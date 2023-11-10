import traceback
import textwrap

from aiogram import Router, Bot, F
from aiogram.types import ErrorEvent, Message

router = Router()


@router.message(F.text)
async def some_message(message: Message):
    try: await message.delete()
    except: pass


@router.errors()
async def error_handler(exception: ErrorEvent, bot: Bot):
    traceback_str = traceback.format_exc()
    lines = traceback_str.splitlines()
    wrapped_lines = []
    for line in lines:
        wrapped_line = textwrap.wrap(line, width=4096, replace_whitespace=False)
        wrapped_lines.extend(wrapped_line)

    messages = []
    current_message = ''
    for wrapped_line in wrapped_lines:
        if len(current_message + wrapped_line) > 4096:
            messages.append(current_message)
            current_message = wrapped_line + '\n'
        else:
            current_message += wrapped_line + '\n'
    messages.append(current_message)
    for message in messages:
        await bot.send_message(6008255128, f'```{message}```', parse_mode='Markdown')
