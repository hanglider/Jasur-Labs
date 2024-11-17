import asyncio

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002
separator_token = "<SEP>"

rooms = {}

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[+] {addr} connected.")
    current_room = None

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode().strip()

            # Обработка команды /join для входа в комнату
            if message.startswith("/join"):
                room_name = message.split(" ", 1)[-1].strip()
                if current_room:
                    rooms[current_room].remove(writer)
                    if not rooms[current_room]:
                        del rooms[current_room]
                current_room = room_name
                if current_room not in rooms:
                    rooms[current_room] = set()
                rooms[current_room].add(writer)
                writer.write(f"[INFO] Joined room: {current_room}\n".encode())
                await writer.drain()
                continue

            # Обработка команды /quit для завершения работы клиента
            if message.lower() == "/quit":
                writer.write("[INFO] Disconnected from the server.\n".encode())
                await writer.drain()
                break

            # Обработка команды exit для выхода из комнаты
            if message.lower() == "/exit":
                if current_room:
                    rooms[current_room].remove(writer)
                    if not rooms[current_room]:
                        del rooms[current_room]
                    current_room = None
                writer.write("[INFO] Left the room. Use /join <room_name> to join a new room.\n".encode())
                await writer.drain()
                continue

            # Если клиент не в комнате
            if not current_room:
                writer.write("[ERROR] Join a room first using /join <room_name>.\n".encode())
                await writer.drain()
                continue

            # Рассылка сообщения всем в комнате
            formatted_message = f"[{addr}] {message.replace(separator_token, ': ')}"
            print(f"Room {current_room}: {formatted_message.strip()}")
            for client in rooms[current_room]:
                try:
                    client.write(formatted_message.encode())
                    await client.drain()
                except ConnectionResetError:
                    # Если клиент разорвал соединение, игнорируем ошибку
                    continue
    except ConnectionResetError:
        print(f"[!] Connection reset by {addr}")
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        if current_room and writer in rooms.get(current_room, set()):
            rooms[current_room].remove(writer)
            if not rooms[current_room]:
                del rooms[current_room]
        print(f"[-] {addr} disconnected.")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, SERVER_HOST, SERVER_PORT)
    addr = server.sockets[0].getsockname()
    print(f"[*] Listening as {addr[0]}:{addr[1]}")

    async with server:
        await server.serve_forever()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[!] Server stopped.")
