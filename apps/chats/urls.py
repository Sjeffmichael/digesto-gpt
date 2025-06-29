from django.urls import path

from .views import Chats, ConversationDeleteView, MessagesListView, UpdateView

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
    path(
        "edit-title/<str:slug>",
        UpdateView.as_view(),
        name="conversation-edit-title",
    ),
    path(
        "delete/<str:slug>",
        ConversationDeleteView.as_view(),
        name="conversation-delete",
    ),
]
