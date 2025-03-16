# Euro Currency Bot 🤖

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![Updates](https://img.shields.io/badge/updates-10%20min-brightgreen.svg)]()

Telegram бот для отслеживания курса евро в обменном пункте на Лиговском проспекте.

## Возможности

- 🔄 Автоматическое обновление курса каждые 10 минут
- 📊 Мгновенные уведомления при изменении курса
- 💰 Информация о курсах покупки и продажи
- 🔐 Безопасное хранение данных в .env файле
- 📈 Отслеживание изменений курса с точностью до копейки

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Vafelkin/euro_currency_bot.git
cd euro_currency_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте необходимые переменные:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
UPDATE_INTERVAL=600
```

## Использование

1. Запустите бота:
```bash
python main.py
```

2. В Telegram доступны следующие команды:
- `/start` - Начать работу с ботом
- Кнопка "💶 Курс евро" - Получить текущий курс

## Формат уведомлений

Бот отправляет уведомления в следующем формате:
```
💶 Курс евро:

Покупка: XX.XX ₽
Продажа: XX.XX ₽

🕒 Обновлено: HH:MM:SS
```

При изменении курса добавляется пометка:
```
❗️ Обнаружено изменение курса!
```

## Настройка

В файле `.env` можно настроить:
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `TELEGRAM_CHAT_ID` - ID чатов для отправки уведомлений (можно указать несколько через запятую)
- `UPDATE_INTERVAL` - интервал обновления курса в секундах (по умолчанию 600 секунд = 10 минут)

## Требования

- Python 3.7+
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

## Лицензия

MIT License 