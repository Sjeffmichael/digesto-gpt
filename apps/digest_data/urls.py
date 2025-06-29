from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _

from .views import DigestDataCrud, DigestDataDetailView, DigestDataForm

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
    path(
        "detail/<str:pk>",
        DigestDataDetailView.as_view(),
        name="detail-law",
    ),
]
