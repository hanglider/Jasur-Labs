import asyncio
import pytest
from server import ChatServer

@pytest.fixture
async def chat_server():
    server = ChatServer('127.0.0.1', 8888)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)  # даем время серверу для старта
    yield server
    server_task.cancel()

async def connect_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    await reader.readline()  # Enter your name:
    writer.write(b"TestClient\n")
    await reader.readline()  # Enter room name:
    writer.write(b"TestRoom\n")
    await reader.readline()  # Client joined message
    return reader, writer

@pytest.mark.asyncio
async def test_client_connection(chat_server):
    reader, writer = await connect_client()
    assert writer.is_closing() is False
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
async def test_message_broadcast(chat_server):
    reader1, writer1 = await connect_client()
    reader2, writer2 = await connect_client()

    # Client 1 sends message
    writer1.write(b"Hello from Client 1\n")
    await writer1.drain()

    # Client 2 should receive the message
    message = await reader2.readline()
    assert "Hello from Client 1" in message.decode()

    # Disconnect clients
    writer1.write(b"#\n")
    writer2.write(b"#\n")
    await writer1.drain()
    await writer2.drain()
    writer1.close()
    writer2.close()
    await writer1.wait_closed()
    await writer2.wait_closed()
