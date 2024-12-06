import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Chat, ChatMessage, Document

User = get_user_model()


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
