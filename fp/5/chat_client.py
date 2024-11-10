import asyncio

class ChatClient:
    def __init__(self, name, room, host='127.0.0.1', port=8888):
        self.name = name
        self.room = room
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        await self.reader.readuntil(b"Enter your name: ")
        self.writer.write(f"{self.name}\n".encode())
        await self.writer.drain()

        await self.reader.readuntil(b"Enter room name: ")
        self.writer.write(f"{self.room}\n".encode())
        await self.writer.drain()

    async def send_message(self, message):
        if self.writer:
            self.writer.write(f"{message}\n".encode())
            await self.writer.drain()

    async def receive_message(self):
        if self.reader:
            return await self.reader.readline()

    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
