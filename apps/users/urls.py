from django.urls import path, re_path

# isort: off
from .views import (
    UserDataCrud,
    UserDataFormView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
)

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="users-section"),
    path(
        "delete/<int:pk>",
        UserDeleteView.as_view(),
        name="delete-user",
    ),
    path(
        "upsert_user-form",
        UserDataFormView.as_view(),
        name="create-user-form",
    ),
    path(
        "upsert-form-user/<str:id>",
        UserDataFormView.as_view(
            modal_header="Update User",
            confirm_botton_text="Update User",
        ),
        name="update-user-form",
    ),
    path(
        "detail/<int:pk>",
        UserDetailView.as_view(),
        name="user-detail",
    ),
    path(
        "update/<int:pk>",
        UserUpdateView.as_view(),
        name="update-user",
    ),
]
