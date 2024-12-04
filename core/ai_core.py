from uuid import UUID

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai.embeddings import AzureOpenAIEmbeddings

from dotenv import load_dotenv
from pydantic import Field, BaseModel

load_dotenv()


def get_chat_llm():
    return init_chat_model(
        model="gpt-4o",
        model_provider="azure_openai",
    )


def get_embedding_model():
    return AzureOpenAIEmbeddings(
        model="text-embedding-3-large",
    )


SYSTEM_PROMPT = """ you are Malcom Tucker from In The Thick of it. You will be asked idiotic questions 
from disgruntled civil servants. reply in character using Markdown"""


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

    subgraph = prompt | get_chat_llm().with_structured_output(CitationList)

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
