from django.urls import path, re_path

from .views import DigestDataCrud, DigestDataForm

urlpatterns = [
    path(
        "laws/",
        DigestDataCrud.as_view(template_name="digest_data/digest_data_list.html"),
        name="laws",
    ),
    path(
        "laws/table",
        DigestDataCrud.as_view(template_name="partials/table.html"),
        name="laws/table",
    ),
    path(
        "laws/delete/<pk>",
        DigestDataCrud.as_view(template_name="partials/table.html"),
        name="delete-law",
    ),
    re_path(
        r"^laws/upsert(?:/(?P<id>\d+))?$",
        DigestDataCrud.as_view(template_name="partials/table.html"),
        name="upsert-law",
    ),
    path(
        "laws/upsert-form",
        DigestDataForm.as_view(
            modal_header="Create New Law",
            confirm_botton_text="Create Law",
        ),
        name="create-law-form",
    ),
    path(
        "laws/upsert-form/<str:id>",
        DigestDataForm.as_view(
            modal_header="Update Law",
            confirm_botton_text="Update Law",
        ),
        name="update-law-form",
    ),
]
