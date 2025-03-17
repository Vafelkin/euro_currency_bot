# Euro Currency Bot 🤖

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![Updates](https://img.shields.io/badge/updates-10%20min-brightgreen.svg)]()

Telegram бот для отслеживания курса евро в обменном пункте на Лиговском проспекте. Бот публичный - любой пользователь может начать с ним взаимодействовать, просто найдя его в Telegram.

## Возможности

- 🔄 Автоматическое обновление курса каждые 10 минут
- 📊 Мгновенные уведомления при изменении курса
- 💰 Информация о курсах покупки и продажи с сайта Лиговки
- 🔐 Безопасное хранение данных в .env файле
- 📈 Отслеживание изменений курса с точностью до копейки
- 🤖 Автоматическое определение пользователей
- 🔄 Автоматический перезапуск при сбоях

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
UPDATE_INTERVAL=600
```

## Использование

### Локальный запуск
1. Запустите бота:
```bash
python main.py
```

### Запуск как systemd сервис (для Linux)
Systemd сервис рекомендуется для использования на серверах, так как он обеспечивает:
- Автоматический запуск бота при перезагрузке сервера
- Автоматический перезапуск при сбоях
- Корректное логирование
- Управление процессом через стандартные команды systemd

1. Создайте файл сервиса:
```bash
sudo nano /etc/systemd/system/euro-currency-bot.service
```

2. Добавьте следующее содержимое:
```ini
[Unit]
Description=Euro Currency Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/euro_currency_bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Активируйте и запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable euro-currency-bot
sudo systemctl start euro-currency-bot
```

4. Проверьте статус:
```bash
sudo systemctl status euro-currency-bot
```

## Команды в Telegram

- `/start` - Начать работу с ботом
- Кнопка "💶 Курс евро" - Получить текущий курс

## Формат уведомлений

Бот отправляет уведомления в следующий чат, где он был активирован, в следующем формате:
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
- `UPDATE_INTERVAL` - интервал обновления курса в секундах (по умолчанию 600 секунд = 10 минут)

## Требования

- Python 3.7+
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

## Лицензия

MIT License 