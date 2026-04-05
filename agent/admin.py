"""Admin configuration for the agent app."""

from django.contrib import admin

from agent.models import AgentCapability, Conversation, GeneratedCode, Message, SystemPrompt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "platform_context", "is_active", "created_at", "updated_at"]
    list_filter = ["platform_context", "is_active"]
    search_fields = ["title"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["role", "conversation", "created_at", "token_count"]
    list_filter = ["role"]
    search_fields = ["content"]


@admin.register(GeneratedCode)
class GeneratedCodeAdmin(admin.ModelAdmin):
    list_display = ["filename", "language", "platform", "created_at"]
    list_filter = ["language", "platform"]
    search_fields = ["filename"]


@admin.register(AgentCapability)
class AgentCapabilityAdmin(admin.ModelAdmin):
    list_display = ["name", "platform", "is_active"]
    list_filter = ["platform", "is_active"]


@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ["name", "version", "is_default", "updated_at"]
    list_filter = ["is_default"]
