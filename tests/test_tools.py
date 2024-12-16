import pytest

from core.tools import list_documents, list_chats


@pytest.mark.django_db
def test_list_documents(user_with_many_documents):
    documents = list_documents.invoke({"user_id": user_with_many_documents.id})
    assert len(documents) > 0


@pytest.mark.django_db
def test_list_chats(user_with_many_chat_messages):
    chats = list_chats.invoke({"user_id": user_with_many_chat_messages.id})
    assert len(chats) == 10
