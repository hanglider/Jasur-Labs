import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

BOOKS_DB_PATH = 'C:/IT/Jasur-Labs/fp/books_system/books.json'

def load_books(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить базу данных: {e}")
        return []

def extract_unique_fields(books):
    genres = set()
    authors = set()
    for book in books:
        genres.add(book.get("genre", "").strip())
        for author in book.get("author", []):
            authors.add(author.strip())
    return sorted(genres), sorted(authors)

def update_autocomplete(event, combobox, values):
    entry = event.widget.get()
    combobox['values'] = [value for value in values if entry.lower() in value.lower()]
    combobox.event_generate('<Down>')

def recommend_books(preferences, books):
    def calculate_score(book):
        score = 0
        if book['genre'] in preferences['genres']:
            score += 3
        if any(author in preferences['authors'] for author in book['author']):
            score += 5
        if any(keyword.lower() in book['description'].lower() for keyword in preferences['keywords']):
            score += 2
        return score

    recommendations = [
        {**book, 'score': calculate_score(book)}
        for book in books
        if book['first_publish_year'] >= preferences['min_year'] and calculate_score(book) >= preferences['min_score']
    ]
    return sorted(recommendations, key=lambda x: x['score'], reverse=True)

def update_table(recommendations, sort_criteria):
    for row in table.get_children():
        table.delete(row)

    if sort_criteria == "Название (по возрастанию)":
        recommendations = sorted(recommendations, key=lambda x: x['title'])
    elif sort_criteria == "Название (по убыванию)":
        recommendations = sorted(recommendations, key=lambda x: x['title'], reverse=True)
    elif sort_criteria == "Год (по возрастанию)":
        recommendations = sorted(recommendations, key=lambda x: x['first_publish_year'])
    elif sort_criteria == "Год (по убыванию)":
        recommendations = sorted(recommendations, key=lambda x: x['first_publish_year'], reverse=True)
    elif sort_criteria == "Рейтинг (по возрастанию)":
        recommendations = sorted(recommendations, key=lambda x: x['score'])
    elif sort_criteria == "Рейтинг (по убыванию)":
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)

    for book in recommendations:
        table.insert('', 'end', values=(book['title'], ", ".join(book['author']), book['genre'], book['first_publish_year'], book['score']))

def save_recommendations():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("Название,Авторы,Жанр,Год,Рейтинг\n")
            for row_id in table.get_children():
                row = table.item(row_id)['values']
                file.write(",".join(map(str, row)) + "\n")
        messagebox.showinfo("Успех", "Рекомендации успешно сохранены!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def add_to_favorites(book):
    favorites_table.insert('', 'end', values=(book['title'], ", ".join(book['author']), book['genre'], book['first_publish_year'], book['score']))

books = load_books(BOOKS_DB_PATH)
all_genres, all_authors = extract_unique_fields(books)
current_recommendations = []

root = tk.Tk()
root.title("Рекомендательная система для книг")
root.geometry("2560x1440")

frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(frame_left, text="Выберите автора:").pack(pady=5)
author_combobox = ttk.Combobox(frame_left, values=all_authors, width=50)
author_combobox.pack()
author_combobox.bind('<KeyRelease>', lambda e: update_autocomplete(e, author_combobox, all_authors))

tk.Label(frame_left, text="Ключевые слова:").pack(pady=5)
keywords_entry = tk.Entry(frame_left, width=50)
keywords_entry.pack()

tk.Label(frame_left, text="Укажите минимальный год публикации:").pack(pady=5)
year_entry = tk.Entry(frame_left, width=20)
year_entry.pack()

tk.Label(frame_left, text="Укажите минимальный рейтинг:").pack(pady=5)
score_entry = tk.Entry(frame_left, width=20)
score_entry.pack()

tk.Label(frame_left, text="Выберите жанры:").pack(pady=5)
genre_listbox = tk.Listbox(frame_left, selectmode=tk.MULTIPLE, height=10)
for genre in all_genres:
    genre_listbox.insert(tk.END, genre)
genre_listbox.pack()

tk.Label(frame_left, text="Сортировать по:").pack(pady=5)
sort_combobox = ttk.Combobox(frame_left, values=[
    "Название (по возрастанию)", "Название (по убыванию)",
    "Год (по возрастанию)", "Год (по убыванию)",
    "Рейтинг (по возрастанию)", "Рейтинг (по убыванию)"
], width=30)
sort_combobox.pack()
sort_combobox.current(0)

button_frame = tk.Frame(frame_left)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Сгенерировать рекомендации", command=lambda: generate_recommendations()).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Сохранить рекомендации", command=save_recommendations).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Добавить в избранное", command=lambda: add_to_favorites_from_table()).pack(side=tk.LEFT, padx=5)

table = ttk.Treeview(frame_left, columns=("Название", "Авторы", "Жанр", "Год", "Рейтинг"), show='headings', height=20)
table.heading("Название", text="Название")
table.heading("Авторы", text="Авторы")
table.heading("Жанр", text="Жанр")
table.heading("Год", text="Год")
table.heading("Рейтинг", text="Рейтинг")
table.column("Название", width=300)
table.column("Авторы", width=200)
table.column("Жанр", width=100)
table.column("Год", width=70)
table.column("Рейтинг", width=80)
table.pack(pady=10, fill=tk.BOTH, expand=True)

frame_right = tk.Frame(root)
frame_right.pack(side=tk.LEFT, padx=10, pady=10)

favorites_label = tk.Label(frame_right, text="Избранное")
favorites_label.pack(pady=10)

favorites_table = ttk.Treeview(frame_right, columns=("Название", "Авторы", "Жанр", "Год", "Рейтинг"), show='headings', height=20)
favorites_table.heading("Название", text="Название")
favorites_table.heading("Авторы", text="Авторы")
favorites_table.heading("Жанр", text="Жанр")
favorites_table.heading("Год", text="Год")
favorites_table.heading("Рейтинг", text="Рейтинг")
favorites_table.column("Название", width=300)
favorites_table.column("Авторы", width=200)
favorites_table.column("Жанр", width=100)
favorites_table.column("Год", width=70)
favorites_table.column("Рейтинг", width=80)
favorites_table.pack(pady=10, fill=tk.BOTH, expand=True)

def generate_recommendations():
    global current_recommendations

    selected_genres = [genre_listbox.get(idx) for idx in genre_listbox.curselection()]
    preferences = {
        'min_year': int(year_entry.get()) if year_entry.get().isdigit() else 0,
        'min_score': int(score_entry.get()) if score_entry.get().isdigit() else 0,
        'genres': selected_genres,
        'authors': [author.strip() for author in author_combobox.get().split(',')],
        'keywords': [keyword.strip() for keyword in keywords_entry.get().split(',')]
    }
    current_recommendations = recommend_books(preferences, books)
    update_table(current_recommendations, sort_combobox.get())

def add_to_favorites_from_table():
    for row_id in table.selection():
        row = table.item(row_id)['values']
        book = {
            'title': row[0],
            'author': row[1].split(", "),
            'genre': row[2],
            'first_publish_year': row[3],
            'score': row[4]
        }
        add_to_favorites(book)

root.mainloop()
