from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from langchain_core.messages import (
    SystemMessage,
)
from langgraph.prebuilt import create_react_agent

from core.ai_core import get_chat_llm, ChatMessage, citations, SYSTEM_PROMPT, to_json
from core.models import Chat, ChatMessage as ChatMessageModel, Citation as CitationModel
from core.tools import (
    search_documents,
    list_documents,
    delete_document,
    search_wikipedia,
)

agent = create_react_agent(
    get_chat_llm(),
    tools=[search_wikipedia, search_documents, list_documents, delete_document],
)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def disconnect(self, close_code):
        # Handle disconnection
        await self.close()

    async def receive_json(self, content, **kwargs):
        chat_message = ChatMessage.model_validate(content)

        chat = await Chat.objects.aget(id=chat_message.chat_id)

        await sync_to_async(ChatMessageModel.from_langchain)(
            chat=chat, message=chat_message.message
        )

        graph = agent | {"citations": citations}

        messages = await sync_to_async(chat.to_langchain)()
        answer: ChatMessageModel | None = None

        async for event in graph.astream_events(
            {"messages": [SystemMessage(content=SYSTEM_PROMPT), *messages]},
            stream_mode="values",
            version="v2",
        ):
            await self.send_json(content=to_json(event))

            if event["event"] == "on_chain_end" and event["name"] == "LangGraph":
                last_message = event["data"]["output"]["messages"][-1]
                answer = await sync_to_async(ChatMessageModel.from_langchain)(
                    chat=chat, message=last_message
                )

            elif event["event"] == "on_chain_end" and event["name"] == "citations":
                for index, citation in enumerate(
                    event["data"]["output"].citations, start=1
                ):
                    await CitationModel.objects.acreate(
                        chat_message=answer,
                        text_in_answer=citation.text_in_answer,
                        text_in_source=citation.text_in_source,
                        reference=citation.reference,
                        index=index,
                    )

        annotated_content = await sync_to_async(answer.annotated_content)()
        await self.send_json(
            content={"event": "done", "data": {"annotated_content": annotated_content}}
        )
        print("done!")
