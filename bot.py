
import logging
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from settings import TG_TOKEN
from datetime import date
from typing import Any

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_weekend(day: Any) -> bool:
    weekdays_num = 4
    #
    if isinstance(day, int):
        return day > weekdays_num
    elif isinstance(day, str):
        return int(day) > weekdays_num
    elif isinstance(day, date):
        return day.weekday() > weekdays_num

def get_next_date(base: date, offset: int) -> date:
    if isinstance(base, date):
        return base + datetime.timedelta(days=offset)
    else:
        return None

def get_next_week(base: date) -> list:
    week_lenght = 8
    if isinstance(base, date):
        return [get_next_date(base, i)
                for i in range(week_lenght)]
    else:
        return None

def get_keyboard(list, callback_func) -> list:
    return [
        [InlineKeyboardButton(
            str(item), callback_data=callback_func(item))]
        for item in list
    ]

class BookingBot():
#
    TIMES = dict({                                              \
        False : ["18:00", "21:00"],                             \
        True : ["9:00", "12:00", "15:00", "18:00", "21:00"]})   \

    #
    (
        START_MENU,
        DATE_SELECTION,
        TIME_SELECTION,
    ) = map(chr, range(3))

    def __init__(self):
        self._menu_keyboard = [
            [InlineKeyboardButton("Забронировать", callback_data="book")],
            [InlineKeyboardButton("Отменить бронирование",
                                  callback_data="cancel")],
            [InlineKeyboardButton("Мои бронирования",
                                  callback_data="my_bookings")],
        ]
        #
        self._application = Application.builder().token(
            f"{TG_TOKEN}").build()
        #
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                BookingBot.START_MENU: [
                    CallbackQueryHandler(self.book, pattern="book"),
                    CallbackQueryHandler(self.cancel_booking, pattern="cancel"),
                    CallbackQueryHandler(
                        self.my_bookings, pattern="my_bookings"),
                ],
                BookingBot.DATE_SELECTION: [
                    CallbackQueryHandler(self.select_time, pattern="date_*"),
                    CallbackQueryHandler(
                        self.back_to_start, pattern="back_to_start"),
                ],
                BookingBot.TIME_SELECTION: [
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
    def get_date(day) -> str:
        if isinstance(day, date):
            return f"date_{str(day)}_{day.weekday()}"
        else:
            return None

    @staticmethod
    def get_time(time) -> str:
        if isinstance(time, str):
            return f"time_{time}"
        else:
            return None

    @staticmethod
    def parse_data(data : Any):
        if isinstance(data, str):
            if data.startswith("date_"):
                splitted = data.split("_")
                return splitted[1], splitted[2]
            elif data.startswith("time_"):
                return data.split("_")[1]
        else:
            return None;

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        reply_markup = InlineKeyboardMarkup(self._menu_keyboard)

        await update.message.reply_text(
            "Выберите действие:", reply_markup=reply_markup
        )
        return BookingBot.START_MENU
        #
    #
    async def start_over(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()
        #
        reply_markup = InlineKeyboardMarkup(self._menu_keyboard)

        await query.edit_message_text(
            "Выберите действие:", reply_markup=reply_markup
        )
        return BookingBot.START_MENU
        #
    #
    async def book(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()

        dates = get_next_week(date.today())

        keyboard = get_keyboard(dates, BookingBot.get_date)
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_start")])
        #
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Выберите дату:", reply_markup=reply_markup)
        return BookingBot.DATE_SELECTION
        #
    #
    async def select_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()

        selected_date, weekno = self.parse_data(query.data)

        context.user_data["selected_date"] = selected_date
        cur_times = BookingBot.TIMES.get(is_weekend(weekno))
        #
        keyboard = get_keyboard(cur_times, BookingBot.get_time)
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_dates")])
        #
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Выбрана дата: {selected_date}\nВыберите время:", reply_markup=reply_markup
        )
        return BookingBot.TIME_SELECTION
        #
    #
    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()

        selected_time = self.parse_data(query.data)
        selected_date = context.user_data.get("selected_date")

        if selected_date and selected_time:
            await query.edit_message_text(
                f"Вы забронировали на {selected_date} в {selected_time}."
            )
        else:
            await query.edit_message_text("Произошла ошибка, попробуйте снова.")

        return await self.start_over(update, context)
        #
    #
    async def cancel_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Реализовать логику отмены бронирования")
        return ConversationHandler.END
    #
    async def my_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Ваши слоты:")
        return await self.start_over(update, context)
        #
    #
    async def back_to_dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()

        dates = get_next_week(date.today())

        keyboard = get_keyboard(dates, BookingBot.get_date)
        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_start")])
        #
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Выберите дату:", reply_markup=reply_markup)
        return BookingBot.DATE_SELECTION
        #
    #
    async def back_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        return await self.start_over(update, context)
