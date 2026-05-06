from typing import Any

# isort: off
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Conversation, Message
from django.views.generic import (
    View,
    ListView,
    UpdateView,
    DeleteView,
)
from django.http import Http404, HttpResponse
from common.util.locale import is_language_switcher_request
from django_htmx.http import replace_url
from django.contrib.messages import add_message, constants as messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


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


class ConversationEditTitleView(UpdateView):
    model = Conversation
    fields = ["title"]
    template_name = "chats/conversation_edit_title.html"
    context_object_name = "conversation"
    success_url = reverse_lazy("chats:chat-section")

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        try:
            return self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            raise Http404("Conversation not found")

    def form_valid(self, form):
        return super().form_valid(form)


class ConversationDeleteView(DeleteView):
    model = Conversation
    template_name = "chats/chat_section.html"
    success_url = "/chats/"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        url = reverse_lazy("chats:chat-section")

        response = None
        if kwargs.get("slug") in request.headers.get("HX-Current-URL", ""):
            # retarget the conversation to delete
            response = render(request, self.template_name, context={"use_oob": True})
            response = replace_url(response, url)
        else:
            response = HttpResponse("")
        add_message(request, messages.SUCCESS, _("Conversation deleted successfully"))
        return response
