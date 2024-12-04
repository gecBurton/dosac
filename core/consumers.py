from uuid import UUID

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from langchain_core.messages import (
    SystemMessage,
    AnyMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from core.models import Chat, ChatMessage as ChatMessageModel, Citation as CitationModel
from core.tools import (
    search_documents,
    list_documents,
    delete_document,
    search_wikipedia,
)

SYSTEM_PROMPT = """ you are Malcom Tucker from In The Thick of it. You will be asked idiotic questions 
from disgruntled civil servants. reply in character using Markdown"""


agent = create_react_agent(
    settings.LLM,
    tools=[search_wikipedia, search_documents, list_documents, delete_document],
)


class Citation(BaseModel):
    """A reference to a source that supports a claim made in the response"""

    text_in_answer: str = Field(
        description="Exact part of text from `answer` that references a source, include formatting."
    )
    text_in_source: str = Field(
        description="Exact part of text from `source` that supports the `answer`"
    )
    reference: str = Field(
        description="reference to the source, could be a file-name, url or uri"
    )


class CitationList(BaseModel):
    """a list of citations that support the response"""

    citations: list[Citation] = Field(
        default_factory=list,
        description="a list of citations that support the response",
    )


@RunnableLambda
def citations(state):
    system_prompt = (
        "Given a response to a question and the sources that support it "
        "determine which parts of the response are supported by source "
        "there is likely to be more than one part of the response to find a source for."
        "\n\nHere is the response: "
        "{response}"
        "\n\nHere are the supporting source: "
        "{artifacts}"
        "Do not guess or invent citations!"
    )

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt)])

    subgraph = prompt | settings.LLM.with_structured_output(CitationList)

    artifacts = [
        getattr(message, "artifact", None) or [] for message in state["messages"]
    ]

    return subgraph.invoke(
        {"response": state["messages"][-1].content, "artifacts": sum(artifacts, [])}
    )


class ChatMessage(BaseModel):
    chat_id: UUID | None = None
    message: AnyMessage


def to_json(obj):
    if isinstance(obj, dict):
        return {k: to_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return list(map(to_json, obj))
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj


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
