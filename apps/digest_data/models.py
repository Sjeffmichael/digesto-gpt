from django.db import models


# Create your models here.
class Law(models.Model):
    id = models.TextField(
        primary_key=True,
        unique=True,
    )
    metadata = models.JSONField()
    filename = models.TextField()

class User(models.Model):
    id = models.TextField(
        primary_key=True,
        unique=True,
    )
    metadata = models.JSONField()
    filename = models.TextField()
