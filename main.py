import logging
import os
import sys
from datetime import datetime
import signal
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, UPDATE_INTERVAL, RATE_MESSAGE_TEMPLATE
from pytz import timezone

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Изменено на DEBUG для более подробного логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем клавиатуру с одной кнопкой
KEYBOARD = ReplyKeyboardMarkup([['💶 Курс евро']], resize_keyboard=True)

# Глобальный список для хранения chat_id пользователей
active_users = set()

class EuroRateParser:
    def __init__(self):
        self.url = "https://ligovka.ru/detailed/eur"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.last_buy_rate = None
        self.last_sell_rate = None

    def get_rate(self) -> tuple[float, float, bool] | tuple[None, None, bool]:
        """
        Получает текущий курс и определяет, изменился ли он
        Возвращает (курс покупки, курс продажи, флаг изменения)
        """
        try:
            logger.debug(f"Запрашиваю курс евро с {self.url}...")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем строку с "от 1" в таблице курсов
            row = soup.find('td', class_='money_quantity', string='от 1')
            if row and row.parent:
                # Находим ячейки с курсами в этой же строке
                buy_cell = row.parent.find('td', class_='money_price buy_price')
                sell_cell = buy_cell.find_next('td', class_='money_price') if buy_cell else None
                
                if buy_cell and sell_cell:
                    buy_rate = float(buy_cell.text.strip())
                    sell_rate = float(sell_cell.text.strip())
                    
                    # Проверяем, изменился ли курс
                    rate_changed = (
                        self.last_buy_rate is not None and
                        self.last_sell_rate is not None and
                        (abs(buy_rate - self.last_buy_rate) >= 0.01 or
                         abs(sell_rate - self.last_sell_rate) >= 0.01)
                    )
                    
                    # Обновляем последние известные курсы
                    self.last_buy_rate = buy_rate
                    self.last_sell_rate = sell_rate
                    
                    logger.debug(f"Успешно получены курсы: покупка {buy_rate}, продажа {sell_rate}")
                    if rate_changed:
                        logger.info("Обнаружено изменение курса!")
                    return buy_rate, sell_rate, rate_changed
            
            logger.error("Не удалось найти курсы EUR для суммы 'от 1'")
            return None, None, False
            
        except Exception as e:
            logger.error(f"Ошибка при получении курса евро: {e}")
            return None, None, False

parser = EuroRateParser()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
        logger.debug(f"Получена команда /start от пользователя {update.effective_user.id}")
        chat_id = update.effective_chat.id
        if chat_id not in active_users:
            active_users.add(chat_id)
            logger.info(f"Новый пользователь добавлен: {chat_id}")
        await update.message.reply_text(
            "Привет! Я бот для отслеживания курса евро. Я буду отправлять вам уведомления при изменении курса.",
            reply_markup=KEYBOARD
        )
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    try:
        logger.debug(f"Получено сообщение: {update.message.text} от пользователя {update.effective_user.id}")
        chat_id = update.effective_chat.id
        if chat_id not in active_users:
            active_users.add(chat_id)
            logger.info(f"Новый пользователь добавлен: {chat_id}")
            
        if update.message.text == '💶 Курс евро':
            await get_rate(update, context)
    except Exception as e:
        logger.error(f"Ошибка в обработчике сообщений: {e}")

async def get_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение и отправка текущего курса"""
    try:
        logger.debug(f"Запрос курса от пользователя {update.effective_user.id}")
        rates = parser.get_rate()
        if rates and len(rates) == 3:
            buy_rate, sell_rate, _ = rates  # Игнорируем флаг изменения для ручного запроса
            current_time = datetime.now(timezone('Europe/Moscow')).strftime("%H:%M:%S")
            await update.message.reply_text(
                RATE_MESSAGE_TEMPLATE.format(
                    buy_rate=buy_rate,
                    sell_rate=sell_rate,
                    time=current_time
                ),
                reply_markup=KEYBOARD
            )
        else:
            await update.message.reply_text(
                "Извините, не удалось получить текущий курс евро.",
                reply_markup=KEYBOARD
            )
    except Exception as e:
        logger.error(f"Ошибка в обработчике get_rate: {e}")

async def send_rate_update(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка и отправка обновления курса"""
    try:
        rates = parser.get_rate()
        if rates and len(rates) == 3:
            buy_rate, sell_rate, rate_changed = rates
            if rate_changed:  # Отправляем сообщение только если курс изменился
                current_time = datetime.now(timezone('Europe/Moscow')).strftime("%H:%M:%S")
                message = f"❗️ Обнаружено изменение курса!\n\n" + RATE_MESSAGE_TEMPLATE.format(
                    buy_rate=buy_rate,
                    sell_rate=sell_rate,
                    time=current_time
                )
                # Создаем копию списка пользователей, так как он может измениться во время итерации
                users_to_notify = list(active_users)
                for chat_id in users_to_notify:
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=message
                        )
                    except Exception as e:
                        logger.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")
                        # Удаляем пользователя из списка, если не удалось отправить сообщение
                        if chat_id in active_users:
                            active_users.remove(chat_id)
                            logger.info(f"Пользователь удален из списка: {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике send_rate_update: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Произошла ошибка: {context.error}")

def main() -> None:
    try:
        # Проверяем наличие токена
        if not TELEGRAM_BOT_TOKEN:
            logger.error("Не задан токен бота в переменных окружения!")
            sys.exit(1)
            
        logger.info("Запуск бота...")
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Добавляем обработчики команд и сообщений
        logger.debug("Регистрация обработчиков...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("rate", get_rate))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)

        # Добавляем задачу на регулярное обновление курса
        job_queue = application.job_queue
        job_queue.run_repeating(send_rate_update, interval=UPDATE_INTERVAL, first=1)
        logger.debug("Задача обновления курса добавлена")

        # Запускаем бота
        logger.info("Бот запущен и готов к работе")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 