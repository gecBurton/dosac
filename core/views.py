from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from core.models import Document, Chat


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
