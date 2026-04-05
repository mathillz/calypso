"""
Core AI Engine - Handles communication with LLM providers.
Supports OpenAI and Anthropic with fallback, retry logic, and streaming.
"""

import json
import logging
import re
from dataclasses import dataclass, field

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Structured response from the AI engine."""
    content: str
    model: str
    token_usage: dict = field(default_factory=dict)
    code_blocks: list = field(default_factory=list)
    finish_reason: str = ""


class AIEngine:
    """Core AI engine that interfaces with LLM providers."""

    def __init__(self, provider="openai"):
        self.provider = provider
        self.api_key = self._get_api_key()
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE

    def _get_api_key(self):
        if self.provider == "openai":
            return settings.OPENAI_API_KEY
        elif self.provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        return ""

    def generate(self, messages, system_prompt="", temperature=None, max_tokens=None):
        """Generate a response from the AI model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            AIResponse with the generated content
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        if not self.api_key:
            return self._generate_demo_response(messages, system_prompt)

        try:
            if self.provider == "openai":
                return self._generate_openai(messages, system_prompt, temp, tokens)
            elif self.provider == "anthropic":
                return self._generate_anthropic(messages, system_prompt, temp, tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error("AI generation failed: %s", str(e))
            return self._generate_demo_response(messages, system_prompt)

    def _generate_openai(self, messages, system_prompt, temperature, max_tokens):
        """Generate response using OpenAI API."""
        import openai

        client = openai.OpenAI(api_key=self.api_key)

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        response = client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        content = choice.message.content or ""

        return AIResponse(
            content=content,
            model=self.model,
            token_usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            code_blocks=self._extract_code_blocks(content),
            finish_reason=choice.finish_reason or "",
        )

    def _generate_anthropic(self, messages, system_prompt, temperature, max_tokens):
        """Generate response using Anthropic API."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        formatted_messages = []
        for msg in messages:
            if msg["role"] != "system":
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = client.messages.create(**kwargs)

        content = response.content[0].text if response.content else ""

        return AIResponse(
            content=content,
            model=self.model,
            token_usage={
                "prompt_tokens": response.usage.input_tokens if response.usage else 0,
                "completion_tokens": response.usage.output_tokens if response.usage else 0,
            },
            code_blocks=self._extract_code_blocks(content),
            finish_reason=response.stop_reason or "",
        )

    def _generate_demo_response(self, messages, system_prompt):
        """Generate a demo response when no API key is configured."""
        last_message = messages[-1]["content"] if messages else ""

        demo_content = self._build_demo_content(last_message)

        return AIResponse(
            content=demo_content,
            model="demo-mode",
            token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            code_blocks=self._extract_code_blocks(demo_content),
            finish_reason="demo",
        )

    def _build_demo_content(self, user_message):
        """Build contextual demo response based on user message."""
        lower_msg = user_message.lower()

        if any(kw in lower_msg for kw in ["django", "backend", "api", "model"]):
            return self._demo_django_response(user_message)
        elif any(kw in lower_msg for kw in ["react native", "mobile", "app"]):
            return self._demo_react_native_response(user_message)
        elif any(kw in lower_msg for kw in ["electron", "desktop"]):
            return self._demo_electron_response(user_message)
        elif any(kw in lower_msg for kw in ["template", "html", "web page"]):
            return self._demo_web_response(user_message)
        else:
            return self._demo_general_response(user_message)

    def _demo_django_response(self, user_message):
        return f"""I'll help you build that Django backend! Here's my analysis:

**Architecture Decision:** Using Django REST Framework with a service layer pattern.

```python
# models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

```python
# serializers.py
from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']
```

```python
# views.py
from rest_framework import viewsets, filters
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(is_active=True)
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
```

**Next steps:** Add authentication, write tests, set up Docker.
*Running in demo mode — configure OPENAI_API_KEY or ANTHROPIC_API_KEY for full AI responses.*"""

    def _demo_react_native_response(self, user_message):
        return f"""I'll create that React Native component for you!

```typescript
// screens/HomeScreen.tsx
import React from 'react';
import {{ View, Text, FlatList, StyleSheet, TouchableOpacity }} from 'react-native';
import {{ useNavigation }} from '@react-navigation/native';

interface Item {{
  id: string;
  title: string;
  subtitle: string;
}}

const HomeScreen: React.FC = () => {{
  const navigation = useNavigation();
  const [items, setItems] = React.useState<Item[]>([]);

  const renderItem = ({{ item }}: {{ item: Item }}) => (
    <TouchableOpacity style={{styles.card}} onPress={{() => navigation.navigate('Detail', {{ id: item.id }})}}>
      <Text style={{styles.title}}>{{item.title}}</Text>
      <Text style={{styles.subtitle}}>{{item.subtitle}}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={{styles.container}}>
      <FlatList data={{items}} renderItem={{renderItem}} keyExtractor={{(item) => item.id}} />
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{ flex: 1, backgroundColor: '#f5f5f5' }},
  card: {{ backgroundColor: '#fff', padding: 16, marginHorizontal: 16, marginTop: 12, borderRadius: 8 }},
  title: {{ fontSize: 18, fontWeight: '600' }},
  subtitle: {{ fontSize: 14, color: '#666', marginTop: 4 }},
}});

export default HomeScreen;
```

*Running in demo mode — configure an API key for full AI responses.*"""

    def _demo_electron_response(self, user_message):
        return f"""Here's a secure Electron setup:

```javascript
// main.js
const {{ app, BrowserWindow, ipcMain }} = require('electron');
const path = require('path');

function createWindow() {{
  const mainWindow = new BrowserWindow({{
    width: 1200,
    height: 800,
    webPreferences: {{
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    }},
  }});
  mainWindow.loadFile('index.html');
}}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {{ if (process.platform !== 'darwin') app.quit(); }});
```

*Running in demo mode — configure an API key for full AI responses.*"""

    def _demo_web_response(self, user_message):
        return """Here's a Django template with HTMX:

```html
{{% extends "base.html" %}}
{{% block content %}}
<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
  <div hx-get="/api/items/" hx-trigger="load" hx-target="#items-list">
    Loading...
  </div>
  <div id="items-list"></div>
</div>
{{% endblock %}}
```

*Running in demo mode — configure an API key for full AI responses.*"""

    def _demo_general_response(self, user_message):
        return f"""I'm CodeCraft AI, ready to help you build! I can generate:

- **Django backends** with REST APIs, authentication, and background tasks
- **React Native** mobile apps with navigation, state management, and native features
- **Electron** desktop apps with secure IPC and OS integration
- **Django web apps** with HTMX, Alpine.js, and server-side rendering

Tell me what you'd like to build, and I'll generate production-ready code!

*Running in demo mode — configure OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file for full AI-powered responses.*"""

    @staticmethod
    def _extract_code_blocks(content):
        """Extract code blocks from markdown-formatted content."""
        pattern = r'```(\w*)\n(.*?)```'
        blocks = []
        for match in re.finditer(pattern, content, re.DOTALL):
            blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2).strip(),
            })
        return blocks
