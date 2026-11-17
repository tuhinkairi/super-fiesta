
from context_aware_suggestion_rag.generation.models import (
    GenerationRequest,
)
from context_aware_suggestion_rag.generation.prompts import (
    PromptTemplate,
    PromptBuilder,
    build_generation_prompt,
)


# Test 1: Template rendering
template = PromptTemplate(
    name="test_template",
    template="Write about $topic for $audience.",
)

rendered = template.render({
    "topic": "Artificial Intelligence",
    "audience": "students",
})

assert rendered == "Write about Artificial Intelligence for students."

print("Prompt template rendering: PASS")


# Test 2: Missing template variable
try:
    template.render({"topic": "AI"})
except ValueError:
    print("Missing template variable validation: PASS")
else:
    raise AssertionError("Expected missing variable validation.")


# Test 3: Build a generation request
request = GenerationRequest(
    prompt="Explain retrieval augmented generation.",
    content_format="article",
    target_audience="MCA students",
    language="en",
    region="IN",
    context="RAG combines retrieval with language generation.",
    instructions="Include practical examples.",
)

print("Generation request creation: PASS")


# Test 4: Build system prompt
builder = PromptBuilder()

system_prompt = builder.build_system_prompt()

assert "professional content strategist" in system_prompt

print("System prompt construction: PASS")


# Test 5: Build user prompt
user_prompt = builder.build_user_prompt(request)

assert "retrieval augmented generation" in user_prompt
assert "MCA students" in user_prompt
assert "practical examples" in user_prompt
assert "RAG combines retrieval" in user_prompt

print("User prompt construction: PASS")


# Test 6: Build complete prompt
prompts = build_generation_prompt(request)

assert "system_prompt" in prompts
assert "user_prompt" in prompts
assert prompts["system_prompt"]
assert prompts["user_prompt"]

print("Complete prompt construction: PASS")


# Test 7: Invalid request
try:
    builder.build_user_prompt("invalid request")
except TypeError:
    print("Request type validation: PASS")
else:
    raise AssertionError("Expected request type validation.")


print("\nAll generation prompt tests passed.")
