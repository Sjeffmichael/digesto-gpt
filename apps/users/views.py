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


# Create your views here.
class UserListView(ListView):
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        pass
