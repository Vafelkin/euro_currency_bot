import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Интервал обновления курса в секундах (1 час = 3600 секунд)
UPDATE_INTERVAL = 600

# Шаблон сообщения для отправки курса
RATE_MESSAGE_TEMPLATE = """
💶 Курс евро:

Покупка: {buy_rate} ₽
Продажа: {sell_rate} ₽

🕒 Обновлено: {time}
"""

# URL для парсинга
LIGOVKA_URL = "https://ligovka.ru/"

# Формат сообщения с курсом
MESSAGE_TEMPLATE = """
💶 <b>Курс евро (Лиговка)</b>

💰 Покупка: {buy_rate} ₽
💸 Продажа: {sell_rate} ₽
⏰ Обновлено: {update_time}
""" 