from django.contrib.auth.forms import AuthenticationForm
from django import forms
from . import models

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Email'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
        self.fields['username'].widget.attrs['class'] = 'flex w-full justify-center input input-bordered'
        self.fields['password'].widget.attrs['class'] = 'flex w-full justify-center input input-bordered'

    class Meta:
        model = models.User
        fields = ["email", "password"]