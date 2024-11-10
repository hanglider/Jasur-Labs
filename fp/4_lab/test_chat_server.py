import asyncio
import pytest
from chat_server import ChatServer  # Предположим, что ваш класс сервера называется ChatServer

HOST = "127.0.0.1"
PORT = 8888

@pytest.fixture
async def server():
    srv = ChatServer(HOST, PORT)
    await srv.start()  # Запуск сервера
    yield srv
    await srv.stop()   # Остановка сервера после завершения тестов

@pytest.mark.asyncio
async def test_client_connection(server):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    await reader.readuntil(b"Enter your name: ")
    writer.write(b"Client1\n")
    await writer.drain()
    
    await reader.readuntil(b"Enter room name: ")
    writer.write(b"Room1\n")
    await writer.drain()
    
    # Проверяем, что клиент подключен к комнате
    assert "Room1" in server.rooms
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
async def test_message_broadcast(server):
    reader1, writer1 = await asyncio.open_connection(HOST, PORT)
    reader2, writer2 = await asyncio.open_connection(HOST, PORT)

    await reader1.readuntil(b"Enter your name: ")
    writer1.write(b"Client1\n")
    await writer1.drain()
    
    await reader1.readuntil(b"Enter room name: ")
    writer1.write(b"Room1\n")
    await writer1.drain()
    
    await reader2.readuntil(b"Enter your name: ")
    writer2.write(b"Client2\n")
    await writer2.drain()
    
    await reader2.readuntil(b"Enter room name: ")
    writer2.write(b"Room1\n")
    await writer2.drain()

    # Проверка, что клиенты находятся в одной комнате
    assert writer1 in server.rooms["Room1"]
    assert writer2 in server.rooms["Room1"]

    writer1.close()
    await writer1.wait_closed()
    writer2.close()
    await writer2.wait_closed()

@pytest.mark.asyncio
async def test_separate_rooms(server):
    reader1, writer1 = await asyncio.open_connection(HOST, PORT)
    reader2, writer2 = await asyncio.open_connection(HOST, PORT)

    await reader1.readuntil(b"Enter your name: ")
    writer1.write(b"Client1\n")
    await writer1.drain()
    await reader1.readuntil(b"Enter room name: ")
    writer1.write(b"Room1\n")
    await writer1.drain()

    await reader2.readuntil(b"Enter your name: ")
    writer2.write(b"Client2\n")
    await writer2.drain()
    await reader2.readuntil(b"Enter room name: ")
    writer2.write(b"Room2\n")
    await writer2.drain()

    # Проверка, что клиенты находятся в разных комнатах
    assert writer1 in server.rooms["Room1"]
    assert writer2 in server.rooms["Room2"]

    writer1.close()
    await writer1.wait_closed()
    writer2.close()
    await writer2.wait_closed()

@pytest.mark.asyncio
async def test_error_handling(server):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    await reader.readuntil(b"Enter your name: ")
    writer.write(b"Client_with_error\n")
    await writer.drain()
    await reader.readuntil(b"Enter room name: ")
    writer.write(b"Room_with_error\n")
    await writer.drain()

    # Закрываем соединение, чтобы вызвать ошибку на стороне сервера
    writer.close()
    await writer.wait_closed()

    await asyncio.sleep(1)  # Пауза, чтобы сервер успел обработать отключение

    # Проверяем, что сервер удалил клиента из комнаты
    assert "Room_with_error" not in server.rooms or writer not in server.rooms.get("Room_with_error", [])
