from django.urls import path, re_path

from .views import DigestDataCrud, DigestDataForm

urlpatterns = [
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
            modal_header="Create New Law",
            confirm_botton_text="Create Law",
        ),
        name="create-law-form",
    ),
    path(
        "upsert-form/<str:id>",
        DigestDataForm.as_view(
            modal_header="Update Law",
            confirm_botton_text="Update Law",
        ),
        name="update-law-form",
    ),
]
