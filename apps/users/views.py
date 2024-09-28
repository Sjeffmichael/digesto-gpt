from typing import Any

from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render

# isort: off
from django.views.generic import ListView

from apps.user_authentication.models import User


# Create your views here.
class UserListView(ListView):
    content_object_name = "users"

    def get_queryset(self):
        users = User.objects.all()

        return users

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if self.request.htmx:
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
