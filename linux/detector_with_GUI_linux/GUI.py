import tkinter as tk
from tkinter import messagebox
from blocker import block_ip
from logger import log_suspicious_event


class TrafficMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Traffic Monitor")
        self.geometry("800x600")

        # Список сетевых запросов
        self.request_list = tk.Listbox(self, height=25, width=80)
        self.request_list.pack(pady=10)

        # Кнопка блокировки
        self.block_button = tk.Button(self, text="Block Selected IP", command=self.block_selected_ip)
        self.block_button.pack(pady=5)

    def add_request(self, ip, reason=None):
        """Добавить запрос в список. Если reason указан, выделить запрос красным."""
        item_text = f"{ip} - {reason if reason else 'Normal'}"
        self.request_list.insert(tk.END, item_text)

        if reason:
            # Выделение подозрительного трафика
            self.request_list.itemconfig(self.request_list.size() - 1, {'fg': 'red'})

    def block_selected_ip(self):
        """Блокировать выбранный IP из списка."""
        try:
            selected_index = self.request_list.curselection()[0]
            selected_item = self.request_list.get(selected_index)
            ip = selected_item.split(" - ")[0]

            block_ip(ip)
            log_suspicious_event(ip, "Manually blocked by user")
            messagebox.showinfo("Blocked", f"IP {ip} has been blocked.")
        except IndexError:
            messagebox.showwarning("No Selection", "No IP selected for blocking.")
