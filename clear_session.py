import requests
from config import TELEGRAM_BOT_TOKEN

def clear_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=True"
    response = requests.get(url)
    print(f"Статус очистки вебхука: {response.status_code}")
    print(f"Ответ: {response.json()}")

if __name__ == "__main__":
    clear_webhook() 