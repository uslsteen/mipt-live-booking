#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

import datetime

from datetime import date
from settings import TG_TOKEN

WEEKEND_VIEW = 7


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def get_next_date(base : date, offset : int) -> date:
    if isinstance(base, date):
        return base + datetime.timedelta(days=offset)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with inline buttons according to the following dates."""
    today = datetime.date.today()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{get_next_date(today, i)}", callback_data="1")
            for i in range(WEEKEND_VIEW // 2)
        ],
        [
            InlineKeyboardButton(
                f"{get_next_date(today, i)}", callback_data="1")
            for i in range(WEEKEND_VIEW // 2 + 1, WEEKEND_VIEW + 1)
        ],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please specify the date:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        f"{TG_TOKEN}").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
