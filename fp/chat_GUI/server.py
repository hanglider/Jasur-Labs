import socket
import threading
import time
import os

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {username: (socket, room)}
        self.rooms = {}    # {room: [username1, username2]}

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        threading.Thread(target=self.broadcast_rooms, daemon=True).start()

        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()

    def broadcast_rooms(self):
        while True:
            time.sleep(3)
            rooms_list = "/rooms " + ",".join(self.rooms.keys())
            for username, (client_socket, _) in self.clients.items():
                try:
                    client_socket.send(rooms_list.encode())
                except:
                    self.disconnect_client(username)

    def handle_client(self, client_socket, addr):
        username = None
        room = None

        try:
            while True:
                data = client_socket.recv(4096).decode().strip()
                if not data:
                    break

                if data.startswith("/join"):
                    room = data.split()[1]
                    username = f"{addr[0]}:{addr[1]}"
                    self.clients[username] = (client_socket, room)

                    if room not in self.rooms:
                        self.rooms[room] = []
                    self.rooms[room].append(username)

                    self.send_to_room(room, f"[INFO] {username} has joined the room {room}")

                elif data.startswith("/image"):
                    # Извлекаем имя файла из команды
                    _, filename = data.split(maxsplit=1)

                    # Получаем данные изображения
                    image_data = client_socket.recv(1024 * 1024)  # 1 MB buffer
                    self.save_image(username, filename, image_data, room)

                elif data.startswith("/quit"):
                    break

                else:
                    self.send_to_room(room, f"{username}: {data}")

        except Exception as e:
            print(f"Error with client {addr}: {e}")
        finally:
            self.disconnect_client(username)


    def send_to_room(self, room, message):
        if room in self.rooms:
            for user in self.rooms[room]:
                if user in self.clients:
                    client_socket, _ = self.clients[user]
                    try:
                        client_socket.send(message.encode())
                    except:
                        self.disconnect_client(user)

    def save_image(self, username, filename, image_data, room):
        # Сохраняем файл с оригинальным именем
        save_path = os.path.join(r"C:\IT\Jasur-Labs\fp\chat_GUI\downloads", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        try:
            # Сохраняем данные изображения
            with open(save_path, "wb") as f:
                f.write(image_data)

            self.send_to_room(room, f"[INFO] Image saved as {filename}")
        except Exception as e:
            print(f"Failed to save image for {username}: {e}")



    def disconnect_client(self, username):
        if username in self.clients:
            client_socket, room = self.clients[username]
            try:
                client_socket.close()
            except:
                pass
            del self.clients[username]

            if room in self.rooms:
                self.rooms[room].remove(username)
                if not self.rooms[room]:
                    del self.rooms[room]

            self.send_to_room(room, f"[INFO] {username} has left the room")


if __name__ == "__main__":
    server = ChatServer("127.0.0.1", 5002)
    server.start()
