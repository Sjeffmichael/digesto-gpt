from django.urls import path
from .views import LoginView
from django.contrib.auth import views as auth_views

app_name = "authentication"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
