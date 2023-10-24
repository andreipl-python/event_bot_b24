import json
from typing import Union, Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config_reader import config
from keyboards.user_keyboards import UserKb, ChangeCityFactory
from messages.user_messages import UserMessages
from sql import Database

router = Router()


@router.callback_query(F.data == 'cabinet')
@router.message(Command('cabinet'))
async def cabinet(event: Union[CallbackQuery, Message]):
    user_id = event.from_user.id
    if isinstance(event, CallbackQuery):
        return await event.message.edit_text(text=UserMessages().cabinet(), reply_markup=await UserKb().cabinet())

    await event.answer(text=UserMessages().cabinet(), reply_markup=await UserKb().cabinet())
    try: await event.delete()
    except: pass


@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(text=await UserMessages().settings(user_id), reply_markup=await UserKb().settings())


@router.callback_query(F.data == 'change_city')
@router.callback_query(ChangeCityFactory.filter())
async def change_city(callback: CallbackQuery, callback_data: Optional[ChangeCityFactory] = None):
    user_id = callback.from_user.id
    if callback_data:
        products_cities = json.loads(config.products_cities.get_secret_value())
        products_cities = {int(key): value for key, value in products_cities.items()}
        new_city = products_cities.get(callback_data.city_id)
        async with Database() as db:
            await db.set_user_city(user_id, new_city)

    await callback.message.edit_text(text=await UserMessages().change_city(user_id),
                                     reply_markup=await UserKb().change_city(user_id))


@router.callback_query(F.data == 'history')
async def history(callback: CallbackQuery):
    await callback.answer(text='🛠 Скоро будет доступно!', show_alert=True)

