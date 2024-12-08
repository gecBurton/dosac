import math

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Chat, ChatMessage, Document, Embedding

User = get_user_model()

SQRT_2_PI = math.sqrt(2.0 * math.pi)


def gaussian(x: float, mu: float = 0, sigma: float = 1) -> float:
    numerator = math.exp(-math.pow((x - mu) / sigma, 2) / 2)
    denominator = SQRT_2_PI * sigma
    return numerator / denominator


@pytest.fixture
def user():
    _user = User.objects.create(email="whatever@somewhere.com")
    yield _user
    _user.delete()


@pytest.fixture
def chat(user):
    _chat = Chat.objects.create(user=user)
    yield _chat
    _chat.delete()


@pytest.fixture
def chat_message(chat):
    _message = ChatMessage.objects.create(
        chat=chat, content="the cat sat on the mat", type=ChatMessage.TYPES.AI
    )
    yield _message
    _message.delete()


@pytest.fixture
def user_document(user):
    document = Document.objects.create(
        user=user, file=SimpleUploadedFile(name="hello.txt", content=b"hello!")
    )
    yield document
    document.delete()


@pytest.fixture
def user_embedded_document(user_document):
    for index in range(10):
        Embedding.objects.create(
            document=user_document,
            text=f"example text #{index}",
            embedding=[gaussian(i, index) for i in range(3072)],
            index=index,
            metadata={"page_number": 1},
        )

    yield user_document


@pytest.fixture
def user_with_many_chat_messages(user):
    chats = [Chat.objects.create(user=user) for _ in range(10)]

    for i, chat in enumerate(chats):
        for m in range(0, i):
            ChatMessage.objects.create(
                chat=chat, type=ChatMessage.TYPES.HUMAN, content="hello"
            )

    yield user

    for chat in chats:
        chat.delete()
