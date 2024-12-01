import socket
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self, room):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.send(f"/join {room}\n".encode())
            self.connected = True
            return True
        except Exception as e:
            return str(e)

    def send_message(self, message):
        if self.connected:
            try:
                self.socket.send(message.encode())
            except:
                self.connected = False

    def receive_messages(self, callback):
        def listen():
            while self.connected:
                try:
                    message = self.socket.recv(1024).decode()
                    if message:
                        callback(message)
                except:
                    self.connected = False
                    callback("[INFO] Соединение с сервером потеряно.")
                    break

        Thread(target=listen, daemon=True).start()

    def disconnect(self):
        if self.connected:
            try:
                self.socket.send("/quit\n".encode())
                self.socket.close()
            except:
                pass
        self.connected = False


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Чат-клиент")

        self.client = None

        # Поля ввода для имени и комнаты
        self.frame_top = tk.Frame(self.root)
        self.frame_top.pack(pady=10)

        tk.Label(self.frame_top, text="Имя:").grid(row=0, column=0, padx=5)
        self.username_entry = tk.Entry(self.frame_top)
        self.username_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.frame_top, text="Комната:").grid(row=0, column=2, padx=5)
        self.room_entry = tk.Entry(self.frame_top)
        self.room_entry.grid(row=0, column=3, padx=5)

        self.connect_button = tk.Button(self.frame_top, text="Подключиться", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=5)

        # Поле для сообщений
        self.messages_text = scrolledtext.ScrolledText(self.root, state="disabled", wrap="word")
        self.messages_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Поле ввода сообщений
        self.frame_bottom = tk.Frame(self.root)
        self.frame_bottom.pack(pady=10)

        self.message_entry = tk.Entry(self.frame_bottom, width=50)
        self.message_entry.grid(row=0, column=0, padx=5)

        self.send_button = tk.Button(self.frame_bottom, text="Отправить", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        self.quit_button = tk.Button(self.frame_bottom, text="Выйти", command=self.quit_chat)
        self.quit_button.grid(row=0, column=2, padx=5)

    def connect_to_server(self):
        username = self.username_entry.get().strip()
        room = self.room_entry.get().strip()

        if not username or not room:
            messagebox.showerror("Ошибка", "Имя и комната обязательны!")
            return

        if not self.client:
            self.client = ChatClient("127.0.0.1", 5002)

        result = self.client.connect(room)
        if result is True:
            self.add_message(f"[INFO] Подключено к комнате: {room}")
            self.client.receive_messages(self.add_message)
        else:
            messagebox.showerror("Ошибка подключения", result)

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return

        if message.lower() == "/quit":
            self.quit_chat()
            return

        self.client.send_message(message)
        self.message_entry.delete(0, tk.END)

    def add_message(self, message):
        self.messages_text.configure(state="normal")
        self.messages_text.insert(tk.END, message + "\n")
        self.messages_text.configure(state="disabled")
        self.messages_text.see(tk.END)

    def quit_chat(self):
        if self.client:
            self.client.disconnect()
        self.add_message("[INFO] Отключено от сервера.")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
