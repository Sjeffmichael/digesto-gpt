from django.urls import path

from .views import UserListView

app_name = "users"

urlpatterns = [path("users/", UserListView.as_view(), name="users")]
