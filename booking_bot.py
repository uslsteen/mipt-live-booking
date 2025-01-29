
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from settings import TG_TOKEN
from booking_data import BookingSlot, BookingTime, get_next_week

from typing import Any
from enum import Enum
import inspect

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class BookingBot():
#
    TIMES = {
        False: [BookingTime(start="18:00"), BookingTime(start="21:00")],
        True: [
            BookingTime(start="9:00"),
            BookingTime(start="12:00"),
            BookingTime(start="15:00"),
            BookingTime(start="18:00"),
            BookingTime(start="21:00")
        ]
    }

    """
        Avaliable user interfaces (start menu)
    """
    INTERFACE = {
        "book": "Забронировать",
        "cancel_booking": "Отменить бронирование",
        "view_bookings": "Мои бронирования",
    }

    class State(Enum):
        START_MENU = 1
        DATE_SELECTION = 2
        TIME_SELECTION = 3

    def __init__(self):
        self._menu_keyboard = [
            [InlineKeyboardButton(ru_name, callback_data=meth_name)]
            for (meth_name, ru_name) in BookingBot.INTERFACE.items()
        ]
        #
        self._application = Application.builder().token(
            f"{TG_TOKEN}").build()
        #
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                BookingBot.State.START_MENU: [
                    CallbackQueryHandler(getattr(self, meth_name), pattern=meth_name)
                                            for meth_name in BookingBot.INTERFACE.keys()
                ],
                BookingBot.State.DATE_SELECTION: [
                    CallbackQueryHandler(self.select_time, pattern="date_*"),
                    CallbackQueryHandler(
                        self.back_to_start, pattern="back_to_start"),
                ],
                BookingBot.State.TIME_SELECTION: [
                    CallbackQueryHandler(
                        self.confirm_booking, pattern="time_*"),
                    CallbackQueryHandler(
                        self.back_to_dates, pattern="back_to_dates"),
                ],
            },
            fallbacks=[CommandHandler("start", self.start)],
        )

        self._application.add_handler(conv_handler)
        self._application.run_polling()
    #
    @staticmethod
    def parse_data(data : Any) -> Any:
        if isinstance(data, str):
            if data.startswith("date_"):
                return BookingSlot.deserialize(data)
            elif data.startswith("time_"):
                return BookingTime.deserialize(data)
        else:
            return None;

    @staticmethod
    def get_keyboard(list, callback_func) -> list:
        return [
        [InlineKeyboardButton(
            str(item), callback_data=callback_func(item))]
        for item in list
    ]

    """
        User interface implementation
    """
    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(self._menu_keyboard)

        if inspect.currentframe().f_back.f_code.co_name == self.start_over.__name__:
            query = update.callback_query
            await query.answer()
            #
            reply_markup = InlineKeyboardMarkup(self._menu_keyboard)

            await query.edit_message_text(
                "Выберите действие:", reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Выберите действие:", reply_markup=reply_markup
            )
        return BookingBot.State.START_MENU
    #
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.menu(update, context)
    #
    async def start_over(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.menu(update, context)
    #
    async def book(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        dates = get_next_week()

        keyboard = BookingBot.get_keyboard(dates, BookingSlot.serialize)
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_start")])
        #
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Выберите дату:", reply_markup=reply_markup)
        return BookingBot.State.DATE_SELECTION
    #
    async def select_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        selected_slot : BookingSlot = self.parse_data(query.data)

        context.user_data["selected_slot"] = selected_slot
        cur_times = BookingBot.TIMES.get(selected_slot.is_weekend)
        #
        keyboard = BookingBot.get_keyboard(cur_times, BookingTime.serialize)
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_dates")])
        #
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Выбрана дата: {str(selected_slot)}\nВыберите время:", reply_markup=reply_markup
        )
        return BookingBot.State.TIME_SELECTION
    #
    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        selected_slot : BookingSlot = context.user_data.get("selected_slot")
        selected_slot.time = self.parse_data(query.data)

        if selected_slot.is_valid:
            await query.edit_message_text(
                f"Вы забронировали на {str(selected_slot)} в {str(selected_slot.time)}."
            )
        else:
            await query.edit_message_text("Произошла ошибка, попробуйте снова.")

        return await self.start_over(update, context)
    #
    async def cancel_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Реализовать логику отмены бронирования")
        return ConversationHandler.END
    #
    async def view_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Ваши слоты:")
        return await self.start_over(update, context)
    #
    async def back_to_dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        dates = get_next_week()

        keyboard = BookingBot.get_keyboard(dates, BookingSlot.serialize)
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_start")])
        #
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Выберите дату:", reply_markup=reply_markup)
        return BookingBot.State.DATE_SELECTION
    #
    async def back_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.start_over(update, context)
