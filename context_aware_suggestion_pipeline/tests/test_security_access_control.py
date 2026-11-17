
from context_aware_suggestion_rag.security.access_control import (
    AccessControlManager,
    AccessPolicy,
    Permission,
)
from context_aware_suggestion_rag.security.models import SecurityAction


manager = AccessControlManager()

# Create permissions
read_permission = Permission(
    action=SecurityAction.READ,
    resource="documents",
)

write_permission = Permission(
    action=SecurityAction.WRITE,
    resource="documents",
)

# Create a role
manager.create_role("reader", {read_permission})
manager.assign_role("user_1", "reader")

print("Role creation and assignment: PASS")

# Allowed access
decision = manager.authorize(
    principal="user_1",
    action="read",
    resource="documents",
)

assert decision.allowed is True
print("Authorized access: PASS")

# Denied access
decision = manager.authorize(
    principal="user_1",
    action="write",
    resource="documents",
)

assert decision.allowed is False
print("Unauthorized access denial: PASS")

# Direct permission
manager.grant_permission("user_2", write_permission)

decision = manager.authorize(
    principal="user_2",
    action="write",
    resource="documents",
)

assert decision.allowed is True
print("Direct permission assignment: PASS")

# Policy registration
policy = AccessPolicy(
    name="document_reader",
    permissions={read_permission},
)

manager.register_policy(policy)

assert manager.get_policy("document_reader") is policy
print("Policy registration: PASS")

# Policy assignment
manager.assign_policy("user_3", "document_reader")

decision = manager.authorize(
    principal="user_3",
    action="read",
    resource="documents",
)

assert decision.allowed is True
print("Policy authorization: PASS")

# Role revocation
assert manager.revoke_role("user_1", "reader") is True

decision = manager.authorize(
    principal="user_1",
    action="read",
    resource="documents",
)

assert decision.allowed is False
print("Role revocation: PASS")

# Wildcard resource
manager.grant_permission(
    "admin",
    Permission(SecurityAction.READ, "*"),
)

decision = manager.authorize(
    principal="admin",
    action="read",
    resource="news",
)

assert decision.allowed is True
print("Wildcard resource permission: PASS")

# Clear manager
manager.clear()

decision = manager.authorize(
    principal="admin",
    action="read",
    resource="news",
)

assert decision.allowed is False
print("Access-control reset: PASS")

print("All security access-control tests passed.")
