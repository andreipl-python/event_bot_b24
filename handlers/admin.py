from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from keyboards.admin_keyboards import AdminPanelKb
from sql import Database

router = Router()


class Admin(StatesGroup):
    set_start_message = State()


@router.callback_query(F.data == 'admin_panel')
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Выберите действие 😊', reply_markup=AdminPanelKb().admin_panel_kb())


@router.callback_query(F.data == 'change_start_message')
async def change_start_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='👇 Введите новое стартовое сообщение',
                                     reply_markup=AdminPanelKb().back_to_admin_panel())
    await state.set_state(Admin.set_start_message)
    await state.update_data(msg_to_edit=callback.message.message_id)


@router.message(Admin.set_start_message)
async def approve_new_start_message(message: Message, bot: Bot, state: FSMContext):
    chat_id = message.chat.id
    try:
        await message.delete()
    except:
        pass
    state_data = await state.get_data()
    await state.update_data(new_start_message=message.html_text)
    await bot.edit_message_text(text=f'‼️ Проверьте стартовое сообщение, всё верно?\n\n{message.html_text}',
                                chat_id=chat_id, message_id=state_data.get('msg_to_edit'),
                                reply_markup=AdminPanelKb().approve_change_start_message())


@router.callback_query(Admin.set_start_message, F.data == 'approve_change_start_message')
async def set_new_start_message(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    async with Database() as db:
        await db.set_start_message(state_data.get('new_start_message'))
    await callback.message.edit_text(text='🐸 Стартовое сообщение успешно изменено!',
                                     reply_markup=AdminPanelKb().back_to_admin_panel())
