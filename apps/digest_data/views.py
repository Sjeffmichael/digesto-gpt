import mimetypes
import uuid
from typing import Any

# isort: off
from django.contrib.messages import add_message, constants as messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404, QueryDict
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    View,
)

from apps.digest_data.models import Law

# isort: off
from apps.digest_data.pydantic_models import (
    categories,
    ranks,
    statuses,
    subjects,
    administrator,
)
from components.user_data_form.user_data_form import UserDataForm
from components.law_data_form.law_data_form import LawDataForm
from common.util.locale import is_language_switcher_request


class DigestDataCrud(View):
    template_name = ""
    LIMIT_OPTIONS = [10, 25, 50, 100]
    DEFAULT_LIMIT = 10
    DEFAULT_PAGE = 1

    def get(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        context = self.get_context_data(
            query_set,
            int(request.GET.get("page", "1")),
            int(request.GET.get("limit", "10")),
            request.GET.get("search", ""),
        )

        if request.htmx and not is_language_switcher_request(request):
            self.template_name = "digest_data/digest_data_section.html"

        return render(request, self.template_name, context)

    def delete(self, request, *args, **kwargs):
        body_data = QueryDict(request.body)
        try:
            law = get_object_or_404(Law, pk=kwargs.get("pk", ""))
            law.delete()
            add_message(request, messages.SUCCESS, _("Law deleted successfully"))
        except Http404:
            add_message(request, messages.ERROR, _("Law not found"))

        query_set = self.get_queryset()

        context = self.get_context_data(
            query_set,
            int(body_data.get("page", "1")),
            int(body_data.get("limit", "10")),
            body_data.get("search", ""),
        )

        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        body_data = {key: value[0] for key, value in request.POST.lists()}
        print(f"Received body data: {body_data}, id: {id}")
        file = request.FILES.get("file")
        if id is not None and id != "":
            try:
                Law.objects.filter(id=id).update(
                    metadata=body_data.get("metadata", {}),
                )
                add_message(request, messages.SUCCESS, _("Law updated successfully"))
            except Exception as e:
                add_message(request, messages.ERROR, _("Error updating law"))
        else:
            try:
                new_law = Law(
                    id=str(uuid.uuid4()),
                    metadata=body_data.get("metadata", {}),
                    filename=file.name if file else "",
                )
                new_law.save()
                self.handle_uploaded_file(file, new_law.id)
                add_message(request, messages.SUCCESS, _("Law created successfully"))
            except Exception as e:
                print(f"Error creating law: {e}")
                add_message(request, messages.ERROR, _("Error creating law"))

        query_set = self.get_queryset()
        context = self.get_context_data(
            query_set,
            int(body_data.get("page", "1")),
            int(body_data.get("limit", "10")),
            body_data.get("search", ""),
        )

        return render(request, self.template_name, context)

    def get_queryset(self) -> QuerySet[Any]:
        search = self.request.GET.get("search", "")

        if search:
            return Law.objects.filter(
                Q(filename__icontains=search) | Q(metadata__icontains=search)
            ).order_by("-updated_at")
        return Law.objects.all().order_by("-updated_at")

    def get_context_data(self, queryset, page, limit, search):

        # Adjust pagination
        paginator = Paginator(queryset, limit)

        try:
            laws = paginator.page(page)
        except PageNotAnInteger:
            laws = paginator.page(self.DEFAULT_PAGE)
        except EmptyPage:
            laws = paginator.page(paginator.num_pages)

        laws.adjusted_elided_pages = paginator.get_elided_page_range(
            laws.number,
            on_each_side=1,
        )

        context = {
            "paginator": paginator,
            "page_obj": laws,
            "laws": laws,
            "limit": limit,
            "limit_options": self.LIMIT_OPTIONS,
            "statuses": statuses,
            "categories": categories,
            "ranks": ranks,
            "subjects": subjects,
            "administrator": administrator,
        }

        return context

    def handle_uploaded_file(self, f, id_):
        if f:
            extension = mimetypes.guess_extension(f.content_type) if f else ".html"
            new_filename = id_ + extension
            with open(
                f"apps/digest_data/files/laws/{new_filename}", "wb+"
            ) as destination:
                for chunk in f.chunks():
                    destination.write(chunk)


class DigestDataDetailView(DetailView):
    model = Law

    def render_to_response(self, context, **response_kwargs):
        return LawDataForm.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modal_context = {
            "modal_header": _("Update Law"),
            "confirm_botton_text": _("Update Law"),
            "csrf_token": get_token(self.request),
        }
        context.update(**modal_context)

        return context


class DigestDataForm(View):
    modal_header = ""
    confirm_botton_text = ""

    def get(self, request, id=None):

        return LawDataForm.render_to_response(
            context={
                "modal_header": _("Create Law"),
                "confirm_botton_text": _("Create Law"),
                "csrf_token": get_token(request),
            }
        )

    def get_queryset(self, id):
        law = Law.objects.get(pk=id)
        return law
