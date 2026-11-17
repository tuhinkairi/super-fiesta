
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
    LLMUsage,
)

# Default request.
request = LLMRequest(
    prompt="Explain retrieval augmented generation."
)

assert request.temperature == 0.7
assert request.top_p == 0.95
assert request.max_output_tokens == 2048

print("Default LLM request: PASS")

# Custom request.
custom_request = LLMRequest(
    prompt="Explain hybrid search.",
    model="test-model",
    temperature=0.5,
    top_p=0.9,
    top_k=20,
    max_output_tokens=1000,
)

assert custom_request.model == "test-model"
assert custom_request.top_k == 20

print("Custom LLM request: PASS")

# Token usage.
usage = LLMUsage(
    prompt_tokens=100,
    completion_tokens=50,
)

assert usage.total_tokens == 150

print("LLM token usage: PASS")

# Response.
response = LLMResponse(
    text="Hybrid search combines dense and sparse retrieval.",
    model="test-model",
    provider="test-provider",
    usage=usage,
    latency_ms=120.5,
)

assert response.text
assert response.usage.total_tokens == 150
assert response.provider == "test-provider"

print("LLM response model: PASS")

# Invalid request validation.
try:
    LLMRequest(prompt="")
except ValueError:
    print("Invalid prompt validation: PASS")
else:
    raise AssertionError("Empty prompts should be rejected.")

# Invalid token usage.
try:
    LLMUsage(prompt_tokens=-1)
except ValueError:
    print("Invalid token usage validation: PASS")
else:
    raise AssertionError("Negative token counts should be rejected.")

print("All LLM model tests passed.")
