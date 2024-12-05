from uuid import UUID

from charset_normalizer.md import getLogger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect

from core.forms import LoginForm
from core.models import Document, Chat
from sesame.utils import get_query_string

logger = getLogger(__name__)
User = get_user_model()


@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user)
    context = {"documents": documents}
    return render(request, "core/document-list.html", context)


@login_required
def document_detail(request, pk: UUID, page_number: int = 1):
    document = get_object_or_404(Document, pk=pk, user=request.user)
    elements = document.embedding_set.filter(metadata__page_number=page_number)
    context = {"document": document, "elements": elements, "page_number": page_number}
    return render(request, "core/page.html", context)


@login_required
def chat_new(request):
    instance = Chat.objects.create(user=request.user)
    return redirect("chat-detail", pk=instance.pk)


@login_required
def chat_detail(request, pk: UUID):
    chat = get_object_or_404(Chat, pk=pk, user=request.user)

    chat_history = Chat.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "core/chat.html",
        {
            "chat": chat,
            "chat_history": chat_history,
            "scheme": settings.WEBSOCKET_SCHEME,
        },
    )


def magic(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                message = f"click here to login: {request.get_host()}{settings.LOGIN_URL}{get_query_string(user)}"
                _, domain = settings.EMAIL_HOST_USER.split("@")
                send_mail("dosac login", message, f"no-reply@{domain}", [email])
                logger.info(message)
            except User.DoesNotExist:
                logger.warn(f"user={email} does not exist")
            return HttpResponseRedirect("/email-sent/")

    form = LoginForm()
    return render(request, "core/login.html", {"login_form": form})


def email_sent(request):
    return render(request, "core/email_sent.html")
