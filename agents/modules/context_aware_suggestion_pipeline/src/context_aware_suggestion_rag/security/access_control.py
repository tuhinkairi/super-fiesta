"""
Role-based access control utilities.

Provides permission definitions, access policies, and an access-control
manager with deny-by-default behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Mapping

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.security.models import (
    AccessControlDecision,
    SecurityAction,
)


# ============================================================
# Permission Model
# ============================================================

@dataclass(frozen=True, slots=True)
class Permission:
    """Represents permission to perform an action on a resource."""

    action: SecurityAction | str
    resource: str

    def __post_init__(self) -> None:
        action = self.action

        if isinstance(action, str):
            try:
                action = SecurityAction(action.lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported security action: {self.action!r}"
                ) from None

            object.__setattr__(self, "action", action)

        if not isinstance(action, SecurityAction):
            raise TypeError("action must be a SecurityAction.")

        if not isinstance(self.resource, str) or not self.resource.strip():
            raise ValueError("resource must be a non-empty string.")

    def matches(self, action: SecurityAction, resource: str) -> bool:
        """Return whether this permission matches an action and resource."""
        action_matches = (
            self.action == action
            or self.action == SecurityAction.ADMIN
        )

        resource_matches = (
            self.resource == "*"
            or self.resource == resource
        )

        return action_matches and resource_matches


# ============================================================
# Access Policy
# ============================================================

@dataclass(slots=True)
class AccessPolicy:
    """Associates a principal or role with a collection of permissions."""

    name: str
    permissions: set[Permission] = field(default_factory=set)
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Policy name must be a non-empty string.")

        if not isinstance(self.permissions, set):
            raise TypeError("permissions must be a set.")

        if not all(
            isinstance(permission, Permission)
            for permission in self.permissions
        ):
            raise TypeError("All permissions must be Permission objects.")

        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a boolean.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    def allows(
        self,
        action: SecurityAction,
        resource: str,
    ) -> bool:
        """Check whether this policy grants the requested permission."""
        if not self.enabled:
            return False

        return any(
            permission.matches(action, resource)
            for permission in self.permissions
        )


# ============================================================
# Access Control Manager
# ============================================================

class AccessControlManager:
    """
    Thread-safe role-based access control manager.

    Principals can receive permissions directly or through assigned roles.
    Access is denied when no matching permission is found.
    """

    def __init__(self) -> None:
        self._lock = RLock()

        self._principal_permissions: dict[str, set[Permission]] = {}
        self._principal_roles: dict[str, set[str]] = {}
        self._roles: dict[str, set[Permission]] = {}
        self._policies: dict[str, AccessPolicy] = {}

    # --------------------------------------------------------
    # Role Management
    # --------------------------------------------------------

    def create_role(
        self,
        role: str,
        permissions: set[Permission] | None = None,
    ) -> None:
        """Create a role with an optional set of permissions."""
        self._validate_name(role, "role")

        permissions = permissions or self._empty_permissions()

        self._validate_permissions(permissions)

        with self._lock:
            if role in self._roles:
                raise ValueError(f"Role already exists: {role}")

            self._roles[role] = set(permissions)

    def delete_role(self, role: str) -> bool:
        """Delete a role and remove it from all principal assignments."""
        with self._lock:
            if role not in self._roles:
                return False

            del self._roles[role]

            for roles in self._principal_roles.values():
                roles.discard(role)

            return True

    def assign_role(self, principal: str, role: str) -> None:
        """Assign an existing role to a principal."""
        self._validate_name(principal, "principal")
        self._validate_name(role, "role")

        with self._lock:
            if role not in self._roles:
                raise KeyError(f"Unknown role: {role}")

            self._principal_roles.setdefault(principal, set()).add(role)

    def revoke_role(self, principal: str, role: str) -> bool:
        """Remove a role assignment from a principal."""
        with self._lock:
            roles = self._principal_roles.get(principal)

            if not roles or role not in roles:
                return False

            roles.remove(role)

            if not roles:
                self._principal_roles.pop(principal, None)

            return True

    def get_roles(self, principal: str) -> set[str]:
        """Return the roles assigned to a principal."""
        with self._lock:
            return set(self._principal_roles.get(principal, set()))

    # --------------------------------------------------------
    # Direct Permission Management
    # --------------------------------------------------------

    def grant_permission(
        self,
        principal: str,
        permission: Permission,
    ) -> None:
        """Grant a permission directly to a principal."""
        self._validate_name(principal, "principal")

        if not isinstance(permission, Permission):
            raise TypeError("permission must be a Permission object.")

        with self._lock:
            self._principal_permissions.setdefault(
                principal, set()
            ).add(permission)

    def revoke_permission(
        self,
        principal: str,
        permission: Permission,
    ) -> bool:
        """Revoke a directly assigned permission."""
        with self._lock:
            permissions = self._principal_permissions.get(principal)

            if not permissions or permission not in permissions:
                return False

            permissions.remove(permission)

            if not permissions:
                self._principal_permissions.pop(principal, None)

            return True

    # --------------------------------------------------------
    # Policy Management
    # --------------------------------------------------------

    def register_policy(self, policy: AccessPolicy) -> None:
        """Register a named access policy."""
        if not isinstance(policy, AccessPolicy):
            raise TypeError("policy must be an AccessPolicy.")

        with self._lock:
            if policy.name in self._policies:
                raise ValueError(
                    f"Policy already exists: {policy.name}"
                )

            self._policies[policy.name] = policy

    def unregister_policy(self, policy_name: str) -> bool:
        """Remove a registered access policy."""
        with self._lock:
            return self._policies.pop(policy_name, None) is not None

    def get_policy(self, policy_name: str) -> AccessPolicy | None:
        """Retrieve a registered policy."""
        with self._lock:
            return self._policies.get(policy_name)

    def assign_policy(
        self,
        principal: str,
        policy_name: str,
    ) -> None:
        """Assign a registered policy's permissions to a principal."""
        self._validate_name(principal, "principal")

        with self._lock:
            policy = self._policies.get(policy_name)

            if policy is None:
                raise KeyError(f"Unknown policy: {policy_name}")

            if not policy.enabled:
                raise ValueError("Cannot assign a disabled policy.")

            self._principal_permissions.setdefault(
                principal, set()
            ).update(policy.permissions)

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    def authorize(
        self,
        principal: str,
        action: SecurityAction | str,
        resource: str,
        context: Mapping[str, Any] | None = None,
    ) -> AccessControlDecision:
        """
        Evaluate whether a principal can perform an action.

        Returns an AccessControlDecision. Unknown principals and
        unmatched permissions are denied by default.
        """
        if not isinstance(principal, str) or not principal.strip():
            raise ValueError("principal must be a non-empty string.")

        if isinstance(action, str):
            try:
                action = SecurityAction(action.lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported security action: {action!r}"
                ) from None

        if not isinstance(action, SecurityAction):
            raise TypeError("action must be a SecurityAction.")

        if not isinstance(resource, str) or not resource.strip():
            raise ValueError("resource must be a non-empty string.")

        if context is not None and not isinstance(context, Mapping):
            raise TypeError("context must be a mapping or None.")

        with self._lock:
            permissions = set(
                self._principal_permissions.get(principal, set())
            )

            assigned_roles = self._principal_roles.get(
                principal, set()
            )

            for role in assigned_roles:
                permissions.update(self._roles.get(role, set()))

            allowed = any(
                permission.matches(action, resource)
                for permission in permissions
            )

        return AccessControlDecision(
            allowed=allowed,
            principal=principal,
            action=action,
            resource=resource,
            reason=(
                "Matching permission found."
                if allowed
                else "No matching permission found. Access denied."
            ),
            metadata={
                "assigned_roles": sorted(assigned_roles),
                "permission_count": len(permissions),
                "context_provided": context is not None,
            },
        )

    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------

    @staticmethod
    def _validate_name(value: str, field_name: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must be a non-empty string."
            )

    @staticmethod
    def _validate_permissions(
        permissions: set[Permission],
    ) -> None:
        if not isinstance(permissions, set):
            raise TypeError("permissions must be a set.")

        if not all(
            isinstance(permission, Permission)
            for permission in permissions
        ):
            raise TypeError(
                "All permissions must be Permission objects."
            )

    @staticmethod
    def _empty_permissions() -> set[Permission]:
        return set()

    def clear(self) -> None:
        """Remove all roles, assignments, permissions, and policies."""
        with self._lock:
            self._principal_permissions.clear()
            self._principal_roles.clear()
            self._roles.clear()
            self._policies.clear()
