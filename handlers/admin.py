from typing import List

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, SuccessfulPayment
from asyncpg import Record

from b24_models import B24
from keyboards.admin_keyboards import AdminPanelKb, ApprovePaymentCallbackFactory
from keyboards.user_keyboards import UserKb
from messages.user_messages import UserMessages
from sql import Database

router = Router()


class Admin(StatesGroup):
    set_start_message = State()
    set_payment_registration = State()


@router.callback_query(F.data == 'admin_panel')
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text='Выберите действие 😊', reply_markup=AdminPanelKb().admin_panel_kb())


@router.callback_query(F.data == 'payment_registration')
async def payment_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='👇 Введите номер заказа для регистрации оплаты',
                                     reply_markup=AdminPanelKb().back_to_admin_panel())
    await state.set_state(Admin.set_payment_registration)
    await state.update_data(msg_to_edit=callback.message.message_id)


@router.message(Admin.set_payment_registration)
async def approve_payment_registration(message: Message, bot: Bot, state: FSMContext):
    chat_id, state_data = message.chat.id, await state.get_data()
    msg_to_edit = state_data.get('msg_to_edit')
    try:
        await message.delete()
    except Exception:
        pass

    try:
        deal_id = int(message.text)
    except ValueError:
        try:
            return await bot.edit_message_text(
                text='Некорректное значение номера заказа, в нём могут быть только цифры. '
                     'Пожалуйста, введите ещё раз:', chat_id=chat_id, message_id=msg_to_edit,
                reply_markup=AdminPanelKb().back_to_admin_panel())
        except Exception:
            return

    async with Database() as db:
        deal_data: List[Record] = await db.get_user_deal_by_deal_id(deal_id)
        if not deal_data:
            try:
                return await bot.edit_message_text(text='Заказ с таким номером не найден. Пожалуйста, введите еще раз:',
                                                   chat_id=chat_id, message_id=msg_to_edit,
                                                   reply_markup=AdminPanelKb().back_to_admin_panel())
            except Exception:
                return
        if deal_data[0].get('paid'):
            try:
                return await bot.edit_message_text(text='Заказ с таким номером уже отмечен как оплаченный. '
                                                        'Пожалуйста, введите еще раз:',
                                                   chat_id=chat_id, message_id=msg_to_edit,
                                                   reply_markup=AdminPanelKb().back_to_admin_panel())
            except Exception:
                return

        user_data: List[Record] = await db.get_user_data(deal_data[0].get('user_id'))
        user_link = f'<a href="https://t.me/{user_data[0].get("username")}">{user_data[0].get("full_name")}</a>' \
            if user_data[0].get("username") else f'<code>{user_data[0].get("full_name")}</code>'
        product_data: List[Record] = await db.get_product_by_id(deal_data[0].get('product_id'))
        await bot.edit_message_text(text=('Заказ найден! Проверьте данные:\n\n'
                                          f'<b>ID сделки:</b> <code>{deal_id}</code>\n'
                                          f'<b>Cумма заказа:</b> <code>{deal_data[0].get("opportunity")}</code>\n'
                                          f'<b>Мероприятие:</b> <code>{product_data[0].get("name")}</code>\n'
                                          f'<b>ID пользователя Telegram:</b> <code>{deal_data[0].get("user_id")}</code>\n'
                                          f'<b>Имя пользователя Telegram:</b> {user_link}\n\n'
                                          f'Подтвердить оплату?'),
                                    chat_id=chat_id, message_id=msg_to_edit,
                                    reply_markup=AdminPanelKb().approve_payment_registration(deal_id),
                                    disable_web_page_preview=True)
        await state.clear()


@router.callback_query(ApprovePaymentCallbackFactory.filter())
async def set_new_payment(callback: CallbackQuery, callback_data: ApprovePaymentCallbackFactory, bot: Bot):
    deal_id = callback_data.deal_id
    async with Database() as db:
        deal_data: List[Record] = await db.get_user_deal_by_deal_id(deal_id)
        product_data: List[Record] = await db.get_product_by_id(deal_data[0].get('product_id'))
        await db.set_paid_deal(deal_id)
        payment_data = SuccessfulPayment(currency='PLN', total_amount=int(product_data[0].get('price') * 100),
                                         invoice_payload=f'{deal_data[0].get("product_id")}:{deal_id}',
                                         telegram_payment_charge_id='blik_or_bank',
                                         provider_payment_charge_id=f'{deal_id}')
        await db.add_payment(deal_data[0].get('user_id'), payment_data)
        await B24().update_deal_stage(deal_id, 'WON')
        deal_url = f'https://rudneva.bitrix24.pl/crm/deal/details/{deal_id}/'
        await B24().send_message_to_ol(deal_data[0].get('user_id'), 'Система',
                                       f'Зарегистрирована оплата:\nСумма: [B]{product_data[0].get("price")} PLN[/B]\n'
                                       f'Сделка: [URL={deal_url}][B]ID {deal_id}[/B][/URL]')

    await bot.send_message(chat_id=deal_data[0].get('user_id'),
                           text=UserMessages().successful_payment(payment_data, product_data[0].get('name')),
                           reply_markup=await UserKb().return_to_start_kb())
    await callback.message.edit_text(text='Оплата успешно зарегистрирована!',
                                     reply_markup=AdminPanelKb().back_to_admin_panel())


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
