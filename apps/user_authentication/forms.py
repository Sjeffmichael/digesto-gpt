from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from . import models


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_class = (
            "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg "
            "focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 "
            "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 "
            "dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        )
        self.fields["username"].widget.attrs["placeholder"] = _("Email")
        self.fields["password"].widget.attrs["placeholder"] = _("Password")
        self.fields["username"].widget.attrs["class"] = common_class
        self.fields["password"].widget.attrs["class"] = common_class

    class Meta:
        model = models.User
        fields = ["email", "password"]
