from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("document/", views.document_list, name="document-list"),
    path("document/<uuid:pk>/", views.document_detail, name="document-detail"),
    path(
        "document/<uuid:pk>/page/<int:page_number>/",
        views.document_detail,
        name="document-detail-page",
    ),
    path("chat/", views.chat_new, name="chat-new"),
    path("chat/<uuid:pk>/", views.chat_detail, name="chat-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
