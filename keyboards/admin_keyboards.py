from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ApprovePaymentCallbackFactory(CallbackData, prefix='approvedealpay'):
    deal_id: Optional[int] = None


class AdminPanelKb(InlineKeyboardBuilder):

    def admin_panel_kb(self) -> InlineKeyboardMarkup:
        self.button(
            text='⚡️ Заменить стартовое сообщение',
            callback_data='change_start_message')
        self.button(
            text='💰 Зарегистрировать оплату',
            callback_data='payment_registration'
        )
        self.button(
            text='🔙 Календарь событий',
            callback_data='start'
        )
        self.adjust(1)
        return self.as_markup()

    def back_to_admin_panel(self) -> InlineKeyboardMarkup:
        self.button(
            text='🔙 Назад',
            callback_data='admin_panel'
        )
        return self.as_markup()

    def approve_change_start_message(self) -> InlineKeyboardMarkup:
        self.button(
            text='✅ Да', callback_data='approve_change_start_message'
        )
        self.button(
            text='❌ Нет', callback_data='change_start_message'
        )
        self.adjust(2)
        return self.as_markup()

    def approve_payment_registration(self, deal_id: int) -> InlineKeyboardMarkup:
        self.button(
            text='✅ Да', callback_data=ApprovePaymentCallbackFactory(deal_id=deal_id)
        )
        self.button(
            text='❌ Нет', callback_data='payment_registration'
        )
        self.adjust(2)
        return self.as_markup()
