import pytest
import asyncio
from chat_client import ChatClient

HOST = '127.0.0.1'
PORT = 8888

@pytest.mark.asyncio
async def test_client_connection(server):
    client = ChatClient("Client1", "Room1", HOST, PORT)
    await client.connect()

    # Проверяем, что клиент находится в нужной комнате
    assert "Room1" in server.rooms
    assert client.writer in server.rooms["Room1"]

    await client.disconnect()

@pytest.mark.asyncio
async def test_message_broadcast(server):
    client1 = ChatClient("Client1", "Room1", HOST, PORT)
    client2 = ChatClient("Client2", "Room1", HOST, PORT)

    await client1.connect()
    await client2.connect()

    # Отправляем сообщение от клиента 1 и проверяем, что клиент 2 его получил
    await client1.send_message("Hello from Client1")
    received_message = await client2.receive_message()
    assert received_message == b"Client1: Hello from Client1\n"

    await client1.disconnect()
    await client2.disconnect()

@pytest.mark.asyncio
async def test_separate_rooms(server):
    client1 = ChatClient("Client1", "Room1", HOST, PORT)
    client2 = ChatClient("Client2", "Room2", HOST, PORT)

    await client1.connect()
    await client2.connect()

    # Проверяем, что клиенты находятся в разных комнатах
    assert client1.writer in server.rooms["Room1"]
    assert client2.writer in server.rooms["Room2"]

    await client1.disconnect()
    await client2.disconnect()

@pytest.mark.asyncio
async def test_error_handling(server):
    client = ChatClient("Client_with_error", "Room_with_error", HOST, PORT)
    await client.connect()

    # Отключаем клиента, чтобы вызвать ошибку на стороне сервера
    await client.disconnect()

    await asyncio.sleep(1)  # Небольшая задержка для обработки отключения

    # Проверяем, что клиент удален из комнаты
    assert client.writer not in server.rooms.get("Room_with_error", [])
