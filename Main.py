import telebot
from telebot import types

TOKEN = '8941488725:AAFes8uQVjbeoOOuKKnuHyL00D2YXKpl8WA '
bot = telebot.TeleBot(TOKEN)

# Хранилища
waiting_users = []       # Очередь ищущих
active_pairs = {}        # Активные пары {user1: user2, user2: user1}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton("🔍 Найти собеседника", callback_data="search")
    markup.add(btn)
    bot.send_message(message.chat.id, "Привет! Я бот для анонимного общения. Нажми кнопку ниже, чтобы найти собеседника.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "search")
def search(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)

    if user_id in active_pairs:
        bot.send_message(user_id, "Вы уже в чате! Нажмите 'Стоп', чтобы выйти.")
        return

    if user_id in waiting_users:
        bot.send_message(user_id, "Вы уже в поиске...")
        return

    if waiting_users:
        # Нашли пару
        partner = waiting_users.pop(0)
        active_pairs[user_id] = partner
        active_pairs[partner] = user_id

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("❌ Стоп", callback_data="stop"))

        bot.send_message(user_id, "Собеседник найден! Общайтесь.", reply_markup=markup)
        bot.send_message(partner, "Собеседник найден! Общайтесь.", reply_markup=markup)
    else:
        # Встаем в очередь
        waiting_users.append(user_id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("❌ Отменить поиск", callback_data="stop"))
        bot.send_message(user_id, "Ищем собеседника...", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "stop")
def stop(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)

    if user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "Поиск отменен.")
        start(call.message)
        return

    if user_id in active_pairs:
        partner = active_pairs[user_id]
        del active_pairs[user_id]
        if partner in active_pairs:
            del active_pairs[partner]
        bot.send_message(partner, "Собеседник завершил чат. Нажмите /start чтобы найти нового.")
        bot.send_message(user_id, "Чат завершен.")
        start(call.message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    if user_id in active_pairs:
        partner = active_pairs[user_id]
        try:
            bot.send_message(partner, f"Аноним: {message.text}")
        except:
            bot.send_message(user_id, "Не удалось отправить. Собеседник вышел.")
    else:
        bot.send_message(user_id, "Ты пока не в чате. Нажми /start -> Найти собеседника.")

print("Бот запущен...")
bot.infinity_polling()
