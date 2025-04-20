import mimetypes
import uuid
from typing import Any

from django.contrib.messages import add_message, constants as messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.query import QuerySet
from django.http import Http404, QueryDict
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from apps.digest_data.models import Law
from apps.user_authentication.models import User

# isort: off
from apps.digest_data.pydantic_models import (
    LawData,
    LawDataFormContext,
    LawDataTable,
    LawMetadata,
    UserDataFormContext,
    UserData,
    UserDataTable,
    UserMetadata,
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
        )

        if request.htmx and not is_language_switcher_request(request):
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
            "administrator": administrator,
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

        print(type(self.modal_header), type(self.confirm_botton_text))

        context = LawDataFormContext(
            modal_header=str(self.modal_header),
            csrf_token=csrf_token,
            confirm_botton_text=str(self.confirm_botton_text),
            statuses=statuses,
            categories=categories,
            ranks=ranks,
            subjects=subjects,
            law_data=law_data,
            administrator=administrator,
        )

        return context
    
class DigestDataUserForm(View):
    modal_header = ""
    confirm_botton_text = ""

    def get(self, request, id=None):
        print(f"El id recibido en la petición es: {id}")  # Imprimir el id recibido
        queryset = None
        if id is not None:
            queryset = self.get_queryset(id)
        
        if queryset is not None:
            self.modal_header = "Update User"
            self.confirm_botton_text = "Update User"
        else:
            self.modal_header = "Create New User"
            self.confirm_botton_text = "Create User"

        context = self.get_context_data(queryset, request)

        return UserDataForm.render_to_response(kwargs={"data_context": context})

    def get_queryset(self, id):
        print(f"Buscando usuario con id: {id}")  # Agregar un print aquí
        try:
            user = User.objects.get(pk=id)
            print(f"Usuario encontrado: {user}")  # También imprimir el objeto usuario encontrado
            return user
        except User.DoesNotExist:
            print(f"Usuario con id {id} no encontrado.")  # En caso de no encontrar al usuario
            return None

    def get_context_data(self, queryset: User, request):
        csrf_token = get_token(request)
        user_data = None
        if queryset is not None:
            user_data = UserData(
                id=queryset.id,
                email=queryset.email,
                first_name=queryset.first_name,
                last_name=queryset.last_name,
                is_active=queryset.is_active,
                is_admin=queryset.is_admin,
            )

            print(f"Datos del usuario encontrado: ID={user_data.id}, Email={user_data.email}, "
              f"First Name={user_data.first_name}, Last Name={user_data.last_name}, "
              f"Active={user_data.is_active}, Admin={user_data.is_admin}")

        context = UserDataFormContext(
            modal_header=str(self.modal_header),
            csrf_token=csrf_token,
            confirm_botton_text=str(self.confirm_botton_text),
            statuses=statuses,
            categories=categories,
            ranks=ranks,
            subjects=subjects,
            user_data=user_data,
            administrator=administrator,
        )

        return context

class DigestUserDataCrud(View):
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

        if request.htmx and not is_language_switcher_request(request):
            self.template_name = "users/users_section.html"

        return render(request, self.template_name, context)
    
    def delete(self, request, *args, **kwargs):
        body_data = QueryDict(request.body)
        try:
            user = get_object_or_404(User, pk=kwargs.get("pk", ""))
            user.delete()
            add_message(request, messages.SUCCESS, "User deleted successfully")
        except Http404:
            add_message(request, messages.ERROR, "User not found")

        query_set = self.get_queryset()

        context = self.get_context_data(
            query_set,
            int(body_data.get("page", "1")),
            int(body_data.get("limit", "10")),
        )

        return render(request, self.template_name, context)

    def post(self, request, id=None, *args, **kwargs):
        body_data = {key: value[0] for key, value in request.POST.lists()}
        if id is not None:
            try:
                User.objects.filter(id=id).update(
                    email=body_data.get("email"),
                    first_name=body_data.get("first_name"),
                    last_name=body_data.get("last_name"),
                    is_active=body_data.get("is_active") == "1",
                    is_admin=body_data.get("is_admin") == "1",
                    username=body_data.get("username"),
                )
                add_message(request, messages.SUCCESS, "User updated successfully")
                print(f"User updated: {body_data}")  # Imprimir datos de usuario actualizado
            except Exception as e:
                add_message(request, messages.ERROR, f"Error updating user: {e}")
                print(f"Error updating user: {e}")
        else:
            try:
                # Crear nuevo usuario
                new_user = User(
                    email=body_data.get("email"),
                    first_name=body_data.get("first_name"),
                    last_name=body_data.get("last_name"),
                    is_active=body_data.get("is_active") == "1",
                    is_admin=body_data.get("is_admin") == "1",
                    username=body_data.get("username"),
                    password=body_data.get("password"),
                    date_joined=timezone.now(),
                )
                new_user.save()
                add_message(request, messages.SUCCESS, "User created successfully")

                # Imprimir los datos del nuevo usuario
                print(f"User created: ID={new_user.id}, Username={new_user.username}, Email={new_user.email}, "
                    f"First Name={new_user.first_name}, Last Name={new_user.last_name}, Active={new_user.is_active}, "
                    f"Admin={new_user.is_admin}, Date Joined={new_user.date_joined}")

            except Exception as e:
                add_message(request, messages.ERROR, f"Error creating user: {e}")
                print(f"Error creating user: {e}")

        query_set = self.get_queryset()
        context = self.get_context_data(
            query_set,
            int(body_data.get("page", "1")),
            int(body_data.get("limit", "10")),
        )

        return render(request, self.template_name, context)

    
    def get_queryset(self) -> QuerySet[Any]:
        query_set = User.objects.all()

        user_data = []
        for user in query_set:
            user_data.append(
                UserDataTable(
                    id = user.id,
                    password = user.metadata.get("user_password`"),
                    last_login = user.metadata.get("last_login"),
                    super_user = user.metadata.get("super_user"),
                    name = user.metadata.get("user_name"),
                    firstname = user.metadata.get("user_firstname"),
                    lastname = user.metadata.get("user_lastname"),
                    date_joined = user.metadata.get("date_joined"),
                    email = user.metadata.get("user_email"),
                    active = user.metadata.get("user_active"),
                    administrator = user.metadata.get("administrator"),
                )
            )

        return user_data
    
    def get_context_data(self, queryset, page, limit):

        # Adjust pagination
        paginator = Paginator(queryset, limit)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(self.DEFAULT_PAGE)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        users.adjusted_elided_pages = paginator.get_elided_page_range(
            users.number,
            on_each_side=1,
        )

        context = {
            "paginator": paginator,
            "page_obj": users,
            "users": users,
            "limit": limit,
            "limit_options": self.LIMIT_OPTIONS,
            "statuses": statuses,
            "categories": categories,
            "ranks": ranks,
            "subjects": subjects,
            "administrator": administrator,
        }

        return context