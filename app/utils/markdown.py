"""Markdown utilities for formatting and detecting markdown content."""
import re
from typing import Dict, Tuple, Optional


class MarkdownDetector:
    """Detect if content is in markdown format"""

    # Markdown patterns
    MARKDOWN_PATTERNS = {
        "heading": r"^#{1,6}\s+",
        "bold": r"\*\*.*?\*\*|\__.*?\__",
        "italic": r"\*.*?\*|_.*?_",
        "code_inline": r"`[^`]+`",
        "code_block": r"```[\s\S]*?```",
        "link": r"\[.*?\]\(.*?\)",
        "list_unordered": r"^\s*[-*+]\s+",
        "list_ordered": r"^\s*\d+\.\s+",
        "blockquote": r"^\s*>\s+",
        "horizontal_rule": r"^[\*\-_]{3,}$",
        "table": r"\|.*\|",
        "emphasis": r"~~.*?~~",
    }

    @staticmethod
    def is_markdown(content: str) -> bool:
        """
        Detect if content is markdown format.
        Returns True if content contains markdown patterns.
        """
        if not content or not isinstance(content, str):
            return False

        lines = content.split("\n")
        markdown_score = 0
        total_patterns_checked = 0

        for line in lines:
            if not line.strip():
                continue

            for pattern_name, pattern in MarkdownDetector.MARKDOWN_PATTERNS.items():
                total_patterns_checked += 1
                if re.search(pattern, line, re.MULTILINE):
                    markdown_score += 1

        # If more than 20% of lines have markdown patterns, consider it markdown
        if total_patterns_checked > 0:
            markdown_percentage = (markdown_score / total_patterns_checked) * 100
            return markdown_percentage > 20

        return False

    @staticmethod
    def get_markdown_confidence(content: str) -> float:
        """
        Get confidence score (0-1) for markdown detection.
        """
        if not content or not isinstance(content, str):
            return 0.0

        lines = content.split("\n")
        markdown_count = 0
        total_lines = len([l for l in lines if l.strip()])

        if total_lines == 0:
            return 0.0

        for line in lines:
            if not line.strip():
                continue

            for pattern in MarkdownDetector.MARKDOWN_PATTERNS.values():
                if re.search(pattern, line, re.MULTILINE):
                    markdown_count += 1
                    break

        return min(markdown_count / total_lines, 1.0)


class MarkdownFormatter:
    """Format content as markdown"""

    @staticmethod
    def format_as_markdown(content: str) -> Dict:
        """
        Format content as markdown with metadata.

        Returns:
            {
                "content": "formatted content",
                "is_markdown": bool,
                "confidence": float (0-1),
                "sections": [list of sections],
                "has_code": bool,
                "has_links": bool,
                "has_lists": bool,
            }
        """
        is_md = MarkdownDetector.is_markdown(content)
        confidence = MarkdownDetector.get_markdown_confidence(content)

        return {
            "content": content,
            "is_markdown": is_md,
            "confidence": confidence,
            "sections": MarkdownFormatter.extract_sections(content),
            "has_code": MarkdownFormatter.has_code_blocks(content),
            "has_links": MarkdownFormatter.has_links(content),
            "has_lists": MarkdownFormatter.has_lists(content),
        }

    @staticmethod
    def extract_sections(content: str) -> list:
        """Extract markdown sections (headings and content)"""
        sections = []
        lines = content.split("\n")
        current_section = None
        current_level = 0
        current_content = []

        for line in lines:
            heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
            if heading_match:
                # Save previous section
                if current_section:
                    sections.append({
                        "heading": current_section,
                        "level": current_level,
                        "content": "\n".join(current_content).strip(),
                    })
                    current_content = []

                current_section = heading_match.group(2)
                current_level = len(heading_match.group(1))
            else:
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            sections.append({
                "heading": current_section,
                "level": current_level,
                "content": "\n".join(current_content).strip(),
            })

        return sections

    @staticmethod
    def has_code_blocks(content: str) -> bool:
        """Check if content has code blocks"""
        return bool(re.search(r"```[\s\S]*?```|`[^`]+`", content))

    @staticmethod
    def has_links(content: str) -> bool:
        """Check if content has links"""
        return bool(re.search(r"\[.*?\]\(.*?\)|https?://\S+", content))

    @staticmethod
    def has_lists(content: str) -> bool:
        """Check if content has lists"""
        return bool(re.search(r"^\s*[-*+]\s+|^\s*\d+\.\s+", content, re.MULTILINE))

    @staticmethod
    def sanitize_markdown(content: str) -> str:
        """
        Sanitize markdown to prevent XSS while preserving formatting.
        """
        # Remove potentially dangerous scripts
        content = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r"on\w+\s*=", "", content, flags=re.IGNORECASE)

        return content

    @staticmethod
    def to_html(markdown_content: str) -> str:
        """
        Convert markdown to basic HTML.
        Note: For production, use a library like markdown2 or python-markdown
        """
        html = markdown_content

        # Headers
        html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"__(.*?)__", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)
        html = re.sub(r"_(.*?)_", r"<em>\1</em>", html)

        # Code
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

        # Links
        html = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', html)

        # Lists
        html = re.sub(r"^\s*[-*+]\s+(.*?)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        return html


class MarkdownResponseFormatter:
    """Format API responses with markdown detection"""

    @staticmethod
    def format_response(
        content: str,
        sender: str = "assistant",
        timestamp: Optional[str] = None,
    ) -> Dict:
        """
        Format response with markdown detection.

        Returns response with markdown metadata for frontend.
        """
        markdown_data = MarkdownFormatter.format_as_markdown(content)

        return {
            "content": content,
            "sender": sender,
            "timestamp": timestamp,
            "format": {
                "is_markdown": markdown_data["is_markdown"],
                "confidence": markdown_data["confidence"],
                "has_code": markdown_data["has_code"],
                "has_links": markdown_data["has_links"],
                "has_lists": markdown_data["has_lists"],
                "sections": markdown_data["sections"],
            },
            "display_as_markdown": markdown_data["is_markdown"] and markdown_data["confidence"] > 0.3,
        }

    @staticmethod
    def format_conversation(messages: list) -> list:
        """Format entire conversation with markdown detection for each message"""
        formatted_messages = []

        for msg in messages:
            if isinstance(msg, dict):
                formatted_msg = MarkdownResponseFormatter.format_response(
                    content=msg.get("content", ""),
                    sender=msg.get("sender", "assistant"),
                    timestamp=msg.get("timestamp"),
                )
                formatted_messages.append(formatted_msg)
            else:
                formatted_messages.append(msg)

        return formatted_messages


# Example usage and testing
if __name__ == "__main__":
    # Test markdown detection
    test_contents = [
        # Markdown content
        """# Getting Started

This is a guide to help you get started.

## Installation

```bash
pip install package-name
```

## Usage

You can use it like this:

- First step
- Second step
- Third step

Visit [our docs](https://example.com) for more information.
""",
        # Plain text
        "This is just plain text without any markdown formatting.",
        # Mixed content
        """Hello! Here's some info:

**Bold text** and *italic text*

Check out the [link](https://example.com)""",
    ]

    print("Markdown Detection Examples:\n")
    for i, content in enumerate(test_contents, 1):
        detector = MarkdownDetector()
        is_md = detector.is_markdown(content)
        confidence = detector.get_markdown_confidence(content)

        print(f"Example {i}:")
        print(f"  Is Markdown: {is_md}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Content preview: {content[:50]}...")
        print()

    # Test formatting
    print("\nFormatted Response Example:")
    response = MarkdownResponseFormatter.format_response(
        """# Welcome

Here's a formatted response with **bold** and *italic* text.

## Key Points

- Point 1
- Point 2
- Point 3

```python
def hello():
    print("Hello, World!")
```

[Visit our site](https://example.com)"""
    )

    import json
    print(json.dumps(response, indent=2))
