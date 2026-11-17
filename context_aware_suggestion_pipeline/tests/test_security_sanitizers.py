
from context_aware_suggestion_rag.security.sanitizers import (
    SanitizationConfig,
    TextSanitizer,
    sanitize_text,
)


# Default sanitization
sanitizer = TextSanitizer()

result = sanitizer.sanitize("  Hello\x00 World  ")

assert result.original_value == "  Hello\x00 World  "
assert result.sanitized_value == "Hello World"
assert result.modified is True
assert result.has_warnings is True

print("Default text sanitization: PASS")


# Control character removal
result = sanitizer.sanitize("Hello\x01World")

assert result.sanitized_value == "HelloWorld"
assert result.modified is True

print("Control character removal: PASS")


# Preserve newlines
result = sanitizer.sanitize("Hello\nWorld")

assert result.sanitized_value == "Hello\nWorld"
assert result.modified is False

print("Newline preservation: PASS")


# Normalize whitespace
config = SanitizationConfig(normalize_whitespace=True)
sanitizer = TextSanitizer(config)

result = sanitizer.sanitize("Hello    World")

assert result.sanitized_value == "Hello World"
assert result.modified is True

print("Whitespace normalization: PASS")


# Convenience function
result = sanitize_text("  Test input  ")

assert result.sanitized_value == "Test input"

print("Convenience function: PASS")


# Invalid input
try:
    sanitizer.sanitize(123)
except TypeError:
    pass
else:
    raise AssertionError("Expected TypeError for non-string input.")

print("Input validation: PASS")

print("All security sanitizer tests passed.")
