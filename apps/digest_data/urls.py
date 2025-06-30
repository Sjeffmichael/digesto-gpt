from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _

from .views import DigestDataCrud, DigestDataForm, DigestDataUserForm, DigestUserDataCrud

urlpatterns = [
    # --- Leyes (Laws) ---
    path(
        "",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_full.html"),
        name="laws-section",
    ),
    path(
        "table",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_table.html"),
        name="laws/table",
    ),
    path(
        "delete/<pk>",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_table.html"),
        name="delete-law",
    ),
    re_path(
        r"^upsert(?:/(?P<id>\d+))?$",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_table.html"),
        name="upsert-law",
    ),
    path(
        "upsert-form",
        DigestDataForm.as_view(
            modal_header=_("Create Law"),
            confirm_botton_text=_("Create Law"),
        ),
        name="create-law-form",
    ),
    path(
        "upsert-form/<str:id>",
        DigestDataForm.as_view(
            modal_header=_("Update Law"),
            confirm_botton_text=_("Update Law"),
        ),
        name="update-law-form",
    ),

    # --- Usuarios (Users) ---
    path(
        "",
        DigestUserDataCrud.as_view(template_name="user/users_full.html"),
        name="users-section",
    ),
    path(
        "table",
        DigestUserDataCrud.as_view(template_name="users/users_table.html"),
        name="users/table",
    ),
    path(
        "delete/<pk>",
        DigestUserDataCrud.as_view(template_name="users/users_table.html"),
        name="delete-user",
    ),
    re_path(
        r"^upsertuser(?:/(?P<id>\d+))?$",
        DigestUserDataCrud.as_view(template_name="users/users_table.html"),
        name="upsert-user",
    ),
    path(
        "upsert_user-form",
        DigestDataUserForm.as_view(
            modal_header="Create User",
            confirm_botton_text="Create User"
        ),
        name="create-user-form",
    ),
    path(
        "upsert-form-user/<str:id>",
        DigestDataUserForm.as_view(
            modal_header="Update User",
            confirm_botton_text="Update User",
        ),
        name="update-user-form",
    ),
]
