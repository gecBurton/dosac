from smtplib import SMTPDataError
from uuid import UUID

from charset_normalizer.md import getLogger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django_q.tasks import async_task

from core.forms import LoginForm, UploadFileForm
from core.models import Document, Chat
from sesame.utils import get_query_string

logger = getLogger(__name__)
User = get_user_model()


@login_required
def document_detail(request, pk: UUID, page_number: int = 1):
    document = get_object_or_404(Document, pk=pk, user=request.user)
    elements = document.embedding_set.filter(metadata__page_number=page_number)
    context = {"document": document, "elements": elements, "page_number": page_number}
    return render(request, "core/document.html", context)


@login_required
def chat_new(request):
    instance = Chat.objects.create(user=request.user)
    return redirect("chat-detail", pk=instance.pk)


@login_required
def chat_detail(request, pk: UUID):
    error = None
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = Document.objects.create(
                    file=request.FILES["file"], user=request.user
                )
                async_task(document.generate_elements)

            except IntegrityError:
                error = "file with this name already exists"
        else:
            error = " ".join(form.errors)

    file_upload_form = UploadFileForm()
    chat = get_object_or_404(Chat, pk=pk, user=request.user)

    chat_history = (
        Chat.objects.annotate(message_count=Count("chatmessage"))
        .filter(user=request.user, message_count__gte=1)
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "core/chat.html",
        {
            "chat": chat,
            "chat_history": chat_history,
            "scheme": settings.WEBSOCKET_SCHEME,
            "file_upload_form": file_upload_form,
            "error": error,
        },
    )


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                host = request.get_host()
                token = get_query_string(user)
                magic_link = f"{settings.HTTP_SCHEME}://{host}/{settings.AUTHENTICATION_URL}{token}"
                message = f"click here to login: {magic_link}"
                send_mail("dosac login", message, settings.EMAIL_HOST_USER, [email])
                logger.info(message)
            except User.DoesNotExist:
                logger.warn(f"user={email} does not exist")
            except SMTPDataError as e:
                logger.error(f"failed to send email to user={email}: {e}")
            return HttpResponseRedirect("/email-sent/")

    form = LoginForm()
    return render(request, "core/login.html", {"login_form": form})


def email_sent(request):
    return render(request, "core/email_sent.html")
