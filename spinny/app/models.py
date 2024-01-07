from django.contrib.auth.models import User
from django.db import models

class Box(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.creator + self.created_at + self.updated_at 