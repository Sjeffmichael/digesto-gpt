from django.conf import settings
from django.contrib.auth import login, views as auth_views
from django.contrib.messages import add_message, constants as messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_htmx.http import HttpResponseClientRedirect, push_url, retarget

from . import forms
from .models import User


class LoggedRedirectMixin:
    """Redirects authenticated users to the login redirect URL."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(resolve_url(settings.LOGIN_REDIRECT_URL))
        return super().dispatch(request, *args, **kwargs)


class LoginView(LoggedRedirectMixin, auth_views.LoginView):
    form_class = forms.LoginForm
    template_name = "user_authentication/login.html"
    success_url = reverse_lazy("chats:chat-section")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponseClientRedirect(self.get_success_url())

    def form_invalid(self, form):
        super().form_invalid(form)
        response = render(
            self.request, self.template_name, self.get_context_data(form=form)
        )
        return retarget(response, "#auth-form")


class PasswordResetView(LoggedRedirectMixin, auth_views.PasswordResetView):
    template_name = "user_authentication/password_reset.html"
    email_template_name = "user_authentication/password_reset_email.html"
    success_url = reverse_lazy("authentication:login")

    def form_valid(self, form):
        super().form_valid(form)
        add_message(
            self.request, messages.SUCCESS, _("Password reset email sent successfully")
        )
        response = render(
            self.request, "user_authentication/login.html", {"form": forms.LoginForm()}
        )
        response = push_url(response, self.get_success_url())
        return retarget(response, "#auth-form")

    def form_invalid(self, form):
        response = render(
            self.request, self.template_name, self.get_context_data(form=form)
        )
        return retarget(response, "#auth-form")


class PasswordResetConfirmView(
    LoggedRedirectMixin, auth_views.PasswordResetConfirmView
):
    template_name = "user_authentication/password_reset_confirm.html"
    success_url = reverse_lazy("authentication:login")

    def form_valid(self, form):
        super().form_valid(form)
        add_message(
            self.request, messages.SUCCESS, _("Password reset done successfully")
        )
        response = render(
            self.request, "user_authentication/login.html", {"form": forms.LoginForm()}
        )
        response = push_url(response, self.get_success_url())
        return retarget(response, "#auth-form")

    def form_invalid(self, form):
        response = render(
            self.request, self.template_name, self.get_context_data(form=form)
        )
        return retarget(response, "#auth-form")


def register_user(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )

            login(request, user)
            return HttpResponseRedirect(reverse_lazy("chats:chat-section"))
        else:
            context = {"form": form}
            response = render(request, "user_authentication/register.html", context)
            return retarget(response, "#register-form")
    context = {"form": forms.RegisterForm()}
    return render(request, "user_authentication/register.html", context)
