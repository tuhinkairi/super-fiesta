
from context_aware_suggestion_rag.generation.models import (
    GenerationStatus,
    GenerationMode,
    GenerationParameters,
    GenerationRequest,
    GeneratedContent,
    GenerationResult,
    GenerationBatchResult,
)


# Test 1: Generation parameters
parameters = GenerationParameters(
    temperature=0.8,
    top_p=0.9,
    max_output_tokens=1500,
)

assert parameters.temperature == 0.8
assert parameters.max_output_tokens == 1500

print("Generation parameters: PASS")


# Test 2: Invalid parameters
try:
    GenerationParameters(temperature=3.0)
except ValueError:
    print("Parameter validation: PASS")
else:
    raise AssertionError("Expected invalid temperature to fail.")


# Test 3: Generation request
request = GenerationRequest(
    prompt="Write an article about artificial intelligence.",
    content_format="article",
    target_audience="students",
)

assert request.prompt
assert request.request_id.startswith("genreq_")

print("Generation request: PASS")


# Test 4: Generated content
content = GeneratedContent(
    content="Artificial intelligence is transforming technology.",
    request_id=request.request_id,
    content_format="article",
    model="test-model",
    title="Introduction to AI",
)

assert content.word_count == 5
assert content.character_count > 0
assert content.content_id.startswith("content_")

print("Generated content: PASS")


# Test 5: Generation result
result = GenerationResult(
    request_id=request.request_id,
    status=GenerationStatus.COMPLETED,
    generated_content=content,
    execution_time_ms=120.5,
    model="test-model",
)

assert result.success is True

print("Generation result: PASS")


# Test 6: Batch result
batch = GenerationBatchResult(results=[result])

assert batch.total == 1
assert batch.successful == 1
assert batch.failed == 0
assert batch.success_rate == 1.0

print("Generation batch result: PASS")


# Test 7: Empty batch
empty_batch = GenerationBatchResult()

assert empty_batch.total == 0
assert empty_batch.success_rate == 0.0

print("Empty batch handling: PASS")


print("\nAll generation model tests passed.")
