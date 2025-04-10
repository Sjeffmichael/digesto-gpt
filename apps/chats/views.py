from typing import Any

# isort: off
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Conversation, Message
from django.views.generic import (
    TemplateView,
    View,
    ListView,
)
from django.http import Http404, QueryDict
from common.util.locale import is_language_switcher_request


class Chats(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        if request.htmx and not is_language_switcher_request(request):
            template_name = "chats/chat_section.html"
        else:
            template_name = "chats/chat_full.html"
        return render(request, template_name, context)


class MessagesListView(ListView):
    context_object_name = "messages"
    http_method_names = ["get"]
    ordering = ["id"]
    model = Message

    def get_queryset(self):
        conversations = self.model.objects.filter(
            conversation_id=self.kwargs.get("slug")
        ).order_by(*self.ordering)

        return conversations

    def get_template_names(self) -> list[str]:

        if self.request.htmx and not is_language_switcher_request(self.request):
            self.template_name = "chats/chat_section.html"
        else:
            self.template_name = "chats/chat_full.html"

        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["user_email"] = self.request.user
        return super().get_context_data(**kwargs)
