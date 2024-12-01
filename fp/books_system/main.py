import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# Путь к файлу JSON
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


def update_table(recommendations):
    for row in table.get_children():
        table.delete(row)
    for book in recommendations:
        table.insert('', 'end', values=(book['title'], ", ".join(book['author']), book['genre'], book['first_publish_year'], book['score']))


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
    update_table(current_recommendations)


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


books = load_books(BOOKS_DB_PATH)
all_genres, all_authors = extract_unique_fields(books)
current_recommendations = []


root = tk.Tk()
root.title("Рекомендательная система для книг")
root.geometry("2560x1440")


tk.Label(root, text="Выберите авторов (через запятую):").pack(pady=5)
author_combobox = ttk.Combobox(root, values=all_authors, width=50)
author_combobox.pack()
author_combobox.bind('<KeyRelease>', lambda e: update_autocomplete(e, author_combobox, all_authors))

tk.Label(root, text="Ключевые слова (через запятую):").pack(pady=5)
keywords_entry = tk.Entry(root, width=50)
keywords_entry.pack()

tk.Label(root, text="Укажите минимальный год публикации:").pack(pady=5)
year_entry = tk.Entry(root, width=20)
year_entry.pack()

tk.Label(root, text="Укажите минимальный рейтинг:").pack(pady=5)
score_entry = tk.Entry(root, width=20)
score_entry.pack()

tk.Label(root, text="Выберите жанры:").pack(pady=5)
genre_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=10)
for genre in all_genres:
    genre_listbox.insert(tk.END, genre)
genre_listbox.pack()

tk.Button(root, text="Сгенерировать рекомендации", command=generate_recommendations).pack(pady=10)
tk.Button(root, text="Сохранить рекомендации", command=save_recommendations).pack(pady=5)

table = ttk.Treeview(root, columns=("Название", "Авторы", "Жанр", "Год", "Рейтинг"), show='headings', height=20)
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

root.mainloop()
