import pytest
import asyncio
from chat_server import ChatServer

HOST = '127.0.0.1'
PORT = 8888

@pytest.fixture
async def server():
    server_instance = ChatServer()
    await server_instance.start(HOST, PORT)
    yield server_instance
    await server_instance.stop()