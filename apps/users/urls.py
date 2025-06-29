from django.urls import path, re_path

# isort: off
from .views import (
    UserDataCrud,
    UserDataFormView,
    UserDeleteView,
    UserDetailView,
    UserListView,
)

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="users-section"),
    # path(
    #     "",
    #     UserDataCrud.as_view(template_name="user/users_full.html"),
    #     name="users-section",
    # ),
    # path(
    #     "table",
    #     UserDataCrud.as_view(template_name="users/users_table.html"),
    #     name="users/table",
    # ),
    # path(
    #     "delete/<pk>",
    #     UserDataCrud.as_view(template_name="users/users_table.html"),
    #     name="delete-user",
    # ),
    path(
        "delete/<int:pk>",
        UserDeleteView.as_view(),
        name="delete-user",
    ),
    # re_path(
    #     r"^upsert(?:/(?P<id>\d+))?$",
    #     UserDataCrud.as_view(template_name="users/users_table.html"),
    #     name="upsert-user",
    # ),
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
]
