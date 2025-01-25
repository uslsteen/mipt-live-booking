import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import filters, ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes

import months

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Set booking functions
def create_start_keyboard():
    keyboard = [[InlineKeyboardButton("Забронировать!", callback_data="book")]]
    return InlineKeyboardMarkup(keyboard)

def generate_dates():
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(8)]
    return dates

def create_date_keyboard(dates):
    keyboard = []
    for i in range(0, len(dates), 2):
        row = []
        if i < len(dates):
            D = dates[i].split('-')[0] + ' '
            M = months.months_list[int(dates[i].split('-')[1]) - 1] + ' '
            Y = dates[i].split('-')[2]
            date = D + M + Y
            row.append(InlineKeyboardButton(date, callback_data=dates[i]))
        if i + 1 < len(dates):
            D = dates[i + 1].split('-')[0] + ' '
            M = months.months_list[int(dates[i + 1].split('-')[1]) - 1] + ' '
            Y = dates[i + 1].split('-')[2]
            date = D + M + Y
            row.append(InlineKeyboardButton(date, callback_data=dates[i + 1]))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(keyboard)

def get_time_slots(date):
    day = datetime.strptime(date, '%d-%m-%Y').weekday()
    if day in [5, 6]:       # Weekend: Saturday=5, Sunday=6
        start_hour = 9
    else:
        start_hour = 18

    slots = [(start_hour + i * 3, start_hour + (i + 1) * 3) for i in range((24 - start_hour) // 3)]
    return [f"{slot[0]:02}:00 - {slot[1]:02}:00" for slot in slots]

# Set default handle commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = create_start_keyboard()
    await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=(
        "Здравствуйте\\, здесь Вы можете забронировать репточку\\! \n"
        "Ознакомиться с правилами поведения на репточке вы можете [здесь](https://vk.com/reptochkamipt?w=wall-222495319_63)\\. \n"
        "При возникновении проблем с бронированием обратитесь к @uslsteen\\."
         ),
    reply_markup=keyboard,
    parse_mode="MarkdownV2")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не знаю такую команду.")

# Set other handle commands
async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    
    if data == "book":
        dates = generate_dates()
        keyboard = create_date_keyboard(dates)
        await query.edit_message_text(text="Выберите дату брони:", reply_markup=keyboard)

    elif data == "back":
        keyboard = create_start_keyboard()
        await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=(
        "Здравствуйте\\, здесь Вы можете забронировать репточку\\! \n"
        "Ознакомиться с правилами поведения на репточке вы можете [здесь](https://vk.com/reptochkamipt?w=wall-222495319_63)\\. \n"
        "При возникновении проблем с бронированием обратитесь к @uslsteen\\."
         ),
    reply_markup=keyboard,
    parse_mode="MarkdownV2")
        
    else:
        slots = get_time_slots(data)
        slots_text = "\n".join(slots)
        D = data.split('-')[0] + ' '
        M = months.months_list[int(data.split('-')[1]) - 1]
        await query.edit_message_text(f"Доступные слоты на {D + M}: \n\n{slots_text}")

def main() -> None:
    application = ApplicationBuilder().token('8184651529:AAG4ULgtyS6kwsKo1Fg1-l9O378hn7SXJTI').build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    reservation_handler = CallbackQueryHandler(handle_date_selection)
    application.add_handler(reservation_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
