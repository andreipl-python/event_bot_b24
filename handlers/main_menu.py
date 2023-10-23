from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards.user_keyboards import UserKb
from sql import Database

router = Router()


@router.message(CommandStart())
async def main_menu(message: Message):
    user_id, username, full_name = message.from_user.id, message.from_user.username, message.from_user.full_name

    async with Database() as db:
        start_message = await db.get_start_message()
        await message.answer(text=start_message, reply_markup=await UserKb().main_menu(user_id))
        try: await message.delete()
        except Exception: pass

        is_user_exists = await db.is_user_exist(user_id)
        if not is_user_exists:
            await db.add_new_user(user_id, username, full_name)


@router.callback_query(F.data == 'start')
async def main_menu_from_cb(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with Database() as db:
        start_message = await db.get_start_message()

    await callback.message.answer(text=start_message, reply_markup=await UserKb().main_menu(user_id))
    try: await callback.message.delete()
    except Exception: pass
