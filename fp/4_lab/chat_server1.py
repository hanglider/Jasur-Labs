import asyncio

class ChatServer:
    def __init__(self):
        self.rooms = {}  # Словарь для хранения комнат и подключений

    async def handle_client(self, reader, writer):
        writer.write("Enter your name: ".encode())
        await writer.drain()
        name = (await reader.readline()).decode().strip()
        
        writer.write("Enter room name: ".encode())
        await writer.drain()
        room_name = (await reader.readline()).decode().strip()
        
        if room_name not in self.rooms:
            self.rooms[room_name] = []

        self.rooms[room_name].append(writer)
        writer.write(f"Welcome to {room_name}!\n".encode())
        await writer.drain()

        try:
            while True:
                data = await reader.readline()
                message = f"{name}: {data.decode()}"
                
                # Отправляем сообщение всем в комнате
                await self.broadcast(message, room_name, writer)
                
                if not data:
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Удаляем клиента из комнаты
            self.rooms[room_name].remove(writer)
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, message, room_name, sender_writer):
        for writer in self.rooms[room_name]:
            if writer != sender_writer:
                writer.write(message.encode())
                await writer.drain()

    async def main(self, host='127.0.0.1', port=8888):
        server = await asyncio.start_server(self.handle_client, host, port)
        async with server:
            print(f"Server started on {host}:{port}")
            await server.serve_forever()

if __name__ == "__main__":
    chat_server = ChatServer()
    asyncio.run(chat_server.main())