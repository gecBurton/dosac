import pytest
from django.urls import reverse

from core.models import Document, Chat


@pytest.mark.django_db
def test_document_detail(client, user_document: Document):
    client.force_login(user_document.user)
    url = reverse("document-detail", args=(user_document.pk, 1, 1))
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login(client, user, mailoutbox):
    url = reverse("login")
    login_response = client.post(url, data={"email": user.email})
    assert login_response.status_code == 302
    assert login_response.url == "/email-sent/"

    _, link = mailoutbox[-1].body.split(":", 1)
    magic_link_response = client.get(link.strip())
    assert magic_link_response.status_code == 302
    assert magic_link_response.url == "/"


@pytest.mark.django_db
def test_chat_new(client, user):
    client.force_login(user)
    url = reverse("chat-new")
    response = client.get(url)
    assert response.status_code == 302
    pk = response.url.strip("/")
    assert Chat.objects.filter(pk=pk).exists()
