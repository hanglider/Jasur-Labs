import asyncio

async def client(host='127.0.0.1', port=8888):
    reader, writer = await asyncio.open_connection(host, port)

    name = input("Enter your name: ")
    writer.write(f"{name}\n".encode())
    await writer.drain()
    
    room_name = input("Enter room name: ")
    writer.write(f"{room_name}\n".encode())
    await writer.drain()
    
    print("Connected to the chat room! You can start sending messages.")

    async def send_messages():
        while True:
            message = input()
            writer.write(f"{message}\n".encode())
            await writer.drain()

    async def receive_messages():
        while True:
            data = await reader.readline()
            print(data.decode(), end='')

    await asyncio.gather(send_messages(), receive_messages())

if __name__ == "__main__":
    asyncio.run(client())