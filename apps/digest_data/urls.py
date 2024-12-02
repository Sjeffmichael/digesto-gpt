from django.urls import path, re_path

from .views import DigestDataCrud, DigestDataForm, DigestUserDataForm

urlpatterns = [
    path(
        "",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_full.html"),
        name="laws-section",
    ),
    path(
        "",
        DigestUserDataForm.as_view(template_name="user/users_full.html"),
        name="users-section",
    ),
    path(
        "table",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_table.html"),
        name="laws/table",
    ),
    path(
        "table",
        DigestUserDataForm.as_view(template_name="users/users_table.html"),
        name="users/table",
    ),
    path(
        "delete/<pk>",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_table.html"),
        name="delete-law",
    ),
    path(
        "delete/<pk>",
        DigestUserDataForm.as_view(template_name="users/users_table.html"),
        name="delete-user",
    ),
    re_path(
        r"^upsert(?:/(?P<id>\d+))?$",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_table.html"),
        name="upsert-law",
    ),
    re_path(
        r"^upsert(?:/(?P<id>\d+))?$",
        DigestUserDataForm.as_view(template_name="users/users_table.html"),
        name="upsert-user",
    ),
    path(
        "upsert-form",
        DigestDataForm.as_view(
            modal_header="Create New Law",
            confirm_botton_text="Create Law",
        ),
        name="create-law-form",
    ),
    path(
        "upsert_user-form",
        DigestUserDataForm.as_view(
            modal_header="Create New User",
            confirm_botton_text="Create User",
        ),
        name="create-user-form",
    ),
    path(
        "upsert-form/<str:id>",
        DigestDataForm.as_view(
            modal_header="Update Law",
            confirm_botton_text="Update Law",
        ),
        name="update-law-form",
    ),
    path(
        "upsert-form/<str:id>",
        DigestUserDataForm.as_view(
            modal_header="Update User",
            confirm_botton_text="Update User",
        ),
        name="update-user-form",
    ),
]
