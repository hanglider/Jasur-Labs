import pytest
import asyncio
from server import ChatServer  # Импорт вашего сервера

@pytest.mark.asyncio
async def test_broadcast():
    server = ChatServer()
    reader1, writer1 = await asyncio.open_connection()
    reader2, writer2 = await asyncio.open_connection()

    await server.handle_client(reader1, writer1)
    await server.handle_client(reader2, writer2)

    # Тесты на отправку сообщений, соединение клиентов и т.д.

    writer1.close()
    writer2.close()