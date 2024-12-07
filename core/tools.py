from logging import getLogger
from typing import Annotated

import wikipedia
from django.contrib.auth import get_user_model
from langchain_core.documents import Document
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from core.ai_core import get_embedding_model
from core.models import Document as DocumentModel, Chat, Embedding

logger = getLogger(__name__)
User = get_user_model()


@tool(response_format="content_and_artifact")
def search_wikipedia(
    query: str, top_k_results: int = 3, doc_content_chars_max: int = 4000
) -> tuple[str, list[Document]]:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query, results=top_k_results)
    contents = []
    sources = []
    for page_title in page_titles:
        if page := wikipedia.page(title=page_title, auto_suggest=False):
            for section in page.sections:
                if section_content := page.section(section):
                    contents.append(section_content)

                    fragment = section.replace(" ", "_")
                    document = Document(
                        page_content=section_content,
                        metadata={
                            "url": page.url + "#" + fragment,
                            "title": page.title,
                        },
                    )
                    sources.append(document)
    if not contents:
        return "No good Wikipedia Search Result was found", []

    return "\n\n".join(contents)[:doc_content_chars_max], sources


@tool(response_format="content_and_artifact")
def search_documents(
    user_id: Annotated[str, InjectedState("user_id")],
    query: str,
    top_k_results: int = 3,
) -> tuple[str, list[Document]]:
    """search users own documents for relevant sections"""
    embedded_query = get_embedding_model().embed_query(query)
    documents = Embedding.search_by_vector(user_id, embedded_query, top_k_results)

    logger.info(f"converted {len(documents)} docs to langchain")
    return "\n\n".join(document.page_content for document in documents), documents


@tool(response_format="content_and_artifact")
def list_documents(
    user_id: Annotated[str, InjectedState("user_id")],
) -> tuple[str, list[dict[str, str]]]:
    """returns a list of the users documents by exact name"""
    docs = list(DocumentModel.objects.filter(user_id=user_id))
    metadata = [
        {"uri": doc.file.url, "name": doc.file.name, "status": doc.status}
        for doc in docs
    ]
    return "\n".join(doc.file.name for doc in docs), metadata


@tool
def delete_document(
    user_id: Annotated[str, InjectedState("user_id")], exact_document_name: str
) -> bool:
    """delete a document give the exact_document_name,
    returns True if the document was found else False
    """
    try:
        DocumentModel.objects.get(user_id=user_id, file=exact_document_name).delete()
    except DocumentModel.DoesNotExist:
        return False
    return True


@tool
def list_chats(
    user_id: Annotated[str, InjectedState("user_id")],
) -> list[list[Document]]:
    """returns a list of previous chats"""
    return [chat.to_langchain() for chat in Chat.objects.filter(user_id=user_id)]
