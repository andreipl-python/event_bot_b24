from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from b24_models import B24
from keyboards.user_keyboards import UserKb
from messages.user_messages import UserMessages
from sql import Database

router = Router()


@router.message(CommandStart())
async def main_menu(message: Message):
    user_id, username, full_name = message.from_user.id, message.from_user.username, message.from_user.full_name

    async with Database() as db:
        await message.answer(text=UserMessages().main_menu(), reply_markup=await UserKb().main_menu(user_id))
        try: await message.delete()
        except Exception: pass

        is_user_exists = await db.is_user_exist(user_id)
        if not is_user_exists:
            await db.add_new_user(user_id, username, full_name)

    await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]START[/I]')


@router.callback_query(F.data == 'start')
async def main_menu_from_cb(callback: CallbackQuery):
    user_id, full_name = callback.from_user.id, callback.from_user.full_name
    await callback.message.edit_text(text=UserMessages().main_menu(), reply_markup=await UserKb().main_menu(user_id))
    await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]Главное меню[/I]')

