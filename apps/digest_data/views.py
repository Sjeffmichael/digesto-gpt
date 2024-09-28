import mimetypes
import uuid
from typing import Any

from django.contrib.messages import add_message, constants as messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.query import QuerySet
from django.http import Http404, QueryDict
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from apps.digest_data.models import Law

# isort: off
from apps.digest_data.pydantic_models import (
    LawData,
    LawDataFormContext,
    LawDataTable,
    LawMetadata,
    categories,
    ranks,
    statuses,
    subjects,
)
from components.law_data_form.law_data_form import LawDataForm


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
        )

        if request.htmx:
            self.template_name = "digest_data/digest_data_section.html"

        return render(request, self.template_name, context)

    def delete(self, request, *args, **kwargs):
        body_data = QueryDict(request.body)
        try:
            law = get_object_or_404(Law, pk=kwargs.get("pk", ""))
            law.delete()
            add_message(request, messages.SUCCESS, "Law deleted successfully")
        except Http404:
            add_message(request, messages.ERROR, "Law not found")

        query_set = self.get_queryset()

        context = self.get_context_data(
            query_set,
            int(body_data.get("page", "1")),
            int(body_data.get("limit", "10")),
        )

        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        body_data = {key: value[0] for key, value in request.POST.lists()}
        file = request.FILES.get("file")
        if id is not None:
            try:
                law_data = LawData(
                    id=id,
                    filename=file.name,
                    metadata=LawMetadata.model_construct(
                        **body_data,
                    ),
                )
                Law.objects.filter(id=law_data.id).update(
                    metadata=law_data.metadata.model_dump(
                        by_alias=True, exclude_none=True
                    ),
                    filename=law_data.filename,
                )
                add_message(request, messages.ERROR, "Law updated successfully")
            except Exception as e:
                add_message(request, messages.ERROR, "Error updating law")
        else:
            try:
                law_data = LawData(
                    id=str(uuid.uuid4()),
                    filename=file.name,
                    metadata=LawMetadata.model_construct(
                        **body_data,
                    ),
                )
                new_law = Law(
                    id=law_data.id,
                    metadata=law_data.metadata.model_dump(
                        by_alias=True, exclude_none=True
                    ),
                    filename=law_data.filename,
                )
                new_law.save()
                self.handle_uploaded_file(file, law_data.id)
                add_message(request, messages.SUCCESS, "Law created successfully")
            except Exception as e:
                add_message(request, messages.ERROR, "Error creating law")

        query_set = self.get_queryset()
        context = self.get_context_data(
            query_set,
            int(body_data.get("page", "1")),
            int(body_data.get("limit", "10")),
        )

        return render(request, self.template_name, context)

    def get_queryset(self) -> QuerySet[Any]:
        query_set = Law.objects.all()

        laws_data = []
        for law in query_set:
            laws_data.append(
                LawDataTable(
                    id=law.id,
                    title=law.metadata.get("norma_titulo"),
                    publication_date=law.metadata.get("norma_fecha_publicacion"),
                    status=law.metadata.get("norma_estado"),
                )
            )

        return laws_data

    def get_context_data(self, queryset, page, limit):

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
        }

        return context

    def handle_uploaded_file(self, f, id_):
        extension = mimetypes.guess_extension(f.content_type)
        new_filename = id_ + extension
        with open(f"apps/digest_data/files/laws/{new_filename}", "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)


class DigestDataForm(View):
    modal_header = ""
    confirm_botton_text = ""

    def get(self, request, id=None):
        queryset = None
        if id is not None:
            queryset = self.get_queryset(id)

        context = self.get_context_data(queryset, request)

        return LawDataForm.render_to_response(kwargs={"data_context": context})

    def get_queryset(self, id):
        law = Law.objects.get(pk=id)
        return law

    def get_context_data(self, queryset: Law, request):
        csrf_token = get_token(request)
        law_data = None
        if queryset is not None:
            law_data = LawData(
                id=queryset.id,
                filename=queryset.filename,
                metadata=LawMetadata(**queryset.metadata),
            )

        context = LawDataFormContext(
            modal_header=self.modal_header,
            csrf_token=csrf_token,
            confirm_botton_text=self.confirm_botton_text,
            statuses=statuses,
            categories=categories,
            ranks=ranks,
            subjects=subjects,
            law_data=law_data,
        )

        return context
