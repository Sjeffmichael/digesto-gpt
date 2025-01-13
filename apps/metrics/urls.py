from django.urls import path

from .views import Metrics

urlpatterns = [
    path("", Metrics.as_view(), name="metrics-section"),
]
