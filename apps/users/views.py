from typing import Any

from django.http.response import HttpResponse as HttpResponse

# isort: off
from django.views.generic import ListView, UpdateView, DetailView, DeleteView

from apps.user_authentication.models import User

from django.contrib.messages import add_message, constants as messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.query import QuerySet
from django.http import Http404, QueryDict
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.db.models import Q

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
from common.util.views import PaginationMixin


class SearchMixin:

    def get_search_queryset(self):
        filters = (
            Q(email__icontains=self.request.GET.get("search", ""))
            & (
                (
                    Q(is_active=True)
                    if self.request.GET.get("activeStatus") == "true"
                    else Q()
                )
                | (
                    Q(is_active=False)
                    if self.request.GET.get("inactiveStatus") == "true"
                    else Q()
                )
            )
            & (
                (
                    Q(is_admin=True)
                    if self.request.GET.get("adminRole") == "true"
                    else Q()
                )
                | (
                    Q(is_admin=False)
                    if self.request.GET.get("chatbotUserRole") == "true"
                    else Q()
                )
            )
        )

        return self.model._default_manager.filter(filters)


class UserListView(ListView, SearchMixin, PaginationMixin):
    content_object_name = "users"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(**self.get_pagination_data())
        return context

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if self.request.htmx and not is_language_switcher_request(self.request):
            template_name = "users/users_section.html"
        else:
            template_name = "users/users_full.html"

        return self.response_class(
            request=self.request,
            template=template_name,
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )

    def delete(self, *args, **kwargs):
        return self.render_to_response(*args, **kwargs)


class UserUpdateView(UpdateView, SearchMixin, PaginationMixin):
    model = User
    template_name = "users/users_section.html"
    form_class = UserDataForm

    def get_context_data(self, **kwargs):

        return self.get_pagination_data()

    def patch(self, request, *args, **kwargs):
        body_data = QueryDict(request.body)
        status = body_data.get("status")
        role = body_data.get("role", "chatbot_user")
        self.object = self.get_object()

        self.object.is_active = status == "true"
        self.object.is_admin = role == "Admin"
        self.object.save()

        # add_message(request, messages.SUCCESS, _("User updated successfully"))
        add_message(request, messages.SUCCESS, _("Usuario actualizado correctamente"))

        # if not self.object.is_active:
        #     add_message(request, messages.ERROR, _("User already inactive"))
        # else:
        #     self.object.is_active = False
        #     self.object.save()  # Soft delete by setting is_active to False
        #     add_message(request, messages.SUCCESS, _("User deactivated successfully"))

        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=self.get_context_data(),
            using=self.template_engine,
        )


class UserDetailView(DetailView):
    model = User

    def render_to_response(self, context):
        context.update(**{"csrf_token": get_token(self.request)})
        return UserDataForm.render_to_response(context)


class UserDeleteView(DeleteView, SearchMixin, PaginationMixin):
    model = User
    template_name = "users/users_section.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(**self.get_pagination_data())
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.is_active:
            add_message(request, messages.ERROR, _("User already inactive"))
        else:
            self.object.is_active = False
            self.object.save()  # Soft delete by setting is_active to False
            add_message(request, messages.SUCCESS, _("User deactivated successfully"))

        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=self.get_context_data(),
            using=self.template_engine,
        )
        # print("entro")
        # factory = RequestFactory()
        # new_request = factory.get(request.path, data=request.GET.dict())
        # new_request.user = request.user
        # new_request.session = request.session
        # list_view = UserListView.as_view()
        # return list_view(request)


# Create your views here.
# class UserListView(ListView):
#     content_object_name = "users"
#     model = User
#     paginate_by = 10
#     LIMIT_OPTIONS = ["10", "25", "50", "100"]

#     def get_paginate_by(self, queryset):
#         return self.request.GET.get("limit")  or self.paginate_by

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         page = context.get("page_obj")
#         paginator = context.get("paginator")
#         page.adjusted_elided_pages  = paginator.get_elided_page_range(
#             page.number,
#             on_each_side=1,
#         )

#         context.update(**{"limit_options": self.LIMIT_OPTIONS, "page": page})

#         return context

#     def render_to_response(
#         self, context: dict[str, Any], **response_kwargs: Any
#     ) -> HttpResponse:
#         if self.request.htmx and not is_language_switcher_request(self.request):
#             template_name = "users/users_section.html"
#         else:
#             template_name = "users/users_full.html"

#         return self.response_class(
#             request=self.request,
#             template=template_name,
#             context=context,
#             using=self.template_engine,
#             **response_kwargs,
#         )


class UserDataFormView(View):
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
            print(
                f"Usuario encontrado: {user}"
            )  # También imprimir el objeto usuario encontrado
            return user
        except User.DoesNotExist:
            print(
                f"Usuario con id {id} no encontrado."
            )  # En caso de no encontrar al usuario
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


class UserDataCrud(View):
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
                print(
                    f"User updated: {body_data}"
                )  # Imprimir datos de usuario actualizado
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
                    # date_joined=timezone.now(),
                )
                new_user.save()
                add_message(request, messages.SUCCESS, "User created successfully")

            except Exception as e:
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
                    id=user.id,
                    password=user.metadata.get("user_password`"),
                    last_login=user.metadata.get("last_login"),
                    super_user=user.metadata.get("super_user"),
                    name=user.metadata.get("user_name"),
                    firstname=user.metadata.get("user_firstname"),
                    lastname=user.metadata.get("user_lastname"),
                    date_joined=user.metadata.get("date_joined"),
                    email=user.metadata.get("user_email"),
                    active=user.metadata.get("user_active"),
                    administrator=user.metadata.get("administrator"),
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
