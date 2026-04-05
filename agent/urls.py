"""URL configuration for the agent app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from agent import views

router = DefaultRouter()
router.register(r"conversations", views.ConversationViewSet)
router.register(r"prompts", views.SystemPromptViewSet)

urlpatterns = [
    # Web UI
    path("", views.dashboard, name="dashboard"),
    path("chat/", views.chat_view, name="chat"),
    path("chat/<uuid:conversation_id>/", views.chat_view, name="chat_with_id"),
    path("projects/", views.project_view, name="projects"),
    path("prompts/", views.prompt_manager_view, name="prompt_manager"),

    # HTMX endpoints
    path("htmx/send-message/", views.htmx_send_message, name="htmx_send_message"),
    path("htmx/new-conversation/", views.htmx_new_conversation, name="htmx_new_conversation"),

    # REST API
    path("api/", include(router.urls)),
    path("api/scaffold/", views.scaffold_project, name="scaffold_project"),
]
