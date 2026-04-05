"""Admin configuration for the projects app."""

from django.contrib import admin
from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "platform", "created_at"]
    list_filter = ["platform"]
    search_fields = ["name"]
