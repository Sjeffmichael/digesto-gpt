from django.urls import path

from .views import Chats, MessagesListView

app_name = "chats"

urlpatterns = [
    path(
        "",
        Chats.as_view(),
        name="chat-section",
    ),
    path(
        "<str:slug>",
        MessagesListView.as_view(),
        name="conversation",
    ),
]
