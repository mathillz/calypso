"""Custom template tags for the agent app."""

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="render_markdown")
def render_markdown(value):
    """Basic markdown to HTML conversion for code blocks."""
    # Convert code blocks
    def replace_code_block(match):
        lang = match.group(1) or "text"
        code = match.group(2).strip()
        return f'''<div class="code-block">
<div class="code-header">
    <span class="code-lang">{lang}</span>
    <button class="btn btn-sm btn-outline-light copy-btn" onclick="copyCode(this)">Copy</button>
</div>
<pre><code class="language-{lang}">{code}</code></pre>
</div>'''

    result = re.sub(r"```(\w*)\n(.*?)```", replace_code_block, value, flags=re.DOTALL)

    # Convert inline code
    result = re.sub(r"`([^`]+)`", r"<code>\1</code>", result)

    # Convert bold
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result)

    # Convert italic
    result = re.sub(r"\*(.+?)\*", r"<em>\1</em>", result)

    # Convert newlines to <br>
    result = result.replace("\n", "<br>")

    return mark_safe(result)


@register.filter(name="truncate_id")
def truncate_id(value):
    """Truncate a UUID for display."""
    return str(value)[:8]
