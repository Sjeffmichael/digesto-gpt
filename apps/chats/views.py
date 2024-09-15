from django.shortcuts import render

# isort: off
from django.views.generic import (
    TemplateView,
    View,
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
