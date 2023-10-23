from typing import Union

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.user_keyboards import UserKb
from messages.user_messages import UserMessages

router = Router()


@router.callback_query(F.data == 'cabinet')
@router.message(Command('cabinet'))
async def cabinet(event: Union[CallbackQuery, Message]):
    user_id = event.from_user.id
    if isinstance(event, CallbackQuery):
        return await event.message.edit_text(text=await UserMessages().cabinet(user_id), reply_markup=await UserKb().cabinet())

    await event.answer(text=await UserMessages().cabinet(user_id), reply_markup=await UserKb().cabinet())
    try: await event.delete()
    except: pass


@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(text=await UserMessages().settings(user_id), reply_markup=await UserKb().settings())
    try: await callback.message.delete()
    except: pass


@router.callback_query(F.data == 'change_city')
async def change_city(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(text=await UserMessages().change_city(user_id),
                                  reply_markup=await UserKb().change_city(user_id))

