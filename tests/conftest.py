import math
import os

import pytest
import pytest_asyncio
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from langchain_core.language_models import GenericFakeChatModel

from core.models import Chat, ChatMessage, Document, Embedding

User = get_user_model()

SQRT_2_PI = math.sqrt(2.0 * math.pi)


def gaussian(x: float, mu: float = 0, sigma: float = 1) -> float:
    numerator = math.exp(-math.pow((x - mu) / sigma, 2) / 2)
    denominator = SQRT_2_PI * sigma
    return numerator / denominator


@pytest.fixture
def fake_embeddings():
    os.environ["FAKE_API_KEY"] = "n dm"
    yield


@pytest.fixture
def user():
    _user = User.objects.create(email="whatever@somewhere.com")
    yield _user
    _user.delete()


@pytest_asyncio.fixture
async def async_user():
    _user = await User.objects.acreate(email="whatever@somewhere.com")
    yield _user
    await _user.adelete()


@pytest.fixture
def chat(user):
    _chat = Chat.objects.create(user=user)
    yield _chat
    _chat.delete()


@pytest_asyncio.fixture
async def async_chat(async_user):
    _chat = await Chat.objects.acreate(user=async_user)
    yield _chat
    await _chat.adelete()


@pytest.fixture
def chat_message(chat):
    _message = ChatMessage.objects.create(
        chat=chat, content="the cat sat on the mat", type=ChatMessage.TYPES.AI
    )
    yield _message
    _message.delete()


@pytest.fixture
def file():
    yield SimpleUploadedFile(name="hello.txt", content=b"hello!")


@pytest.fixture
def user_document(user, file):
    document = Document.objects.create(user=user, file=file)
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


@pytest.fixture
def user_with_many_documents(user):
    documents = [
        Document.objects.create(
            user=user, file=SimpleUploadedFile(name=f"hello_{i}.txt", content=b"hello!")
        )
        for i in range(10)
    ]
    yield user
    for document in documents:
        document.delete()


class FakeChatModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self
