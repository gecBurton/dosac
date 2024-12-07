from django.contrib import admin

from core.models import Document, Embedding, Chat, ChatMessage, Citation


class EmbeddingInline(admin.StackedInline):
    model = Embedding
    extra = 0
    exclude = ["embedding", "metadata"]
    ordering = ["index"]


@admin.action(description="Extract Text from Documents")
def generate_elements(modeladmin, request, queryset):
    for document in queryset.all():
        document.generate_elements()


class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "status"]
    exclude = ["embeddings"]
    actions = [generate_elements]
    inlines = [EmbeddingInline]


class MessageAdmin(admin.StackedInline):
    model = ChatMessage
    extra = 0
    ordering = ["created_at"]


class ChatAdmin(admin.ModelAdmin):
    inlines = [MessageAdmin]


class CitationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Citation, CitationAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Document, DocumentAdmin)
