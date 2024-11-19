from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import sqlite3, re
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

# Команды бота
async def start_command(update, context):
    await update.message.reply_text("Hello! I'm your bot.")

async def help_command(update, context):
    await update.message.reply_text("Use /start to get started.")

# Основная функция
async def main():
    # Инициализация бота с токеном
    app = ApplicationBuilder().token("7280297934:AAHspvKvMh7PJn4sTszwu43v4SzQWTZY7Rk").build()

    # Настройка команд для бота
    await set_bot_commands(app)

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("log", log_data))
    app.add_handler(CommandHandler("edit", edit_data))
    app.add_handler(CommandHandler("delete", delete_data))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("help", show_help))

    # Запуск приложения с асинхронным опросом
    await app.run_polling()

def get_stats(user_id):
    conn = sqlite3.connect("health_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, value, date FROM logs WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Установка команд
async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Начать или зарегистрироваться"),
        BotCommand("log", "Добавить запись (например, вес, вода)"),
        BotCommand("edit", "Редактировать запись"),
        BotCommand("delete", "Удалить запись"),
        BotCommand("stats", "Посмотреть статистику"),
        BotCommand("help", "Список доступных команд")
    ]
    # Устанавливаем команды для всех пользователей
    await application.bot.set_my_commands(commands)

# Обработчик нажатия кнопки
# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data  # Получаем callback_data кнопки

    if data == 'start':
        await query.edit_message_text("Ты нажал на кнопку /start")
    elif data == 'log':
        await query.edit_message_text("Ты нажал на кнопку /log - Добавление записи")
    elif data == 'edit':
        await query.edit_message_text("Ты нажал на кнопку /edit - Редактирование записи")
    elif data == 'delete':
        await query.edit_message_text("Ты нажал на кнопку /delete - Удаление записи")
    elif data == 'stats':
        stats = get_stats(update.effective_user.id)
        if stats:
            message = "Ваша статистика:\n"
            for category, value, date in stats:
                message += f"{category} ({date}): {value}\n"
            await query.edit_message_text(message)
        else:
            await query.edit_message_text("Ваша статистика пуста. Запишите данные с помощью команды /log.")
    elif data == 'help':
        await query.edit_message_text("Список команд:\n/start - Начать\n/log - Добавить запись\n/edit - Редактировать запись\n/delete - Удалить запись\n/stats - Показать статистику")

# Обновленная функция /start с кнопками
# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    # Проверка на количество аргументов
    if len(context.args) == 0:
        welcome_message = """
        Привет! Я твой личный тренер. Я помогу тебе отслеживать:
        - Вес
        - Количество выпитой воды
        - Активность
        - Настроение

        Начни с добавления данных через команду /log
        """
    else:
        # Если в аргументах есть данные (например, команда с параметрами), можно сделать что-то другое
        welcome_message = "Вы передали аргументы: " + " ".join(context.args)

    await update.message.reply_text(welcome_message)

# Функция для создания кнопок
def create_buttons():
    buttons = [
        [InlineKeyboardButton("Начать /start", callback_data='start')],
        [InlineKeyboardButton("Добавить запись /log", callback_data='log')],
        [InlineKeyboardButton("Редактировать запись /edit", callback_data='edit')],
        [InlineKeyboardButton("Удалить запись /delete", callback_data='delete')],
        [InlineKeyboardButton("Статистика /stats", callback_data='stats')],
        [InlineKeyboardButton("Помощь /help", callback_data='help')]
    ]
    return InlineKeyboardMarkup(buttons)

# Функция для отправки статистики с кнопками
async def show_stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = sqlite3.connect("health_bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT category, value, date FROM logs WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()

    if rows:
        stats = "📊 **Ваша статистика**:\n"
        categories = {"вес": [], "вода": [], "активность": [], "настроение": []}

        for row in rows:
            category, value, date = row
            value = escape_markdown_v2(value)
            stats += f"🔹 **{escape_markdown_v2(category.capitalize())}**:\n🗓️ *{escape_markdown_v2(date)}*: `{value}`\n"

        # Отправляем сообщение с текстом и кнопками
        await update.message.reply_text(stats, parse_mode='MarkdownV2', reply_markup=create_buttons())
    else:
        await update.message.reply_text("📉 Ваша статистика пуста. Начните записывать данные с помощью команды /log.",
                                        reply_markup=create_buttons())
    conn.close()

# Функция для обработки команды /help
async def show_help(update: Update, context: CallbackContext):
    help_text = """
    Привет! Вот список доступных команд:

    /start - Начать или зарегистрироваться в боте.
    /log - Добавить запись о вашем весе, воде, активности, настроении и т.д.
    /edit - Редактировать уже добавленную запись.
    /delete - Удалить запись.
    /stats - Посмотреть вашу статистику (вес, вода, активность, настроение).
    /help - Список доступных команд.

    Вы можете записывать свой вес, сколько воды выпили, активность и настроение каждый день. Бот поможет отслеживать прогресс.
    """
    # Отправляем сообщение с текстом и кнопками
    await update.message.reply_text(help_text, reply_markup=create_buttons())

# Команда /edit
async def edit_data(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text(
            "Ошибка: используйте формат команды /edit категория новое_значение. Пример:\n/edit вес 75")
        return

    category = context.args[0]
    new_value = " ".join(context.args[1:])

    valid_categories = ["вес", "вода", "активность", "настроение"]
    if category not in valid_categories:
        await update.message.reply_text(f"Неправильная категория. Допустимые категории: {', '.join(valid_categories)}.")
        return

    conn = sqlite3.connect("health_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE logs SET value = ? WHERE user_id = ? AND category = ?", (new_value, user_id, category))
    conn.commit()

    if cursor.rowcount > 0:
        await update.message.reply_text(f"Запись обновлена: {category} - {new_value}")
    else:
        await update.message.reply_text(f"Запись для категории {category} не найдена.")

    conn.close()

# Команда /delete
async def delete_data(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if len(context.args) < 1:
        await update.message.reply_text("Ошибка: используйте формат команды /delete категория. Пример:\n/delete вес")
        return

    category = context.args[0]

    valid_categories = ["вес", "вода", "активность", "настроение"]
    if category not in valid_categories:
        await update.message.reply_text(f"Неправильная категория. Допустимые категории: {', '.join(valid_categories)}.")
        return

    conn = sqlite3.connect("health_bot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs WHERE user_id = ? AND category = ?", (user_id, category))
    conn.commit()

    if cursor.rowcount > 0:
        await update.message.reply_text(f"Запись для категории '{category}' удалена.")
    else:
        await update.message.reply_text(f"Запись для категории '{category}' не найдена.")

    conn.close()

# Обработчик команды /log
# Обработчик команды /log
async def log(update: Update, context: CallbackContext):
    # Проверяем, были ли переданы аргументы
    if len(context.args) < 2:
        await update.message.reply_text("Используйте команду в формате: /log категория значение")
        return

    category = context.args[0]
    value = " ".join(context.args[1:])
    user_id = update.effective_user.id

    log_data(user_id, category, value)  # Сохраняем данные в базе
    await update.message.reply_text(f"Данные записаны: {category} - {value}")

# Обработчик команды /log
async def log_data(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # Проверка на наличие аргументов
    if len(context.args) < 2:
        await update.message.reply_text(
            "Ошибка: используйте формат команды /log категория значение. Пример:\n"
            "/log вес 70\n"
            "или\n"
            "/log вода 2"
        )
        return

    # Получаем категорию и значение
    category = context.args[0]
    value = " ".join(context.args[1:])

    # Проверка, что категория допустимая
    valid_categories = ["вес", "вода", "активность", "настроение"]
    if category not in valid_categories:
        await update.message.reply_text(f"Неправильная категория. Допустимые категории: {', '.join(valid_categories)}.")
        return

    # Сохранение в базе данных
    conn = sqlite3.connect("health_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (user_id, category, value) VALUES (?, ?, ?)", (user_id, category, value))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Запись добавлена: {category} - {value}")

# Функция для инициализации базы данных
def init_db():
    conn = sqlite3.connect("health_bot.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        user_id INTEGER,
        category TEXT,
        value TEXT,
        date TEXT DEFAULT (datetime('now','localtime'))
    )
    ''')
    conn.commit()
    conn.close()

# Инициализация базы данных
conn = sqlite3.connect("health_bot.db")
cursor = conn.cursor()

# Удаляем старую таблицу, если она существует
cursor.execute("DROP TABLE IF EXISTS logs")

# Создаем таблицу заново с нужной схемой
cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    user_id INTEGER,
    category TEXT,
    value TEXT,
    date TEXT DEFAULT (datetime('now','localtime'))
)
''')

conn.commit()
conn.close()

# Функция для экранирования символов MarkdownV2
def escape_markdown_v2(text):
    return re.sub(r'([_*[\]()>#+-.!|])', r'\\\1', text)

if __name__ == "__main__":
    print('Бот запустился!')
    init_db()  # Инициализация базы данных
    app = ApplicationBuilder().token("7280297934:AAHspvKvMh7PJn4sTszwu43v4SzQWTZY7Rk").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("log", log_data))
    app.add_handler(CommandHandler("edit", edit_data))
    app.add_handler(CommandHandler("delete", delete_data))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("help", show_help))

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("log", log))
    app.add_handler(CallbackQueryHandler(button_handler))  # Обработчик кнопок

    # Запуск приложения с асинхронным опросом
    app.run_polling()
