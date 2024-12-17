from unittest.mock import patch

import pytest
from channels.testing import WebsocketCommunicator
from langchain_core.messages import AIMessage

from core.consumers import ChatConsumer
from tests.conftest import FakeChatModel


@pytest.mark.asyncio
@pytest.mark.django_db
@patch("core.consumers.get_chat_llm")
async def test_receive_json(fake_chat_model, async_chat):
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"{async_chat.id}/")
    communicator.scope["user"] = async_chat.user
    communicator.scope["url_route"] = {"kwargs": {"chat_id": async_chat.id}}
    connected, _ = await communicator.connect()

    assert connected

    fake_chat_model.return_value = FakeChatModel(
        messages=iter(
            [
                AIMessage(content="hello"),
                AIMessage(content="hello"),
            ]
        )
    )

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
