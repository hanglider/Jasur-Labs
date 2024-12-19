import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import re

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")
        self.logs = None

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Кнопка для загрузки файла
        self.load_button = tk.Button(self.root, text="Load Log File", command=self.load_file)
        self.load_button.pack(pady=10)

        # Поля фильтрации
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="User:").grid(row=0, column=0, padx=5)
        self.user_filter = tk.Entry(filter_frame)
        self.user_filter.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Process:").grid(row=0, column=2, padx=5)
        self.process_filter = tk.Entry(filter_frame)
        self.process_filter.grid(row=0, column=3, padx=5)

        self.filter_button = tk.Button(filter_frame, text="Apply Filters", command=self.apply_filters)
        self.filter_button.grid(row=0, column=4, padx=10)

        # Таблица для отображения логов
        self.tree = ttk.Treeview(self.root, columns=("Timestamp", "Event Type", "User", "Process"), show="headings")
        self.tree.heading("Timestamp", text="Timestamp", command=lambda: self.sort_column("Timestamp"))
        self.tree.heading("Event Type", text="Event Type", command=lambda: self.sort_column("Event Type"))
        self.tree.heading("User", text="User", command=lambda: self.sort_column("User"))
        self.tree.heading("Process", text="Process", command=lambda: self.sort_column("Process"))
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Вертикальный скроллбар
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_file(self):
        # Открываем файл логов
        file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.txt")])
        if not file_path:
            return

        try:
            # Парсим файл логов
            self.logs = self.parse_logs(file_path)
            self.display_logs(self.logs)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load log file: {e}")

    def parse_logs(self, file_path):
        # Чтение файла и преобразование данных
        log_data = []
        with open(file_path, "r") as file:
            for line in file:
                match = re.match(r"(?P<timestamp>[\d\-T:.]+) \| (?P<event_type>\w+) \| User: (?P<user>\w+), Process: (?P<process>.+)", line)
                if match:
                    log_data.append(match.groupdict())
        return pd.DataFrame(log_data)

    def display_logs(self, logs):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Добавление данных в таблицу
        for _, row in logs.iterrows():
            self.tree.insert("", tk.END, values=row.tolist())

    def apply_filters(self):
        if self.logs is None:
            messagebox.showerror("Error", "No logs loaded!")
            return

        # Применяем фильтры
        filtered_logs = self.logs.copy()

        user_filter = self.user_filter.get()
        if user_filter:
            filtered_logs = filtered_logs[filtered_logs["user"].str.contains(user_filter, case=False)]

        process_filter = self.process_filter.get()
        if process_filter:
            filtered_logs = filtered_logs[filtered_logs["process"].str.contains(process_filter, case=False)]

        self.display_logs(filtered_logs)

    def sort_column(self, column):
        if self.logs is None:
            return

        # Сортировка
        self.logs = self.logs.sort_values(by=column, ascending=True)
        self.display_logs(self.logs)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewerApp(root)
    root.mainloop()
