import textwrap
import uuid
from logging import getLogger
from typing import Self, Literal

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import Count
from django.urls import reverse
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from pgvector.django import VectorField, CosineDistance
from langchain_core.documents import Document as LangchainDocument

import requests

from django.contrib.auth.models import AbstractUser, UserManager

from core.ai_core import get_embedding_model


logger = getLogger(__name__)


class CoreUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None):
        return self._create_user(email, password, is_staff=True, is_superuser=True)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["created_at"]


class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField("email address", blank=True, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CoreUserManager()

    def get_history(self, limit: int = 10):
        _history = (
            Chat.objects.annotate(message_count=Count("chatmessage"))
            .filter(user=self, message_count__gte=1)
            .order_by("-created_at")[:limit]
        )
        return _history


class Document(BaseModel):
    file = models.FileField(unique=True, upload_to="uploads")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    processing_error = models.TextField(
        blank=True, null=True, help_text="error encountered during processing"
    )

    @property
    def status(self) -> Literal["ERROR", "COMPLETE", "PROCESSING"]:
        if self.processing_error is not None:
            return "ERROR"
        if self.embedding_set.exists():
            return "COMPLETE"
        return "PROCESSING"

    def __str__(self):
        return self.file.name

    def generate_elements(self):
        try:
            self._generate_elements()
            self.processing_error = None
        except Exception as e:
            self.processing_error = str(e)
        self.save()

    def _generate_elements(self):
        headers = {
            "accept": "application/json",
            "unstructured-api-key": settings.UNSTRUCTURED_API_KEY,
        }

        files = {
            "pdf_infer_table_structure": (None, "true"),
            "max_characters": (None, "1500"),
            "combine_under_n_chars": (None, "500"),
            "strategy": (None, "fast"),
            "files": (
                self.file.name,
                self.file.open("rb"),
            ),
            "chunking_strategy": (None, "by_title"),
        }

        response = requests.post(
            settings.UNSTRUCTURED_API_URL, headers=headers, files=files
        )
        response.raise_for_status()

        texts = [element_response["text"] for element_response in response.json()]

        metadatas = [
            element_response["metadata"] for element_response in response.json()
        ]

        embeddings: list[list[float]] = get_embedding_model().embed_documents(texts)

        for i, (text, embedding, metadata) in enumerate(
            zip(texts, embeddings, metadatas)
        ):
            Embedding.objects.create(
                document=self,
                embedding=embedding,
                text=text,
                index=i,
                metadata=metadata,
            )

    @classmethod
    def delete_by_name(cls, user_id: uuid.UUID, exact_document_name: str) -> bool:
        try:
            cls.objects.get(user_id=user_id, file=exact_document_name).delete()
        except cls.DoesNotExist:
            return False
        return True


class Embedding(BaseModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    embedding = VectorField(dimensions=3072)
    text = models.TextField()
    index = models.PositiveIntegerField()
    metadata = models.JSONField()

    def get_uri(self):
        return reverse(
            "embedding-detail",
            kwargs={
                "pk": self.pk,
            },
        )

    def to_langchain(self) -> LangchainDocument:
        return LangchainDocument(
            page_content=str(self.text),
            metadata=dict(url=self.get_uri(), index=self.index),
        )

    @classmethod
    def search_by_vector(
        cls, user_id: uuid.UUID, embedded_query: list[float], top_k_results: int = 3
    ) -> list:
        results = (
            cls.objects.filter(document__user_id=user_id)
            .annotate(distance=CosineDistance("embedding", embedded_query))
            .order_by("distance")[:top_k_results]
        )
        return [result.to_langchain() for result in results]

    def __str__(self):
        return f"{self.document.file.name}.{self.index}"


class Chat(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if first_message := self.chatmessage_set.first():
            return textwrap.shorten(first_message.content, 80, placeholder="...")
        return "..."

    def to_langchain(self) -> list[AnyMessage]:
        messages = [
            chat_message.to_langchain() for chat_message in self.chatmessage_set.all()
        ]
        return messages


class ChatMessage(BaseModel):
    class TYPES(models.TextChoices):
        HUMAN = "human"
        AI = "ai"
        CHAT = "chat"

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    type = models.CharField(choices=TYPES)

    @classmethod
    def from_langchain(cls, chat, message: AnyMessage) -> Self:
        instance = cls.objects.create(
            chat=chat, content=message.content, type=message.type
        )
        return instance

    def to_langchain(self) -> AnyMessage:
        if self.type == self.TYPES.AI:
            return AIMessage(content=str(self.content))
        if self.type == self.TYPES.HUMAN:
            return HumanMessage(content=str(self.content))
        raise NotImplementedError

    def annotated_content(self) -> str:
        content = str(self.content)

        for citation in self.citation_set.all():
            try:
                content = citation.generate_footnote(content)
            except ValueError:
                pass

        return content

    def __str__(self):
        return textwrap.shorten(self.content, 64, placeholder="...")


class Citation(models.Model):
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    text_in_answer = models.TextField(
        help_text="Exact part of text from `answer` that references a source, include formatting."
    )
    text_in_source = models.TextField(
        help_text="Exact part of text from `source` that supports the `answer`"
    )
    reference = models.TextField(
        help_text="reference to the source, could be a file-name, url or uri"
    )
    index = models.PositiveIntegerField()

    def generate_footnote(self, content: str) -> str:
        index = content.index(self.text_in_answer) + len(self.text_in_answer)
        start = content[:index]
        end = content[index:]
        return f'{start}[^{self.index}]{end}\n\n[^{self.index}]: "{repr(self.text_in_source)[1:-1]}" [source]({self.reference})'
