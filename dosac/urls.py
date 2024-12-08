from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core import views
from sesame.views import LoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(settings.AUTHENTICATION_URL, LoginView.as_view(), name="sesame-login"),
    path(
        "document/<uuid:pk>/page/<int:page_number>/index/<int:index>/",
        views.document_detail,
        name="document-detail",
    ),
    path("", views.chat_new, name="chat-new"),
    path("<uuid:pk>/", views.chat_detail, name="chat-detail"),
    path("login/", views.login, name="login"),
    path("email-sent/", views.email_sent, name="email-sent"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
