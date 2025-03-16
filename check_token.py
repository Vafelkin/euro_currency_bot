import requests
import os
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')

print(f"Проверяем токен: {token}")

# Делаем запрос к API Telegram
url = f"https://api.telegram.org/bot{token}/getMe"
try:
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and data.get('ok'):
        bot_info = data['result']
        print("\n✅ Токен валидный!")
        print(f"Имя бота: {bot_info['first_name']}")
        print(f"Username: @{bot_info['username']}")
        print(f"ID бота: {bot_info['id']}")
    else:
        print("\n❌ Токен невалидный!")
        print(f"Ошибка: {data.get('description', 'Неизвестная ошибка')}")
except Exception as e:
    print("\n❌ Ошибка при проверке токена:")
    print(f"Исключение: {str(e)}") 