from django.shortcuts import render

# isort: off
from django.views.generic import ListView

from apps.user_authentication.models import User


# Create your views here.
class UserListView(ListView):
    model = User
    template_name = "users/users_list.html"
    content_object_name = "users"

    def get_queryset(self):
        users = User.objects.all()

        return users
