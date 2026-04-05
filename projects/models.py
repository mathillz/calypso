"""Models for the projects app."""

import uuid

from django.db import models


class Project(models.Model):
    """A generated project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    description = models.TextField(blank=True, default="")
    path = models.CharField(max_length=1000, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.platform})"
