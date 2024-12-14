import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.connected = False

    def connect(self, username, room):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.username = username
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

    def send_image(self, image_path):
        if self.connected:
            try:
                # Извлекаем имя файла
                filename = os.path.basename(image_path)
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                # Отправляем команду с именем файла, а затем файл
                self.socket.send(f"/image {filename}\n".encode())
                self.socket.send(image_data)
            except Exception as e:
                print(f"Error sending image: {e}")
                self.connected = False



    def receive_messages(self, callback):
        def listen():
            while self.connected:
                try:
                    data = self.socket.recv(4096).decode()
                    if data.startswith("/rooms"):
                        rooms = data.replace("/rooms ", "").strip()
                        callback(rooms, rooms_update=True)
                    else:
                        callback(data)
                except:
                    self.connected = False
                    callback("[INFO] Connection lost.")
                    break

        threading.Thread(target=listen, daemon=True).start()

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
        self.root.title("Chat Application")

        self.client = None

        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        tk.Label(self.top_frame, text="Username:").grid(row=0, column=0, padx=5)
        self.username_entry = tk.Entry(self.top_frame)
        self.username_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.top_frame, text="Room:").grid(row=0, column=2, padx=5)
        self.room_entry = tk.Entry(self.top_frame)
        self.room_entry.grid(row=0, column=3, padx=5)

        self.connect_button = tk.Button(self.top_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4, padx=5)

        self.disconnect_button = tk.Button(self.top_frame, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(row=0, column=5, padx=5)

        self.messages = scrolledtext.ScrolledText(self.root, state="disabled", wrap="word")
        self.messages.pack(padx=10, pady=10, fill="both", expand=True)

        self.rooms_listbox = tk.Listbox(self.root, height=5)
        self.rooms_listbox.pack(padx=10, pady=5, fill="x")

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=10)

        self.message_entry = tk.Entry(self.bottom_frame, width=50)
        self.message_entry.grid(row=0, column=0, padx=5)

        self.send_button = tk.Button(self.bottom_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        self.photo_button = tk.Button(self.bottom_frame, text="Photo", command=self.send_photo)
        self.photo_button.grid(row=0, column=2, padx=5)

        # Запрашиваем список комнат при запуске программы
        self.fetch_rooms_on_start()

    def fetch_rooms_on_start(self):
        """Запрашиваем список комнат сразу при старте программы."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
                temp_socket.connect(("127.0.0.1", 5002))  # Подключаемся к серверу
                temp_socket.send("/list".encode())  # Отправляем запрос на список комнат
                response = temp_socket.recv(4096).decode().strip()

                if response.startswith("/rooms"):
                    rooms = response.replace("/rooms ", "").split(",")
                    self.add_message(",".join(rooms), rooms_update=True)  # Обновляем список комнат
                else:
                    self.add_message("No rooms available.", rooms_update=True)
        except ConnectionRefusedError:
            self.add_message("[ERROR] Cannot connect to the server. Rooms list is unavailable.", rooms_update=True)

    def connect(self):
        username = self.username_entry.get().strip()
        room = self.room_entry.get().strip()

        if not username or not room:
            messagebox.showerror("Error", "Username and room are required!")
            return

        self.client = ChatClient("127.0.0.1", 5002)
        result = self.client.connect(username, room)

        if result is True:
            self.add_message("[INFO] Connected!")
            self.client.receive_messages(self.add_message)
        else:
            messagebox.showerror("Error", result)

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.add_message("[INFO] Disconnected!")

    def send_message(self):
        message = self.message_entry.get().strip()
        self.client.send_message(message)
        self.message_entry.delete(0, tk.END)

    def send_photo(self):
        photo_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg")])
        if photo_path:
            self.client.send_image(photo_path)

    def add_message(self, message, rooms_update=False):
        if rooms_update:
            self.rooms_listbox.delete(0, tk.END)
            if message:  # Если есть комнаты, отображаем их
                for room in message.split(","):
                    self.rooms_listbox.insert(tk.END, room.strip())
            else:
                self.rooms_listbox.insert(tk.END, "No available rooms.")
        else:
            self.messages.configure(state="normal")
            self.messages.insert(tk.END, message + "\n")
            self.messages.configure(state="disabled")
            self.messages.yview(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
