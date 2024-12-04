import pytest
import pytest_asyncio
from django.contrib.auth import get_user_model

from core.models import Chat, ChatMessage

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


@pytest_asyncio.fixture
async def auser():
    _user = await User.objects.acreate(email="whatever@somewhere.com")
    yield _user
    await _user.adelete()


@pytest_asyncio.fixture
async def achat(auser):
    _chat = await Chat.objects.acreate(user=auser)
    yield _chat
    await _chat.adelete()
