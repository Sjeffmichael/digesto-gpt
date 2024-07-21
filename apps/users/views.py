from django.shortcuts import render
from django.views.generic import (
    View, 
    TemplateView, 
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from apps.user_authentication.models import User
# Create your views here.
class UserListView(ListView):
    model = User
    template_name = "users/users_list.html"
    content_object_name = "users"

    def get_queryset(self):
        users = User.objects.all()

        return users
