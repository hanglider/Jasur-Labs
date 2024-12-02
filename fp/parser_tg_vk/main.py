import multiprocessing as mp
import re
import asyncio
from tkinter import Tk, Listbox, Button, MULTIPLE, END, Scrollbar, Label, messagebox, Text, Toplevel, Entry
from nltk.corpus import stopwords
from collections import Counter
import vk_api
from telethon import TelegramClient
import concurrent.futures
from pprint import pprint
from config import API_ID, API_HASH, access_token

additional_stopwords = {'на', 'не', 'в', 'и', 'c'}  # Дополнительные стоп-слова

# Получение числового group_id по alias (короткому имени) для ВК
def get_group_id(alias, token):
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        group_info = vk.groups.getById(group_id=alias)
        return group_info[0]['id']
    except vk_api.VkApiError as error:
        print(f"Ошибка при запросе к VK API: {error}")
        return None

# Получение постов из ВКонтакте
def get_vk_posts(group_id, token, count=100):
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        if group_id > 0:
            group_id = -group_id
        response = vk.wall.get(owner_id=group_id, count=count)
        posts = [post['text'] for post in response['items'] if 'text' in post and post['text'].strip()]
        return posts
    except vk_api.VkApiError as error:
        print(f"Ошибка при запросе к VK API: {error}")
        return None

# Сбор данных из ВКонтакте, добавление в общий файл
def collect_vk_data(source_name, group_id, token, count):
    """Собирает текст постов ВКонтакте для дальнейшего анализа"""
    data = get_vk_posts(group_id, token, count)
    if data:
        all_text = ' '.join(data)  # Объединяем все посты в один текст
        print(f"Данные собраны с {source_name}")
        return all_text
    else:
        print(f"Не удалось собрать данные с {source_name}")
        return None

# Предобработка текста
def preprocess_text(data):
    stop_words = set(stopwords.words('russian')).union(additional_stopwords)
    cleaned_data = re.sub(r'\W+', ' ', data.lower())  # Убираем спецсимволы
    words = [word for word in cleaned_data.split() if word not in stop_words and len(word) > 2]
    return words

# Анализ данных и запись результатов
def analyze_data(source_name, all_text, output_file):
    """Анализирует данные и сохраняет топ-10 слов в файл"""
    words = preprocess_text(all_text)
    word_counts = Counter(words)
    common_words = word_counts.most_common(10)
    
    # Записываем топ-10 слов в файл
    with open(output_file, "a", encoding='utf-8') as f:
        f.write(f"### Топ-10 слов для {source_name} ###\n")
        for word, count in common_words:
            f.write(f"{word}: {count}\n")
    print(f"Топ-10 слов для {source_name}: {common_words}")

# Парсинг ВК
def vk_parser(selected_groups, count):
    group_ids = {alias: get_group_id(alias=alias, token=access_token) for alias in selected_groups}
    group_ids = {name: id for name, id in group_ids.items() if id is not None}
    
    output_file = "all_vk_data.txt"
    # Очищаем файл перед началом новой записи
    with open(output_file, "w", encoding='utf-8') as f:
        f.write("")

    pool = mp.Pool(len(group_ids))
    vk_data_tasks = [(f"VK_{name}", group_id, access_token, count) for name, group_id in group_ids.items()]
    
    # Собираем данные с групп ВК и анализируем их
    for source_name, group_id, token, count in vk_data_tasks:
        all_text = collect_vk_data(source_name, group_id, token, count)
        if all_text:
            analyze_data(source_name, all_text, output_file)

# Сохранение результатов в файл
def save_results_to_file(counter: Counter, file_name: str):
    with open(file_name, 'w', encoding='utf-8') as f:
        for word, freq in counter.most_common(100):
            f.write(f'{word}: {freq}\n')

# Парсинг Telegram
async def telegram_parser(selected_channels, count):
    all_messages_counter = Counter()
    all_hashtags_counter = Counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(lambda name=name: request_messages(name, count)): name for name in selected_channels}
        for future in concurrent.futures.as_completed(futures):
            try:
                messages_counter, hashtags_counter = await future.result()
                all_messages_counter += messages_counter
                all_hashtags_counter += hashtags_counter
            except Exception:
                exit(1)
    pprint(all_messages_counter.most_common(100))
    pprint(all_hashtags_counter.most_common(100))
    save_results_to_file(all_messages_counter, 'counter_words.txt')

# Асинхронный запрос сообщений в Telegram
async def request_messages(channel_name, count):
    async with TelegramClient('anon', API_ID, API_HASH) as client:
        channel = await client.get_entity(channel_name)
        messages = await client.get_messages(channel, limit=count)
        counter = Counter()
        for message in messages:
            if message.text:
                counter += Counter(re.sub(r'[^\w\s#]', '', message.text).split())
        counter_hashtags = Counter({k: v for k, v in counter.items() if k.startswith('#')})
        return counter, counter_hashtags

# Функция для обработки кнопки парсинга
def parse_data(vk_input, telegram_input, count):
    selected_vk_groups = vk_input.split()  # Преобразуем введённые группы в список
    selected_telegram_channels = telegram_input.split()  # Преобразуем введённые каналы в список
    
    if selected_vk_groups:  # Проверка, есть ли выбранные группы ВК
        vk_parser(selected_vk_groups, count)
        
    if selected_telegram_channels:  # Проверка, есть ли выбранные каналы Telegram
        asyncio.run(telegram_parser(selected_telegram_channels, count))

    messagebox.showinfo("Парсинг завершен", "Данные успешно собраны!")

# Функция для отображения содержимого файлов
def show_file_content(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            # Создаем новое окно для отображения содержимого файла
            window = Toplevel()
            window.title(f"Содержимое {file_name}")
            text_area = Text(window, wrap='word', width=80, height=20)
            text_area.pack(expand=True, fill='both')
            text_area.insert(END, data)
            scrollbar = Scrollbar(window)
            scrollbar.pack(side='right', fill='y')
            text_area.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_area.yview)
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {file_name} не найден.")

# Создание GUI с помощью Tkinter
def create_gui():
    root = Tk()
    root.title("Парсинг VK и Telegram")

    # Метка и поле для ввода групп VK
    Label(root, text="Введите группы ВКонтакте для парсинга (через пробел):").pack()
    vk_entry = Entry(root, width=50)
    vk_entry.pack()

    # Метка и поле для ввода каналов Telegram
    Label(root, text="Введите каналы Telegram для парсинга (через пробел):").pack()
    telegram_entry = Entry(root, width=50)
    telegram_entry.pack()

    # Метка и поле для ввода количества сообщений/постов для скачивания
    Label(root, text="Введите количество сообщений/постов для скачивания:").pack()
    count_entry = Entry(root)
    count_entry.insert(END, '100')  # Значение по умолчанию
    count_entry.pack()

    # Кнопка для запуска парсинга
    parse_button = Button(root, text="Запустить парсинг", command=lambda: parse_data(
        vk_entry.get(),  # Получаем введённые данные для VK
        telegram_entry.get(),  # Получаем введённые данные для Telegram
        int(count_entry.get())
    ))
    parse_button.pack()

    # Кнопка для отображения содержимого файлов
    view_vk_button = Button(root, text="Показать данные VK", command=lambda: show_file_content("all_vk_data.txt"))
    view_vk_button.pack()

    view_telegram_button = Button(root, text="Показать данные Telegram", command=lambda: show_file_content("counter_words.txt"))
    view_telegram_button.pack()

    root.mainloop()

if __name__ == '__main__':
    create_gui()
