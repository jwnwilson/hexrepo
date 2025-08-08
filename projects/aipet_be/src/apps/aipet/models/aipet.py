from django.db import models
from .base import BaseModel


class Aipet(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

