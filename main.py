import logging
import os
import sys
from datetime import datetime
import signal
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, UPDATE_INTERVAL, RATE_MESSAGE_TEMPLATE

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем клавиатуру с одной кнопкой
KEYBOARD = ReplyKeyboardMarkup([['💶 Курс евро']], resize_keyboard=True)

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
            logger.info(f"Запрашиваю курс евро с {self.url}...")
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
                    
                    logger.info(f"Успешно получены курсы: покупка {buy_rate}, продажа {sell_rate}")
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
    await update.message.reply_text(
        'Привет! Я бот для отслеживания курса евро. Нажмите на кнопку "💶 Курс евро" для получения текущего курса.',
        reply_markup=KEYBOARD
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    if update.message.text == '💶 Курс евро':
        await get_rate(update, context)

async def get_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение и отправка текущего курса"""
    rates = parser.get_rate()
    if rates and len(rates) == 3:
        buy_rate, sell_rate, _ = rates  # Игнорируем флаг изменения для ручного запроса
        current_time = datetime.now().strftime("%H:%M:%S")
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

async def send_rate_update(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка и отправка обновления курса"""
    rates = parser.get_rate()
    if rates and len(rates) == 3:
        buy_rate, sell_rate, rate_changed = rates
        if rate_changed:  # Отправляем сообщение только если курс изменился
            current_time = datetime.now().strftime("%H:%M:%S")
            message = f"❗️ Обнаружено изменение курса!\n\n" + RATE_MESSAGE_TEMPLATE.format(
                buy_rate=buy_rate,
                sell_rate=sell_rate,
                time=current_time
            )
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message
            )

def main() -> None:
    # Проверяем наличие токена
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Не задан токен бота в переменных окружения!")
        sys.exit(1)
        
    if not TELEGRAM_CHAT_ID:
        logger.error("Не задан ID чата в переменных окружения!")
        sys.exit(1)

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", get_rate))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Добавляем задачу на регулярное обновление курса
    job_queue = application.job_queue
    job_queue.run_repeating(send_rate_update, interval=UPDATE_INTERVAL, first=1)

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 