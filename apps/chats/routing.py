from django.urls import path

from . import consumer

app_name = "chats"
websocket_urlpatterns = [
    path(r"ws/chat/", consumer.ChatConsumer.as_asgi(), name="ws-chat")
]
