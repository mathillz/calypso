"""
Code Generator Service - Extracts, processes, and manages generated code.
"""

import logging
import re

from agent.models import GeneratedCode

logger = logging.getLogger(__name__)


class CodeGenerator:
    """Service for processing and storing AI-generated code."""

    LANGUAGE_EXTENSIONS = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "tsx": ".tsx",
        "jsx": ".jsx",
        "html": ".html",
        "css": ".css",
        "json": ".json",
        "yaml": ".yaml",
        "yml": ".yml",
        "dockerfile": "Dockerfile",
        "shell": ".sh",
        "bash": ".sh",
        "sql": ".sql",
        "markdown": ".md",
    }

    def extract_and_store(self, content, conversation, message=None, platform="general"):
        """Extract code blocks from AI response and store them.

        Args:
            content: The AI response content with code blocks
            conversation: The Conversation instance
            message: The Message instance (optional)
            platform: Target platform identifier

        Returns:
            List of GeneratedCode instances
        """
        code_blocks = self._extract_code_blocks(content)
        stored_blocks = []

        for i, block in enumerate(code_blocks):
            filename = block.get("filename", f"generated_{i}{self._get_extension(block['language'])}")

            generated = GeneratedCode.objects.create(
                conversation=conversation,
                message=message,
                filename=filename,
                language=block["language"],
                content=block["code"],
                platform=platform,
            )
            stored_blocks.append(generated)
            logger.info("Stored generated code: %s", filename)

        return stored_blocks

    def _extract_code_blocks(self, content):
        """Extract code blocks with optional filename comments."""
        blocks = []
        pattern = r'```(\w*)\n(.*?)```'

        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or "text"
            code = match.group(2).strip()

            filename = self._detect_filename(code, language)

            blocks.append({
                "language": language,
                "code": code,
                "filename": filename,
            })

        return blocks

    def _detect_filename(self, code, language):
        """Try to detect filename from code comments or content."""
        first_line = code.split("\n")[0].strip()

        filename_pattern = r'#\s*([\w/.-]+\.\w+)|//\s*([\w/.-]+\.\w+)|/\*\s*([\w/.-]+\.\w+)'
        match = re.match(filename_pattern, first_line)
        if match:
            return next(g for g in match.groups() if g is not None)

        return None

    def _get_extension(self, language):
        """Get file extension for a language."""
        return self.LANGUAGE_EXTENSIONS.get(language.lower(), ".txt")

    def get_project_files(self, conversation):
        """Get all generated code files for a conversation, organized by platform."""
        codes = GeneratedCode.objects.filter(conversation=conversation)
        organized = {}
        for code in codes:
            platform = code.platform
            if platform not in organized:
                organized[platform] = []
            organized[platform].append({
                "id": str(code.id),
                "filename": code.filename,
                "language": code.language,
                "content": code.content,
                "created_at": code.created_at.isoformat(),
            })
        return organized
