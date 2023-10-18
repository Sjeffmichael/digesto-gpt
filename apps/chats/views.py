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

def home(request):
    return render(request, "base.html")


# Create your views here.
class UserChats(View):
    def get(self, request, *args, **kwargs):
        return render(request, "base.html")


class UserChatsTemplateView(TemplateView, UserChats):
    template_name = "base.html"

    def get(self, request, *args, **kwargs):
        return super.get(request, *args, **kwargs)