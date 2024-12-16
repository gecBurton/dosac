import pytest

from core.tools import (
    list_documents,
    list_chats,
    build_delete_document,
    search_documents,
)


@pytest.mark.django_db
def test_list_documents(user_with_many_documents):
    documents = list_documents.invoke({"user_id": user_with_many_documents.id})
    assert len(documents) > 0


@pytest.mark.django_db
def test_list_chats(user_with_many_chat_messages):
    chats = list_chats.invoke({"user_id": user_with_many_chat_messages.id})
    assert len(chats) == 10


@pytest.mark.django_db
def test_build_delete_document(user_document):
    delete_document = build_delete_document(user_document.user.id)
    assert delete_document.invoke({"exact_document_name": user_document.file.name})


@pytest.mark.django_db
def test_search_documents(user_embedded_document, fake_embeddings):
    """this is a rubbish test that needs improving!"""
    assert search_documents.invoke(
        {"user_id": user_embedded_document.user.id, "query": "hello"}
    )
