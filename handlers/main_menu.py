from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from b24_models import B24
from keyboards.user_keyboards import UserKb
from messages.user_messages import UserMessages
from sql import Database

router = Router()

photo_test = 'AgACAgIAAxkBAAIEG2U7oqxY5LreGS1owTJpvSxTEFpLAALL1TEbJYXYSU0w3y5-IE2JAQADAgADeQADMAQ'
photo_live = 'AgACAgIAAxkBAAILFmVtBr7N6HJGpK4PivHUyXcbxDuBAAL-1jEbcNNpSzWTmIkiTLIGAQADAgADeQADMwQ'


@router.message(CommandStart())
async def main_menu(message: Message, bot: Bot):
    user_id, username, full_name = message.from_user.id, message.from_user.username, message.from_user.full_name

    async with Database() as db:
        await bot.send_photo(chat_id=user_id,
                             photo=photo_live,
                             reply_markup=await UserKb().main_menu(user_id))
        try: await message.delete()
        except Exception: pass

        is_user_exists = await db.is_user_exist(user_id)
        if not is_user_exists:
            await db.add_new_user(user_id, username, full_name)

    await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]START[/I]')


@router.callback_query(F.data == 'start')
async def main_menu_from_cb(callback: CallbackQuery, bot: Bot):
    user_id, full_name = callback.from_user.id, callback.from_user.full_name
    await bot.send_photo(chat_id=user_id,
                         photo=photo_live,
                         reply_markup=await UserKb().main_menu(user_id))
    try: await callback.message.delete()
    except Exception: pass
    await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]Главное меню[/I]')

