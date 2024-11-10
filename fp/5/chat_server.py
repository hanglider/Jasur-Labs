import asyncio

class ChatServer:
    def __init__(self):
        self.rooms = {}

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

        await self.broadcast(f"{name} has joined {room_name}", room_name)

        while True:
            data = await reader.readline()
            if not data:
                break
            message = f"{name}: {data.decode()}"
            await self.broadcast(message, room_name)

        writer.close()
        await writer.wait_closed()
        self.rooms[room_name].remove(writer)
        await self.broadcast(f"{name} has left {room_name}", room_name)

    async def broadcast(self, message, room_name):
        for writer in self.rooms[room_name]:
            writer.write(f"{message}\n".encode())
            await writer.drain()

    async def start(self, host, port):
        self.server = await asyncio.start_server(self.handle_client, host, port)
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()