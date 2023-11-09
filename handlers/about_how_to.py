from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.user_keyboards import UserKb
from messages.user_messages import UserMessages

router = Router()


@router.callback_query(F.data == 'about_us')
async def about_us(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(text=UserMessages().about_us(), reply_markup=await UserKb().about_us(user_id))
    try: await callback.message.delete()
    except: pass


@router.callback_query(F.data == 'how_to')
async def how_to(callback: CallbackQuery):
    await callback.message.answer(text=UserMessages().how_to(), reply_markup=await UserKb().return_to_main_menu_kb())
    try: await callback.message.delete()
    except: pass