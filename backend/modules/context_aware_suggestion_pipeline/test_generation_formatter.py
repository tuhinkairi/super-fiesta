
import json

from context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
)
from context_aware_suggestion_rag.generation.formatter import (
    ContentFormatter,
    FormattingOptions,
    format_generated_content,
)


content = GeneratedContent(
    content=(
        "Artificial intelligence is transforming technology.\n\n"
        "Machine learning helps computers learn from data."
    ),
    request_id="request_001",
    content_format="article",
    model="test-model",
    title="Introduction to AI",
    description="A beginner-friendly introduction.",
    metadata={"category": "technology"},
)

formatter = ContentFormatter()


# Test 1: Markdown
markdown = formatter.to_markdown(content)

assert "# Introduction to AI" in markdown
assert "beginner-friendly" in markdown

print("Markdown formatting: PASS")


# Test 2: Plain text
plain_text = formatter.to_plain_text(content)

assert "# Introduction to AI" not in plain_text
assert "Artificial intelligence" in plain_text

print("Plain text formatting: PASS")


# Test 3: HTML
html = formatter.to_html(content)

assert "<h1>Introduction to AI</h1>" in html
assert "<p>" in html

print("HTML formatting: PASS")


# Test 4: HTML escaping
unsafe_content = GeneratedContent(
    content="<script>alert('test')</script>",
    request_id="request_002",
    content_format="article",
    model="test-model",
)

safe_html = formatter.to_html(unsafe_content)

assert "<script>" not in safe_html
assert "&lt;script&gt;" in safe_html

print("HTML escaping: PASS")


# Test 5: JSON
json_output = formatter.to_json(content)
parsed = json.loads(json_output)

assert parsed["content_id"] == content.content_id
assert parsed["content_format"] == "article"

print("JSON serialization: PASS")


# Test 6: Metadata inclusion
metadata_formatter = ContentFormatter(
    FormattingOptions(include_metadata=True)
)

metadata_output = metadata_formatter.to_dict(content)

assert metadata_output["metadata"]["category"] == "technology"

print("Metadata formatting: PASS")


# Test 7: Format dispatcher
result = formatter.format(content, "markdown")

assert result == markdown

print("Format dispatcher: PASS")


# Test 8: Unsupported format
try:
    formatter.format(content, "xml")
except ValueError:
    print("Unsupported format validation: PASS")
else:
    raise AssertionError("Expected unsupported format validation.")


# Test 9: Invalid JSON indentation
try:
    formatter.to_json(content, indent=-1)
except ValueError:
    print("JSON indentation validation: PASS")
else:
    raise AssertionError("Expected invalid indentation validation.")


# Test 10: Convenience function
result = format_generated_content(content, "plain_text")

assert "Artificial intelligence" in result

print("Convenience formatter: PASS")


print("\nAll generation formatter tests passed.")
