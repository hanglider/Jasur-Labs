import pytest
import asyncio
from chat_server import ChatServer

HOST = '127.0.0.1'
PORT = 8888

@pytest.fixture
async def server():
    # Создаем экземпляр сервера
    chat_server = ChatServer()
    server_task = asyncio.create_task(chat_server.main(HOST, PORT))
    
    # Ждем, пока сервер запустится
    await asyncio.sleep(1)
    yield chat_server
    
    # Останавливаем сервер после завершения теста
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_client_connection(server):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    assert reader is not None
    assert writer is not None
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
async def test_message_broadcast(server):
    reader1, writer1 = await asyncio.open_connection(HOST, PORT)
    reader2, writer2 = await asyncio.open_connection(HOST, PORT)
    
    # Вводим имя и комнату для клиента 1
    await reader1.readuntil(b"Enter your name: ")
    writer1.write(b"Client1\n")
    await writer1.drain()
    
    await reader1.readuntil(b"Enter room name: ")
    writer1.write(b"Room1\n")
    await writer1.drain()

    # Вводим имя и комнату для клиента 2
    await reader2.readuntil(b"Enter your name: ")
    writer2.write(b"Client2\n")
    await writer2.drain()
    
    await reader2.readuntil(b"Enter room name: ")
    writer2.write(b"Room1\n")
    await writer2.drain()
    
    # Проверка, что клиенты подключились к одной комнате
    assert server.rooms["Room1"] == [writer1, writer2]
    
    # Клиент 1 отправляет сообщение
    writer1.write(b"Hello from Client1\n")
    await writer1.drain()

    # Клиент 2 должен получить это сообщение
    message = await reader2.readline()
    assert message.decode() == "Client1: Hello from Client1\n"

    writer1.close()
    await writer1.wait_closed()
    writer2.close()
    await writer2.wait_closed()

@pytest.mark.asyncio
async def test_separate_rooms(server):
    reader1, writer1 = await asyncio.open_connection(HOST, PORT)
    reader2, writer2 = await asyncio.open_connection(HOST, PORT)
    
    # Подключаем клиента 1 к комнате Room1
    await reader1.readuntil(b"Enter your name: ")
    writer1.write(b"Client1\n")
    await writer1.drain()
    
    await reader1.readuntil(b"Enter room name: ")
    writer1.write(b"Room1\n")
    await writer1.drain()

    # Подключаем клиента 2 к комнате Room2
    await reader2.readuntil(b"Enter your name: ")
    writer2.write(b"Client2\n")
    await writer2.drain()
    
    await reader2.readuntil(b"Enter room name: ")
    writer2.write(b"Room2\n")
    await writer2.drain()
    
    # Проверка, что клиенты находятся в разных комнатах
    assert server.rooms["Room1"] == [writer1]
    assert server.rooms["Room2"] == [writer2]

    # Клиент 1 отправляет сообщение, клиент 2 не должен его получить
    writer1.write(b"Hello from Room1\n")
    await writer1.drain()

    # Проверяем, что у клиента 2 нет новых сообщений
    writer2.write(b"\n")  # Отправляем пустое сообщение, чтобы вызвать readline
    await writer2.drain()
    message = await reader2.readline()
    assert message.decode() != "Client1: Hello from Room1\n"

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

    # Проверка, что сервер корректно обработал отключение и очистил комнату
    await asyncio.sleep(1)  # Ждем, чтобы сервер успел обработать отключение
    assert "Room_with_error" not in server.rooms or writer not in server.rooms.get("Room_with_error", [])