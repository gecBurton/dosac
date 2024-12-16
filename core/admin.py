from django.contrib import admin

from core.models import Document, Embedding, Chat, ChatMessage, Citation


class EmbeddingInline(admin.StackedInline):
    model = Embedding
    extra = 0
    ordering = ["index"]


class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "status"]
    exclude = ["embeddings"]
    inlines = [EmbeddingInline]


class MessageAdmin(admin.StackedInline):
    model = ChatMessage
    extra = 0
    ordering = ["created_at"]


class ChatAdmin(admin.ModelAdmin):
    inlines = [MessageAdmin]


class CitationAdmin(admin.ModelAdmin):
    list_display = ["id", "chat_message", "reference"]


admin.site.register(Citation, CitationAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Document, DocumentAdmin)
