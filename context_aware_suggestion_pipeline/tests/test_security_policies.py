
from context_aware_suggestion_rag.security.policies import (
    PolicyEvaluationResult,
    SecurityPolicy,
    SecurityPolicyAction,
    SecurityPolicyManager,
    SecurityPolicyType,
)


manager = SecurityPolicyManager()

# Register input policy
input_policy = SecurityPolicy(
    name="input_limit",
    policy_type=SecurityPolicyType.INPUT,
    parameters={"max_length": 100},
)

manager.register(input_policy)

assert len(manager) == 1
print("Policy registration: PASS")

# Valid input
result = manager.evaluate(
    "input_limit",
    {"value": "Valid pipeline input"},
)

assert result.allowed is True
assert result.action == SecurityPolicyAction.ALLOW
print("Valid input policy: PASS")

# Invalid input
result = manager.evaluate(
    "input_limit",
    {"value": "A" * 101},
)

assert result.allowed is False
assert result.blocked is True
print("Input length enforcement: PASS")

# Document policy
document_policy = SecurityPolicy(
    name="document_upload",
    policy_type=SecurityPolicyType.DOCUMENT,
    parameters={
        "allowed_extensions": [".pdf", ".docx", ".txt", ".json"],
        "max_size_bytes": 1024,
    },
)

manager.register(document_policy)

result = manager.evaluate(
    "document_upload",
    {"extension": ".pdf", "size_bytes": 512},
)

assert result.allowed is True
print("Document upload policy: PASS")

# Reject unsupported extension
result = manager.evaluate(
    "document_upload",
    {"extension": ".exe", "size_bytes": 512},
)

assert result.allowed is False
print("Document extension restriction: PASS")

# URL policy
url_policy = SecurityPolicy(
    name="url_restriction",
    policy_type=SecurityPolicyType.URL,
)

manager.register(url_policy)

result = manager.evaluate(
    "url_restriction",
    {"url": "https://example.com"},
)

assert result.allowed is True
print("URL validation policy: PASS")

# Access policy
access_policy = SecurityPolicy(
    name="access_check",
    policy_type=SecurityPolicyType.ACCESS,
)

manager.register(access_policy)

result = manager.evaluate(
    "access_check",
    {"authenticated": True, "authorized": True},
)

assert result.allowed is True
print("Access policy: PASS")

# Warning policy
warning_policy = SecurityPolicy(
    name="warning_input",
    policy_type=SecurityPolicyType.INPUT,
    action=SecurityPolicyAction.WARN,
    parameters={"max_length": 5},
)

manager.register(warning_policy)

result = manager.evaluate(
    "warning_input",
    {"value": "This is longer than five characters"},
)

assert result.allowed is True
assert result.action == SecurityPolicyAction.WARN
assert result.has_warnings is True
print("Warning policy behavior: PASS")

# Missing policy
result = manager.evaluate("missing", {})

assert result.allowed is False
assert result.blocked is True
print("Missing policy denial: PASS")

# Policy filtering
enabled = manager.list_policies(enabled_only=True)

assert len(enabled) == 5
print("Policy listing: PASS")

# Policy removal
assert manager.unregister("input_limit") is True
assert manager.get("input_limit") is None
print("Policy removal: PASS")

# Clear registry
removed = manager.clear()

assert removed == 4
assert len(manager) == 0
print("Policy registry clearing: PASS")

# Result model
evaluation = PolicyEvaluationResult(
    allowed=True,
    action="allow",
    policy_name="test_policy",
)

assert evaluation.allowed is True
print("Policy evaluation model: PASS")

print("All security policy tests passed.")
