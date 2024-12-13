import tkinter as tk
from tkinter import messagebox
from blocker import block_ip, unblock_ip
from logger import log_suspicious_event


class TrafficMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Traffic Monitor")
        self.geometry("1200x600")

        # Панель для запросов
        request_frame = tk.Frame(self)
        request_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(request_frame, text="Network Requests").pack()
        self.request_list = tk.Listbox(request_frame, height=25, width=50)
        self.request_list.pack(pady=10)

        self.block_button = tk.Button(
            request_frame, text="Block Selected IP", command=self.block_selected_ip
        )
        self.block_button.pack(pady=5)

        # Панель для заблокированных IP
        blocked_frame = tk.Frame(self)
        blocked_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(blocked_frame, text="Blocked IPs").pack()
        self.blocked_list = tk.Listbox(blocked_frame, height=25, width=50)
        self.blocked_list.pack(pady=10)

        self.unblock_button = tk.Button(
            blocked_frame, text="Unblock Selected IP", command=self.unblock_selected_ip
        )
        self.unblock_button.pack(pady=5)

    def add_request(self, ip, reason=None):
        """Добавить запрос в список. Если reason указан, выделить запрос красным."""
        item_text = f"{ip} - {reason if reason else 'Normal'}"
        self.request_list.insert(tk.END, item_text)

        if reason:
            self.request_list.itemconfig(self.request_list.size() - 1, {"fg": "red"})

    def add_blocked_ip(self, ip):
        """Добавить IP в список заблокированных."""
        self.blocked_list.insert(tk.END, ip)

    def block_selected_ip(self):
        """Блокировать выбранный IP из списка запросов."""
        try:
            selected_index = self.request_list.curselection()[0]
            selected_item = self.request_list.get(selected_index)
            ip = selected_item.split(" - ")[0]

            block_ip(ip)
            log_suspicious_event(ip, "Manually blocked by user")
            self.add_blocked_ip(ip)
            messagebox.showinfo("Blocked", f"IP {ip} has been blocked.")
        except IndexError:
            messagebox.showwarning("No Selection", "No IP selected for blocking.")

    def unblock_selected_ip(self):
        """Разблокировать выбранный IP из списка заблокированных."""
        try:
            selected_index = self.blocked_list.curselection()[0]
            ip = self.blocked_list.get(selected_index)

            unblock_ip(ip)
            log_suspicious_event(ip, "Manually unblocked by user")
            self.blocked_list.delete(selected_index)
            messagebox.showinfo("Unblocked", f"IP {ip} has been unblocked.")
        except IndexError:
            messagebox.showwarning("No Selection", "No IP selected for unblocking.")
