from django.db import models
from django.utils import timezone

from apps.user_authentication.models import User


class Conversation(models.Model):
    slug = models.SlugField(unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_message = models.TextField()
    references = models.TextField(null=True, blank=True, default=None)
    created_date = models.DateTimeField(default=timezone.now)
    metrics = models.JSONField(null=True, blank=True, default=None)
