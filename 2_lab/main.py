from telethon import TelegramClient, sync
import asyncio
import re
import spacy
import multiprocessing as mp
from collections import Counter
import json

# Задайте ваши параметры API
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'

# Инициализация Spacy для обработки текста
nlp = spacy.load("ru_core_news_sm")
stopwords = nlp.Defaults.stop_words

# Функция для подключения к Telegram и получения данных с канала
async def fetch_telegram_data(client, channel_name):
    try:
        messages = []
        async for message in client.iter_messages(channel_name, limit=1000):  # Задайте лимит сообщений
            if message.text:
                messages.append(message.text)
        return messages
    except Exception as e:
        print(f"Ошибка при получении данных с {channel_name}: {e}")
        return []

# Функция для предварительной обработки текста
def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    doc = nlp(text)
    return " ".join([token.text for token in doc if token.text.lower() not in stopwords])

# Параллельная обработка текста
def preprocess_in_parallel(text_list):
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(preprocess_text, text_list)
    return results

# Функция для извлечения хэштегов
def extract_hashtags(text):
    return re.findall(r"#\w+", text)

# Анализ популярных хэштегов
def analyze_hashtags(preprocessed_data):
    hashtags = []
    for text in preprocessed_data:
        hashtags.extend(extract_hashtags(text))
    popular_hashtags = Counter(hashtags).most_common(10)
    return popular_hashtags

# Основная функция для работы с Telegram
async def main():
    # Telegram клиент
    client = TelegramClient('anon', api_id, api_hash)
    
    await client.start()
    print("Клиент Telegram запущен")
    
    # Каналы для сбора данных (например, новости или трендовые каналы)
    telegram_channels = ['telegram_channel_1', 'telegram_channel_2']  # Укажите каналы

    # Сбор данных с нескольких каналов
    raw_data = []
    for channel in telegram_channels:
        print(f"Сбор данных с канала {channel}")
        messages = await fetch_telegram_data(client, channel)
        raw_data.extend(messages)

    # Параллельная предварительная обработка данных
    print("Предварительная обработка данных...")
    preprocessed_data = preprocess_in_parallel(raw_data)

    # Анализ данных на предмет хэштегов
    print("Анализ данных...")
    popular_hashtags = analyze_hashtags(preprocessed_data)

    # Сохранение результатов в файл
    print("Сохранение результатов...")
    with open('telegram_results.json', 'w') as f:
        json.dump(popular_hashtags, f)

    print("Анализ завершен. Результаты сохранены в telegram_results.json")
    await client.disconnect()

# Запуск основной функции
if __name__ == "__main__":
    asyncio.run(main())
