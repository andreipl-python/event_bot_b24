from typing import Union, Optional

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from keyboards.user_keyboards import UserKb, AnketaStep1Factory, AnketaStep2Factory, AnketaStep3Factory
from sql import Database

router = Router()


class Anketa(StatesGroup):
    anketa = State()


@router.message(Command('personal'))
@router.callback_query(F.data == 'personal')
async def personal_events(event: Union[CallbackQuery, Message], bot: Bot):
    user_id = event.from_user.id

    async with Database() as db:
        is_filled_out_the_form: bool = await db.is_filled_out_the_form(user_id)

    if not is_filled_out_the_form:  # не проходил анкету
        if isinstance(event, CallbackQuery):
            return await event.message.edit_text(text='Текст персонального подбора с анкетой',
                                                    reply_markup=await UserKb().personal_anketa())
        try: await event.delete()
        except: pass
        return await event.answer(text='Текст персонального подбора с анкетой',
                                  reply_markup=await UserKb().personal_anketa())

    if isinstance(event, CallbackQuery):
        return await event.message.edit_text(text='Текст персонального подбора',
                                             reply_markup=await UserKb().get_personal_products_kb(user_id))

    await event.answer(text='Текст персонального подбора', reply_markup=await UserKb().get_personal_products_kb(user_id))
    try: await event.delete()
    except: pass


@router.callback_query(F.data == 'anketa')
@router.callback_query(AnketaStep1Factory.filter())
async def anketa_step1(callback: CallbackQuery,  state: FSMContext, callback_data: Optional[AnketaStep1Factory] = None):
    current_state = await state.get_state()
    if not current_state:
        await state.set_state(Anketa.anketa)
    state_data = await state.get_data()
    buttons = state_data.get('buttons')
    if callback.data == 'anketa':
        if not buttons:
            buttons = {'168': False, '170': False, '172': False, '174': False}
        await state.update_data(buttons=buttons)
        await callback.message.edit_text(text='Первый вопрос анкеты',
                                         reply_markup=await UserKb().anketa_step1(buttons))
    if callback_data:
        buttons[callback_data.active_id] = not buttons[callback_data.active_id]
        await callback.message.edit_text(text='Первый вопрос анкеты',
                                         reply_markup=await UserKb().anketa_step1(buttons))


@router.callback_query(F.data == 'approve_anketa_step1')
@router.callback_query(AnketaStep2Factory.filter())
async def anketa_step2(callback: CallbackQuery, state: FSMContext, callback_data: Optional[AnketaStep2Factory] = None):
    state_data = await state.get_data()

    buttons: dict = state_data.get('buttons')
    if all(value is False for value in buttons.values()):
        return callback.answer(text='Пожалуйста, выберите хотя бы один ответ 😊', show_alert=True)

    buttons2 = state_data.get('buttons2')
    if callback.data == 'approve_anketa_step1':
        if not buttons2:
            buttons2 = {'176': False, '178': False, '180': False, '182': False, '184': False, '186': False, '188': False,
                        '190': False, '192': False, '194': False, '196': False}
        await state.update_data(buttons2=buttons2)
        await callback.message.edit_text(text='Второй вопрос анкеты',
                                         reply_markup=await UserKb().anketa_step2(buttons2))
    if callback_data:
        buttons2[callback_data.topic_id] = not buttons2[callback_data.topic_id]
        await callback.message.edit_text(text='Второй вопрос анкеты',
                                         reply_markup=await UserKb().anketa_step2(buttons2))


@router.callback_query(F.data == 'approve_anketa_step2')
@router.callback_query(AnketaStep3Factory.filter())
async def anketa_step3(callback: CallbackQuery, state: FSMContext, callback_data: Optional[AnketaStep3Factory] = None):
    state_data = await state.get_data()

    buttons2: dict = state_data.get('buttons2')
    if all(value is False for value in buttons2.values()):
        return callback.answer(text='Пожалуйста, выберите хотя бы один ответ 😊', show_alert=True)

    if callback.data == 'approve_anketa_step2':
        buttons3 = {'198': False, '200': False, '202': False}
        await state.update_data(buttons3=buttons3)
        await callback.message.edit_text(text='Третий вопрос анкеты',
                                         reply_markup=await UserKb().anketa_step3(buttons3))
    if callback_data:
        buttons3: dict = state_data.get('buttons3')
        if callback_data.sale_type_id == '202':  # ничего
            buttons3 = {'198': False, '200': False, '202': True}
        else:
            buttons3[callback_data.sale_type_id] = not buttons3[callback_data.sale_type_id]

        try:
            await callback.message.edit_text(text='Третий вопрос анкеты',
                                             reply_markup=await UserKb().anketa_step3(buttons3))
        except TelegramBadRequest:
            await callback.answer()


@router.callback_query(F.data == 'approve_anketa_step3')
async def end_of_anketa(callback: CallbackQuery, state: FSMContext):
    user_id, state_data = callback.from_user.id, await state.get_data()

    buttons3: dict = state_data.get('buttons3')
    if all(value is False for value in buttons3.values()):
        return callback.answer(text='Пожалуйста, выберите хотя бы один ответ 😊', show_alert=True)

    buttons, buttons2 = state_data.get('buttons'), state_data.get('buttons2')

    activities = ','.join(active_id for active_id, status in buttons.items() if status)
    topics = ','.join(topic for topic, status in buttons2.items() if status)
    sales_types = ','.join(sale_type_id for sale_type_id, status in buttons3.items() if status)

    async with Database() as db:
        await db.set_user_form_result(user_id, activities, topics, sales_types)

    await callback.message.edit_text(text='Конец анкеты труляля', reply_markup=await UserKb().end_of_anketa())
    await state.clear()



