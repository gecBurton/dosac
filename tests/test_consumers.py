import pytest
from channels.testing import WebsocketCommunicator

from core.consumers import ChatConsumer


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_receive_json(async_chat):
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"{async_chat.id}/")
    communicator.scope["user"] = async_chat.user
    communicator.scope["url_route"] = {"kwargs": {"chat_id": async_chat.id}}
    connected, _ = await communicator.connect()

    assert connected

    await communicator.send_json_to({"content": "hello"})
    response_1 = await communicator.receive_json_from()
    assert response_1["event"] == "on_chain_end"
    assert len(response_1["data"]["output"]["messages"]) == 3

    response_2 = await communicator.receive_json_from()
    assert response_2["event"] == "on_chain_end"
    assert response_2["data"]["output"] == {"citations": []}

    response_3 = await communicator.receive_json_from()
    assert response_2["event"] == "on_chain_end"
    assert response_3["data"]["annotated_content"]

    await communicator.disconnect()
