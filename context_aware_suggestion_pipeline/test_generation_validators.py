
from context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
    GenerationResult,
    GenerationStatus,
)
from context_aware_suggestion_rag.generation.validators import (
    ContentValidationConfig,
    GeneratedContentValidator,
    validate_generated_content,
)


# Test 1: Valid generated content
content = GeneratedContent(
    content=(
        "Artificial intelligence helps automate complex tasks. "
        "Machine learning enables systems to learn from data."
    ),
    request_id="request_001",
    content_format="article",
    model="test-model",
    title="Artificial Intelligence",
)

validator = GeneratedContentValidator()

result = validator.validate(content)

assert result.is_valid is True
assert result.errors == []

print("Valid content validation: PASS")


# Test 2: Required phrase
config = ContentValidationConfig(
    required_phrases=("artificial intelligence",),
)

result = validate_generated_content(content, config)

assert result.is_valid is True

print("Required phrase validation: PASS")


# Test 3: Missing required phrase
config = ContentValidationConfig(
    required_phrases=("cybersecurity",),
)

result = validate_generated_content(content, config)

assert result.is_valid is False
assert any("cybersecurity" in error for error in result.errors)

print("Missing phrase detection: PASS")


# Test 4: Prohibited phrase
config = ContentValidationConfig(
    prohibited_phrases=("automate complex tasks",),
)

result = validate_generated_content(content, config)

assert result.is_valid is False

print("Prohibited phrase detection: PASS")


# Test 5: Word-count validation
config = ContentValidationConfig(
    min_word_count=100,
)

result = validate_generated_content(content, config)

assert result.is_valid is False

print("Word-count validation: PASS")


# Test 6: Generation result validation
generation_result = GenerationResult(
    request_id="request_001",
    status=GenerationStatus.COMPLETED,
    generated_content=content,
    execution_time_ms=100.0,
)

result = validator.validate_result(generation_result)

assert result.is_valid is True

print("Generation result validation: PASS")


# Test 7: Missing generated content
invalid_result = GenerationResult(
    request_id="request_002",
    status=GenerationStatus.COMPLETED,
)

result = validator.validate_result(invalid_result)

assert result.is_valid is False

print("Missing generated content detection: PASS")


# Test 8: Invalid configuration
try:
    ContentValidationConfig(
        min_word_count=100,
        max_word_count=10,
    )
except ValueError:
    print("Validation configuration checks: PASS")
else:
    raise AssertionError("Expected invalid configuration to fail.")


print("\nAll generation validator tests passed.")
