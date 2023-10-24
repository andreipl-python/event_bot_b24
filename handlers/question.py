from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == 'question')
async def question(callback: CallbackQuery):
    await callback.answer(text='🛠 Скоро будет доступно!', show_alert=True)
