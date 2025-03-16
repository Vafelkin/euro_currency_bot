import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rate():
    url = "https://ligovka.ru/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logger.info(f"Запрашиваю курс евро с {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Сохраняем HTML для анализа
        with open('response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info("HTML сохранен в файл response.html")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Выводим все таблицы на странице
        logger.info("\nВсе таблицы на странице:")
        for table in soup.find_all('table'):
            logger.info(f"Таблица с классами: {table.get('class', 'нет классов')}")
            
        # Выводим все td с классом money_price
        logger.info("\nВсе элементы с курсами:")
        for td in soup.find_all('td', class_='money_price'):
            logger.info(f"Найден курс: {td.text.strip()}, классы: {td.get('class')}")
            
        # Ищем конкретно строку с EUR
        logger.info("\nПоиск строки с EUR:")
        for tr in soup.find_all('tr'):
            if 'EUR' in tr.text:
                logger.info(f"Найдена строка с EUR: {tr.text.strip()}")
                for td in tr.find_all('td'):
                    logger.info(f"- Ячейка: {td.text.strip()}, классы: {td.get('class', 'нет классов')}")
        
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при получении курса евро: {e}")
        return None

if __name__ == "__main__":
    get_rate() 