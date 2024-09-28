from django.contrib.auth import login, views as auth_views
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from . import forms


# Create your views here.
class LoginView(auth_views.LoginView):
    form_class = forms.LoginForm
    template_name = "user_authentication/login.html"
    success_url = reverse_lazy("chats:chat-section")

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)
