import uuid
from typing import Self

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.urls import reverse
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from pgvector.django import VectorField
from langchain_core.documents import Document as LangchainDocument

import requests

from django.contrib.auth.models import AbstractUser, UserManager


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

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("email address", blank=True, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CoreUserManager()


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["created_at"]


class Document(BaseModel):
    file = models.FileField(unique=True, upload_to="uploads")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name

    def generate_elements(self):
        headers = {
            "accept": "application/json",
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
            settings.UNSTRUCTURED_URL, headers=headers, files=files
        )
        response.raise_for_status()

        texts = [element_response["text"] for element_response in response.json()]

        metadatas = [
            element_response["metadata"] for element_response in response.json()
        ]

        embeddings: list[list[float]] = settings.EMBEDDING_MODEL.embed_documents(texts)

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


class Embedding(BaseModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    embedding = VectorField(dimensions=3072)
    text = models.TextField()
    index = models.PositiveIntegerField()
    metadata = models.JSONField()

    def get_uri(self):
        # {self.index}/
        return reverse(
            "document-detail-page",
            kwargs={
                "pk": self.document.pk,
                "page_number": self.metadata["page_number"],
            },
        )

    def to_langchain(self) -> LangchainDocument:
        return LangchainDocument(
            page_content=str(self.text),
            metadata=dict(self.metadata, index=self.index, url=self.get_uri()),
        )

    def __str__(self):
        return f"{self.document.file.name}.{self.index}"


class Chat(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if first_message := self.chatmessage_set.first():
            return first_message.content
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
        return f"{start} [{self.index}]({self.reference} {repr(self.text_in_source)}) {end}"