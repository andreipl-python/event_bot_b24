from typing import List

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove
from asyncpg import Record

from sql import Database
from b24_models import B24
from config_reader import config
from keyboards.user_keyboards import (UserKb, UserReplyKb, SelectEventCallbackFactory, BuyEventCallbackFactory,
                                      BuyEventPayMethodFactory)
from messages.user_messages import UserMessages

router = Router()


class User(StatesGroup):
    state = State()


@router.message(Command('calendar'))
async def start(message: Message):
    user_id, username, full_name = message.from_user.id, message.from_user.username, message.from_user.full_name

    async with Database() as db:
        start_message = await db.get_start_message()
        await message.answer(text=start_message, reply_markup=await UserKb().get_products_kb(user_id))
        try: await message.delete()
        except Exception: pass

        is_user_exists = await db.is_user_exist(user_id)
        if not is_user_exists:
            await db.add_new_user(user_id, username, full_name)

    await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]START[/I]')


@router.message(F.contact)
async def contact(message: Message, state: FSMContext, bot: Bot):
    user_id, state_data = message.from_user.id, await state.get_data()
    await message.answer(text=UserMessages().successful_contact, reply_markup=ReplyKeyboardRemove())
    try: await message.delete()
    except: pass
    try: await bot.delete_message(user_id, state_data.get('msg_to_del'))
    except: pass
    await state.clear()

    async with Database() as db:
        start_message = await db.get_start_message()
    await message.answer(text=start_message, reply_markup=await UserKb().get_products_kb(user_id))

    async with Database() as db:
        await db.set_phone(user_id, message.contact.phone_number)
        user_data: List[Record] = await db.get_user_data(user_id)
    await B24().update_contact_phone(user_data[0].get('b24_id'), message.contact.phone_number)
    await B24().add_phone_task(user_data[0].get('b24_id'), 1)
    await B24().send_message_to_ol(user_id, 'Система',
                                   '[B]Пользователь запросил обратный звонок. Поставлена задача.[/B]')


# @router.message(Command('send_1'))
# async def send_custom(message: Message, bot: Bot):
#     async with Database() as db:
#         users_list: List[Record] = await db.get_all_users()
#         success_counter, fail_counter = 0, 0
#         for user in users_list:
#             user_id = user.get('user_id')
#             try:
#                 await bot.send_photo(chat_id=user_id,
#                                      photo='AgACAgIAAxkBAAICtmUuuJE8EAxNuPQd2qhFwidt-zQXAAK2zjEb9lJ4SeZb9L7dmm0XAQADAgADeQADMAQ',
#                                      caption=UserMessages().custom_send(), reply_markup=await UserKb().event_kb(268))
#                 await B24().send_message_to_ol(user_id, 'Система',
#                                                'Отправлено сообщение-рассылка. Бизнес-ужин 19.10 четверг в 18.00.')
#                 success_counter += 1
#                 await asyncio.sleep(0.5)
#             except:
#                 await db.set_bot_blocked(user_id, True)
#                 fail_counter += 1
#
#         await bot.send_message(chat_id=6008255128, text=f"<b>Итоги рассылки:</b>\n\nВсего адресатов: {len(users_list)}\n"
#                                                         f"Доставлено успешно: {success_counter}\n"
#                                                         f"Не доставлено (вероятно заблокировали бота): {fail_counter}")


# @router.message(F.photo)
# async def return_photo_id(message: Message):
#     await message.answer(message.photo[-1].file_id)


# @router.message(F.text)
# async def some_message(message: Message):
#     user_id, full_name = message.from_user.id, message.from_user.full_name
#     await B24().send_message_to_ol(user_id, full_name, f'{message.text}')


@router.callback_query(F.data == 'call_ask')
async def ask_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User.state)
    msg_to_del = await callback.message.answer(text=UserMessages().ask_phone, reply_markup=UserReplyKb().ask_contact_kb())
    await state.update_data(msg_to_del=msg_to_del.message_id)
    try: await callback.message.delete()
    except: pass


@router.callback_query(F.data == 'calendar')
async def calendar_from_cb(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with Database() as db:
        start_message = await db.get_start_message()

    await callback.message.answer(text=start_message, reply_markup=await UserKb().get_products_kb(user_id))
    try: await callback.message.delete()
    except Exception: pass


@router.callback_query(SelectEventCallbackFactory.filter())
async def select_event(callback: CallbackQuery, callback_data: SelectEventCallbackFactory):
    user_id, full_name, username = callback.from_user.id, callback.from_user.full_name, callback.from_user.username

    async with Database() as db:
        event_data: List[Record] = await db.get_product_by_id(callback_data.product_id)
        if not event_data:
            await callback.message.answer(text=UserMessages().not_active_event,
                                                    reply_markup=await UserKb().return_to_start_kb())
            try: await callback.message.delete()
            except Exception: pass
            return

        event_description: str = event_data[0].get('description')
        await callback.message.answer(text=UserMessages().event_description(event_description),
                                         reply_markup=await UserKb().event_kb(callback_data.product_id))
        try: await callback.message.delete()
        except Exception: pass

        message_keyboard = callback.message.reply_markup.inline_keyboard
        button_text = ''.join([i[0].text for i in message_keyboard
                               if i[0].callback_data == f'{SelectEventCallbackFactory.__prefix__}:{callback_data.product_id}'])
        await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]{button_text}[/I]')

        await db.add_button_count(user_id, button_text)

        is_b24_contact_exist = await db.is_b24_contact_exist(user_id)
        # если не было контакта создано в Б24 то создаю контакт
        if not is_b24_contact_exist:
            im_link = None
            while im_link is None:
                user_data = await db.get_user_data(user_id)
                im_link = user_data[0].get('im_link_b24')
            b24_id = await B24().make_new_contact(user_id, full_name, username, im_link)
            await db.set_b24_id(user_id, b24_id)

            # перевожу лид на стадию "Выслано предложение" и привязываю контакт
            lead_id = user_data[0].get('lead_id')
            await B24().update_lead_status(lead_id, 'PROCESSED')
            await B24().update_lead_contact(lead_id, b24_id)


@router.callback_query(BuyEventCallbackFactory.filter())
async def buy_event(callback: CallbackQuery, callback_data: BuyEventCallbackFactory, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    if state_data.get('msg_to_del'):
        try: await bot.delete_message(callback.message.chat.id, state_data.get('msg_to_del'))
        except Exception: pass
        await state.clear()
    user_id, full_name = callback.from_user.id, callback.from_user.full_name
    product_id = callback_data.product_id
    async with Database() as db:
        event_data: List[Record] = await db.get_product_by_id(product_id)
        if not event_data:
            await callback.message.answer(text=UserMessages().not_active_event,
                                                    reply_markup=await UserKb().return_to_start_kb())
            try: await callback.message.delete()
            except Exception: pass
            return

        event_name: str = event_data[0].get('name')

        # получаю сделки по пользователю, данные по пользователю
        deals_data: List[Record] = await db.get_user_deals(user_id)
        user_data = await db.get_user_data(user_id)
        lead_id = user_data[0].get('lead_id')
        contact_id = user_data[0].get('b24_id')
        # если нет сделок - перевожу лид в конвертированные
        if not deals_data:
            await B24().update_lead_status(lead_id, 'CONVERTED')

        # проверяю есть ли сделка с таким товаром, если нет - создаю
        deal_exist = False
        product_price: float = event_data[0].get('price')
        if deals_data:
            for record in deals_data:
                if record.get('product_id') == product_id and not record.get('paid'):
                    deal_exist = True
                    deal_id = record.get('deal_id')
                    break

        if not deal_exist:
            deal_data = await B24().add_new_deal(full_name, event_name, contact_id)
            deal_id: int = deal_data.get('result')

        await callback.message.answer(text="Выберите удобный для Вас способ оплаты:",
                                      reply_markup=await UserKb().payment_methods_kb(product_id, deal_id))
        try: await callback.message.delete()
        except Exception: pass

        await B24().send_message_to_ol(user_id, full_name, f'[B]Нажата кнопка[/B] [I]Купить {event_name}[/I]')
        if not deal_exist:
            await B24().add_product_to_deal(deal_id, product_id, product_price)
            await db.add_new_deal(user_id, deal_id, product_id, product_price)
            deal_url = f'https://rudneva.bitrix24.pl/crm/deal/details/{deal_id}/'
            await B24().send_message_to_ol(user_id, 'Система',
                                           f'[URL={deal_url}][B]Создана сделка на сумму {product_price} zł[/B][/URL]')
        # регистрирую нажатие кнопки Купить
        await db.add_button_count(user_id, f'Купить {event_name}')


@router.callback_query(BuyEventPayMethodFactory.filter())
async def payment_by_method(callback: CallbackQuery, callback_data: BuyEventPayMethodFactory, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id

    async with Database() as db:
        event_data: List[Record] = await db.get_product_by_id(callback_data.product_id)
        if not event_data:
            await callback.message.answer(text=UserMessages().not_active_event,
                                                    reply_markup=await UserKb().return_to_start_kb())
            try: await callback.message.delete()
            except Exception: pass
            return

        event_name: str = event_data[0].get('name')
        product_price: float = event_data[0].get('price')

    if callback_data.method == 'card':
        invoice = await bot.send_invoice(
            title=event_name, description='Оплата участия картой Visa/MasterCard',
            payload=f'{callback_data.product_id}:{callback_data.deal_id}',
            provider_token=config.stripe_test_token.get_secret_value(), currency='PLN',
            prices=[LabeledPrice(label='1 шт', amount=int(product_price * 100))], chat_id=user_id
        )
        return_msg = await callback.message.answer(text='Нажмите на кнопку ниже, чтобы выбрать другой способ оплаты 👇',
                                                   reply_markup=await UserKb().return_to_payment_methods(
                                                    product_id=callback_data.product_id, with_calendar=False))
        await state.set_state(User.state)
        await state.update_data(msg_to_del=invoice.message_id, cb_to_del=return_msg.message_id)
        try: await callback.message.delete()
        except Exception: pass

    if callback_data.method in ['blik', 'bank']:
        await callback.message.answer(
            text=UserMessages().other_payment(callback_data.deal_id, event_name, product_price, callback_data.method),
            reply_markup=await UserKb().return_to_payment_methods(product_id=callback_data.product_id, with_calendar=True))
        try: await callback.message.delete()
        except Exception: pass


@router.pre_checkout_query()
async def pre_checkout_approve(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    product_id = pre_checkout_query.invoice_payload.split(':')[0]
    deal_id = pre_checkout_query.invoice_payload.split(':')[1]

    async with Database() as db:
        event_data: List[Record] = await db.get_product_by_id(int(product_id))
        deal_data: List[Record] = await db.get_user_deal_by_deal_id(int(deal_id))

    if not event_data:
        return await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,
                                                   error_message='Мероприятие уже прошло, либо недоступно для покупки')
    if deal_data[0].get('paid'):
        return await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,
                                                   error_message='Этот заказ уже оплачен вами другим методом оплаты. '
                                                                 'Для повторной покупки сформируйте новый заказ.')

    return await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext, bot: Bot):
    user_id, state_data = message.from_user.id, await state.get_data()
    payment_data = message.successful_payment
    product_id = int(payment_data.invoice_payload.split(':')[0])
    async with Database() as db:
        product_data: List[Record] = await db.get_product_by_id(product_id)
        product_name = product_data[0].get('name')
    await message.answer(text=UserMessages().successful_payment(payment_data, product_name),
                         reply_markup=await UserKb().return_to_start_kb())

    try: await bot.delete_message(user_id, state_data.get('msg_to_del'))
    except Exception: pass
    try: await bot.delete_message(user_id, state_data.get('cb_to_del'))
    except Exception: pass
    try: await message.delete()
    except Exception: pass

    await state.clear()

    async with Database() as db:
        deal_id = int(payment_data.invoice_payload.split(':')[1])
        deal_url = f'https://rudneva.bitrix24.pl/crm/deal/details/{deal_id}/'
        currency = payment_data.currency
        total_amount = payment_data.total_amount

        await db.add_payment(user_id, payment_data)
        await db.set_paid_deal(deal_id)
        await B24().update_deal_stage(deal_id, 'WON')
        await B24().send_message_to_ol(user_id, 'Система',
                                       f'Произведена оплата:\nСумма: [B]{total_amount/100} {currency}[/B]\n'
                                       f'Сделка: [URL={deal_url}][B]ID {deal_id}[/B][/URL]')
        await B24().send_message_to_ol(user_id, 'Система',
                                       f'Пользователю отправлено подтверждение:\n\n'
                                       f'{UserMessages().successful_payment(payment_data, product_name)}')




