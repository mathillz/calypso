# CodeCraft AI

An intelligent coding agent platform built with Django that generates production-grade applications across multiple platforms.

## Features

- **Multi-Platform Code Generation**: Django backends, React Native mobile apps, Electron desktop apps, and Django web templates
- **Conversational Interface**: Chat with the AI agent through a sleek web UI
- **Project Scaffolding**: Generate complete project structures with one click
- **System Prompt Management**: Customize the AI's behavior with versioned prompts
- **REST API**: Full API for programmatic access
- **Code Extraction**: Automatically extracts and stores generated code blocks

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: Django Templates + HTMX + Bootstrap 5
- **AI**: OpenAI GPT-4 / Anthropic Claude (with demo mode fallback)
- **Database**: SQLite (default), PostgreSQL ready

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd codecraft_ai

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Visit `http://localhost:8000` to access the dashboard.

## Configuration

Create a `.env` file with:

```
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key        # Optional - enables AI responses
ANTHROPIC_API_KEY=your-anthropic-key   # Optional - alternative provider
AI_MODEL=gpt-4
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.1
```

**Note**: Without API keys, the agent runs in demo mode with pre-built responses.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conversations/` | GET, POST | List/create conversations |
| `/api/conversations/{id}/send_message/` | POST | Send a message |
| `/api/conversations/{id}/messages/` | GET | Get conversation messages |
| `/api/conversations/{id}/code/` | GET | Get generated code |
| `/api/prompts/` | GET, POST | Manage system prompts |
| `/api/scaffold/` | POST | Scaffold a new project |

## Architecture

```
codecraft_ai/
├── agent/                    # Main AI agent app
│   ├── models.py            # Conversation, Message, GeneratedCode models
│   ├── views.py             # Web UI + REST API views
│   ├── serializers.py       # DRF serializers
│   ├── services/            # Core services
│   │   ├── ai_engine.py     # LLM integration (OpenAI/Anthropic)
│   │   ├── code_generator.py # Code extraction and storage
│   │   └── project_scaffolder.py # Project structure generation
│   ├── prompts/             # System prompts
│   │   └── system_prompt.py # Comprehensive coding agent prompt
│   └── templates/           # Django templates
├── projects/                # Project management app
├── templates/               # Global templates
└── codecraft_ai/            # Django project settings
```

## Platforms Supported

1. **Django Backend**: REST APIs, models, authentication, Celery tasks
2. **React Native**: Mobile apps, navigation, state management, native features
3. **Electron**: Desktop apps, IPC, system tray, auto-updater
4. **Django Web**: Server-rendered with HTMX, Alpine.js, Bootstrap

## License

MIT
