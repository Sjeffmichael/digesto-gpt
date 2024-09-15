from django.urls import path

from .views import UserChats

app_name = "chats"

urlpatterns = [
    path("", UserChats.as_view(), name="index"),
]
