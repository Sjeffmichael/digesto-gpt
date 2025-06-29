from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from . import models


class LoginForm(AuthenticationForm):
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            render_value=True, attrs={"autocomplete": "current-password"}
        ),
    )
    error_messages = {
        "invalid_login": _("Please enter a correct email address and password."),
        "inactive": _("This account is inactive."),
    }

    class Meta:
        model = models.User
        fields = ["email", "password"]


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            render_value=True, attrs={"autocomplete": "current-password"}
        ),
        strip=False,
    )

    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            render_value=True, attrs={"autocomplete": "new-password"}
        ),
        strip=False,
    )

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError(_("Passwords do not match."))

        return password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if models.User.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists."))

        validate_email(email)

        return email

    class Meta:
        model = models.User
        fields = ["email", "password"]
