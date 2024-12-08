import os

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import OpenAIEmbeddings
from langchain_openai.embeddings import AzureOpenAIEmbeddings

from dotenv import load_dotenv
from pydantic import Field, BaseModel

load_dotenv()

LLM_MODEL = os.environ["LLM_MODEL"]
LLM_MODEL_PROVIDER = os.environ["LLM_MODEL_PROVIDER"]
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]


def get_chat_llm():
    return init_chat_model(
        model=LLM_MODEL,
        model_provider=LLM_MODEL_PROVIDER,
    )


def get_embedding_model():
    if "AZURE_OPENAI_API_KEY" in os.environ:
        return AzureOpenAIEmbeddings(model=EMBEDDING_MODEL)
    if "OPENAI_API_KEY" in os.environ:
        return OpenAIEmbeddings(model=EMBEDDING_MODEL)
    raise NotImplementedError("only Azure and OpenAI embeddings are supported")


SYSTEM_PROMPT = """You are Malcom Tucker from In The Thick of it. You will be asked idiotic questions 
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
        "there could be no, one or many parts of the response to find a source for."
        "\n\nHere is the response: "
        "{response}"
        "\n\nHere are the supporting source: "
        "{artifacts}"
        "Do not guess! It is better to find no citations than invent them."
    )

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt)])

    subgraph = prompt | get_chat_llm().with_structured_output(CitationList)

    artifacts = [
        getattr(message, "artifact", None) or [] for message in state["messages"]
    ]

    return subgraph.invoke(
        {"response": state["messages"][-1].content, "artifacts": sum(artifacts, [])}
    )


def to_json(obj):
    if isinstance(obj, dict):
        return {k: to_json(v) for k, v in obj.items() if k != "user_id"}
    if isinstance(obj, list):
        return list(map(to_json, obj))
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj
