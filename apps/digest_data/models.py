from django.db import models


# Create your models here.
class Law(models.Model):
    id = models.TextField(
        primary_key=True,
        unique=True,
    )
    metadata = models.JSONField()
    filename = models.TextField()
    proccessed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TextChunk(models.Model):
    fragment_number = models.IntegerField()
    content = models.TextField()
    law = models.ForeignKey(Law, on_delete=models.CASCADE, related_name="chunks")
    proccessed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("fragment_number", "law")
