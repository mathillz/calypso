"""Serializers for the AI agent REST API."""

from rest_framework import serializers

from agent.models import Conversation, GeneratedCode, Message, SystemPrompt


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id", "conversation", "role", "content",
            "created_at", "token_count", "metadata",
        ]
        read_only_fields = ["id", "created_at"]


class GeneratedCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedCode
        fields = [
            "id", "conversation", "message", "filename",
            "language", "content", "platform", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "title", "created_at", "updated_at",
            "system_prompt_override", "platform_context",
            "is_active", "messages", "message_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_message_count(self, obj):
        return obj.messages.count()


class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = [
            "id", "name", "content", "version",
            "is_default", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
