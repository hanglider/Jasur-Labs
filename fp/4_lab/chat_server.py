import asyncio

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.rooms = {}

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f'Server started on {self.host}:{self.port}')
        await self.server.serve_forever()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        print("Server stopped")

    async def handle_client(self, reader, writer):
        writer.write(b"Enter your name: ")
        await writer.drain()
        name = (await reader.readline()).decode().strip()

        writer.write(b"Enter room name: ")
        await writer.drain()
        room_name = (await reader.readline()).decode().strip()

        if room_name not in self.rooms:
            self.rooms[room_name] = []
        self.rooms[room_name].append(writer)

        try:
            await self.broadcast(f"{name} has joined the room.", room_name, writer)
            while True:
                message = await reader.readline()
                if not message:
                    break
                await self.broadcast(f"{name}: {message.decode()}", room_name, writer)
        finally:
            self.rooms[room_name].remove(writer)
            if not self.rooms[room_name]:  # Удаляем комнату, если она пустая
                del self.rooms[room_name]
            await self.broadcast(f"{name} has left the room.", room_name, writer)
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, message, room_name, sender_writer):
        for writer in self.rooms.get(room_name, []):
            if writer != sender_writer:
                writer.write(message.encode())
                await writer.drain()

# Запуск сервера для ручного тестирования
if __name__ == "__main__":
    server = ChatServer(host='127.0.0.1', port=8888)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Server shutting down...")
