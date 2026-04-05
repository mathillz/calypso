"""Views for the AI agent application."""

import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from agent.models import (
    AgentCapability,
    Conversation,
    GeneratedCode,
    Message,
    SystemPrompt,
)
from agent.prompts.system_prompt import get_system_prompt
from agent.serializers import (
    ConversationSerializer,
    GeneratedCodeSerializer,
    MessageSerializer,
    SystemPromptSerializer,
)
from agent.services.ai_engine import AIEngine
from agent.services.code_generator import CodeGenerator
from agent.services.project_scaffolder import ProjectScaffolder

logger = logging.getLogger(__name__)


# ============================================================
# Template Views (Web UI)
# ============================================================

def dashboard(request):
    """Main dashboard view."""
    conversations = Conversation.objects.filter(is_active=True)[:10]
    return render(request, "agent/dashboard.html", {
        "conversations": conversations,
        "platforms": [
            {"id": "general", "name": "General", "icon": "bi-stars"},
            {"id": "django", "name": "Django Backend", "icon": "bi-server"},
            {"id": "react_native", "name": "React Native", "icon": "bi-phone"},
            {"id": "electron", "name": "Electron", "icon": "bi-display"},
            {"id": "django_web", "name": "Django Web", "icon": "bi-globe"},
        ],
    })


def chat_view(request, conversation_id=None):
    """Chat interface view."""
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        messages = conversation.messages.all()
    else:
        conversation = None
        messages = []

    return render(request, "agent/chat.html", {
        "conversation": conversation,
        "messages": messages,
        "platforms": [
            ("general", "General"),
            ("django", "Django Backend"),
            ("react_native", "React Native"),
            ("electron", "Electron"),
            ("django_web", "Django Web"),
        ],
    })


def project_view(request):
    """Project management view."""
    scaffolder = ProjectScaffolder()
    projects = scaffolder.list_projects()
    return render(request, "agent/projects.html", {
        "projects": projects,
    })


def prompt_manager_view(request):
    """System prompt management view."""
    prompts = SystemPrompt.objects.all()
    return render(request, "agent/prompts.html", {
        "prompts": prompts,
    })


# ============================================================
# HTMX Partial Views
# ============================================================

def htmx_send_message(request):
    """Handle message sending via HTMX."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    content = request.POST.get("message", "").strip()
    conversation_id = request.POST.get("conversation_id", "")
    platform = request.POST.get("platform", "general")

    if not content:
        return render(request, "agent/partials/error.html", {
            "error": "Message cannot be empty"
        })

    # Get or create conversation
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
    else:
        conversation = Conversation.objects.create(
            title=content[:50] + ("..." if len(content) > 50 else ""),
            platform_context=platform,
        )

    # Store user message
    user_message = Message.objects.create(
        conversation=conversation,
        role="user",
        content=content,
    )

    # Get conversation history
    history = list(
        conversation.messages.values("role", "content").order_by("created_at")
    )

    # Generate AI response
    engine = AIEngine()
    system_prompt = get_system_prompt(
        platform=conversation.platform_context,
        custom_override=conversation.system_prompt_override,
    )
    ai_response = engine.generate(history, system_prompt=system_prompt)

    # Store assistant message
    assistant_message = Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=ai_response.content,
        token_count=ai_response.token_usage.get("total_tokens", 0),
        metadata={
            "model": ai_response.model,
            "finish_reason": ai_response.finish_reason,
        },
    )

    # Extract and store code blocks
    if ai_response.code_blocks:
        code_gen = CodeGenerator()
        code_gen.extract_and_store(
            ai_response.content,
            conversation,
            assistant_message,
            platform=conversation.platform_context,
        )

    return render(request, "agent/partials/message_pair.html", {
        "user_message": user_message,
        "assistant_message": assistant_message,
        "conversation": conversation,
    })


def htmx_new_conversation(request):
    """Create a new conversation via HTMX."""
    platform = request.POST.get("platform", "general")
    conversation = Conversation.objects.create(
        title="New Conversation",
        platform_context=platform,
    )
    return redirect("chat_with_id", conversation_id=conversation.id)


# ============================================================
# REST API Views
# ============================================================

class ConversationViewSet(viewsets.ModelViewSet):
    """API endpoint for conversations."""

    queryset = Conversation.objects.filter(is_active=True)
    serializer_class = ConversationSerializer

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        """Send a message in a conversation and get AI response."""
        conversation = self.get_object()
        content = request.data.get("content", "").strip()

        if not content:
            return Response(
                {"error": "Message content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Store user message
        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=content,
        )

        # Get conversation history
        history = list(
            conversation.messages.values("role", "content").order_by("created_at")
        )

        # Generate AI response
        engine = AIEngine()
        system_prompt = get_system_prompt(
            platform=conversation.platform_context,
            custom_override=conversation.system_prompt_override,
        )
        ai_response = engine.generate(history, system_prompt=system_prompt)

        # Store assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=ai_response.content,
            token_count=ai_response.token_usage.get("total_tokens", 0),
            metadata={
                "model": ai_response.model,
                "finish_reason": ai_response.finish_reason,
            },
        )

        # Extract and store code blocks
        if ai_response.code_blocks:
            code_gen = CodeGenerator()
            code_gen.extract_and_store(
                ai_response.content,
                conversation,
                assistant_message,
                platform=conversation.platform_context,
            )

        return Response({
            "user_message": MessageSerializer(user_message).data,
            "assistant_message": MessageSerializer(assistant_message).data,
            "code_blocks": [
                {"language": b["language"], "code": b["code"]}
                for b in ai_response.code_blocks
            ],
        })

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """Get all messages in a conversation."""
        conversation = self.get_object()
        messages = conversation.messages.all()
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=True, methods=["get"])
    def code(self, request, pk=None):
        """Get all generated code for a conversation."""
        conversation = self.get_object()
        code = conversation.generated_code.all()
        return Response(GeneratedCodeSerializer(code, many=True).data)


class SystemPromptViewSet(viewsets.ModelViewSet):
    """API endpoint for system prompts."""

    queryset = SystemPrompt.objects.all()
    serializer_class = SystemPromptSerializer

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set a prompt as the default."""
        prompt = self.get_object()
        SystemPrompt.objects.filter(is_default=True).update(is_default=False)
        prompt.is_default = True
        prompt.save()
        return Response({"status": "ok"})


@api_view(["POST"])
def scaffold_project(request):
    """API endpoint to scaffold a new project."""
    name = request.data.get("name", "").strip()
    platform = request.data.get("platform", "").strip()
    options = request.data.get("options", {})

    if not name or not platform:
        return Response(
            {"error": "name and platform are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    scaffolder = ProjectScaffolder()
    try:
        result = scaffolder.create_project(name, platform, options)
        return Response(result, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
