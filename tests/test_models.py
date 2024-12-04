import pytest
from langchain_core.messages import AIMessage, HumanMessage

from core.models import ChatMessage, Citation


@pytest.mark.django_db
def test_chat_to_langchain(chat):
    ChatMessage.objects.create(
        chat=chat, content="tell me a story", type=ChatMessage.TYPES.HUMAN
    )
    ChatMessage.objects.create(
        chat=chat, content="the cat sat on the mat", type=ChatMessage.TYPES.AI
    )

    assert chat.to_langchain() == [
        HumanMessage(content="tell me a story"),
        AIMessage(content="the cat sat on the mat"),
    ]


@pytest.mark.django_db
def test_chat_from_langchain(chat):
    initial_count = chat.chatmessage_set.count()

    ChatMessage.from_langchain(chat, HumanMessage(content="tell me a story"))
    ChatMessage.from_langchain(chat, AIMessage(content="the cat sat on the mat"))

    chat.refresh_from_db()

    final_count = chat.chatmessage_set.count()

    assert final_count == initial_count + 2


@pytest.mark.django_db
def test_chat_annotated_content(chat_message):
    Citation.objects.create(
        chat_message=chat_message,
        text_in_answer="the cat",
        text_in_source="cats are nice",
        reference="www.catfacts.com",
        index=1,
    )

    assert (
        chat_message.annotated_content()
        == "the cat [1](www.catfacts.com 'cats are nice')  sat on the mat"
    )


@pytest.mark.django_db
def test_chat_annotated_content_no_citations(chat_message):
    assert chat_message.annotated_content() == "the cat sat on the mat"
