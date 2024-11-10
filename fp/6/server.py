import asyncio

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.rooms = {}

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            print(f'Server started on {self.host}:{self.port}')
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        try:
            # Получение имени пользователя
            writer.write(b"Enter your name: ")
            await writer.drain()
            name = (await reader.readline()).decode().strip()

            # Получение комнаты
            writer.write(b"Enter room name: ")
            await writer.drain()
            room_name = (await reader.readline()).decode().strip()

            # Добавление пользователя в комнату
            if room_name not in self.rooms:
                self.rooms[room_name] = []
            self.rooms[room_name].append((name, writer))
            await self.broadcast(f"{name} has joined the room.", room_name)

            # Чтение и пересылка сообщений
            while True:
                message = await reader.readline()
                if message.decode().strip() == "#":  # Отключение по команде '#'
                    break
                await self.broadcast(f"{name}: {message.decode()}", room_name, sender=writer)
        
        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.remove_client(name, writer, room_name)
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, message, room_name, sender=None):
        for client_name, writer in self.rooms.get(room_name, []):
            if writer != sender:  # Не отправляем обратно отправителю
                writer.write(message.encode())
                await writer.drain()

    def remove_client(self, name, writer, room_name):
        # Удаляем клиента из комнаты
        self.rooms[room_name] = [(n, w) for n, w in self.rooms[room_name] if w != writer]
        print(f"{name} has left {room_name}")
        if not self.rooms[room_name]:  # Если комната пуста, удаляем
            del self.rooms[room_name]

# Запуск сервера
if __name__ == "__main__":
    server = ChatServer(host='127.0.0.1', port=8888)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Server shutting down...")
