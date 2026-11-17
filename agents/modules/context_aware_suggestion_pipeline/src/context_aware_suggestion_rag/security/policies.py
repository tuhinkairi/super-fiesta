"""
Security policy definitions.

Provides reusable security policies and a policy manager for
evaluating input, document, URL, and pipeline security requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any, Mapping

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.constants import (
    SUPPORTED_DOCUMENT_EXTENSIONS,
)


# ============================================================
# Enums
# ============================================================

class SecurityPolicyType(str, Enum):
    """Categories of security policies."""

    INPUT = "input"
    DOCUMENT = "document"
    URL = "url"
    ACCESS = "access"
    CONTENT = "content"
    PIPELINE = "pipeline"


class SecurityPolicyAction(str, Enum):
    """Actions taken when a policy is evaluated."""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


# ============================================================
# Policy Evaluation Result
# ============================================================

@dataclass(slots=True)
class PolicyEvaluationResult:
    """Represents the result of evaluating a security policy."""

    allowed: bool
    action: SecurityPolicyAction | str
    policy_name: str
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a boolean.")

        if isinstance(self.action, str):
            self.action = SecurityPolicyAction(self.action.lower())

        if not isinstance(self.action, SecurityPolicyAction):
            raise TypeError(
                "action must be a SecurityPolicyAction."
            )

        if not isinstance(self.policy_name, str) or not self.policy_name.strip():
            raise ValueError("policy_name must be a non-empty string.")

        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string.")

        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list.")

        if not all(isinstance(item, str) for item in self.warnings):
            raise TypeError("All warnings must be strings.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @property
    def blocked(self) -> bool:
        """Return whether the policy blocks the operation."""
        return self.action == SecurityPolicyAction.BLOCK

    @property
    def has_warnings(self) -> bool:
        """Return whether the evaluation produced warnings."""
        return bool(self.warnings)


# ============================================================
# Security Policy
# ============================================================

@dataclass(slots=True)
class SecurityPolicy:
    """Defines a configurable security policy."""

    name: str
    policy_type: SecurityPolicyType | str
    enabled: bool = True
    action: SecurityPolicyAction | str = SecurityPolicyAction.BLOCK
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Policy name must be a non-empty string.")

        if isinstance(self.policy_type, str):
            self.policy_type = SecurityPolicyType(
                self.policy_type.lower()
            )

        if not isinstance(self.policy_type, SecurityPolicyType):
            raise TypeError(
                "policy_type must be a SecurityPolicyType."
            )

        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a boolean.")

        if isinstance(self.action, str):
            self.action = SecurityPolicyAction(self.action.lower())

        if not isinstance(self.action, SecurityPolicyAction):
            raise TypeError(
                "action must be a SecurityPolicyAction."
            )

        if not isinstance(self.description, str):
            raise TypeError("description must be a string.")

        if not isinstance(self.parameters, dict):
            raise TypeError("parameters must be a dictionary.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")


# ============================================================
# Policy Manager
# ============================================================

class SecurityPolicyManager:
    """Thread-safe registry and evaluator for security policies."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._policies: dict[str, SecurityPolicy] = {}

    def register(self, policy: SecurityPolicy) -> None:
        """Register a security policy."""
        if not isinstance(policy, SecurityPolicy):
            raise TypeError("policy must be a SecurityPolicy.")

        with self._lock:
            if policy.name in self._policies:
                raise ValueError(
                    f"Policy already registered: {policy.name}"
                )

            self._policies[policy.name] = policy

    def unregister(self, name: str) -> bool:
        """Remove a registered policy."""
        with self._lock:
            return self._policies.pop(name, None) is not None

    def get(self, name: str) -> SecurityPolicy | None:
        """Retrieve a policy by name."""
        with self._lock:
            return self._policies.get(name)

    def list_policies(
        self,
        policy_type: SecurityPolicyType | str | None = None,
        *,
        enabled_only: bool = False,
    ) -> list[SecurityPolicy]:
        """List registered policies with optional filtering."""
        if isinstance(policy_type, str):
            policy_type = SecurityPolicyType(policy_type.lower())

        if (
            policy_type is not None
            and not isinstance(policy_type, SecurityPolicyType)
        ):
            raise TypeError("Invalid policy_type.")

        with self._lock:
            policies = list(self._policies.values())

        if policy_type is not None:
            policies = [
                policy
                for policy in policies
                if policy.policy_type == policy_type
            ]

        if enabled_only:
            policies = [
                policy for policy in policies if policy.enabled
            ]

        return policies

    def evaluate(
        self,
        name: str,
        context: Mapping[str, Any],
    ) -> PolicyEvaluationResult:
        """Evaluate a named policy against a supplied context."""
        if not isinstance(context, Mapping):
            raise TypeError("context must be a mapping.")

        policy = self.get(name)

        if policy is None:
            return PolicyEvaluationResult(
                allowed=False,
                action=SecurityPolicyAction.BLOCK,
                policy_name=name,
                reason="Policy does not exist.",
            )

        if not policy.enabled:
            return PolicyEvaluationResult(
                allowed=True,
                action=SecurityPolicyAction.ALLOW,
                policy_name=name,
                reason="Policy is disabled.",
            )

        evaluator = self._get_evaluator(policy.policy_type)

        if evaluator is None:
            return PolicyEvaluationResult(
                allowed=False,
                action=SecurityPolicyAction.BLOCK,
                policy_name=name,
                reason="No evaluator exists for this policy type.",
            )

        passed, reason, warnings = evaluator(policy, context)

        if passed:
            return PolicyEvaluationResult(
                allowed=True,
                action=SecurityPolicyAction.ALLOW,
                policy_name=name,
                reason=reason,
                warnings=warnings,
            )

        if policy.action == SecurityPolicyAction.WARN:
            return PolicyEvaluationResult(
                allowed=True,
                action=SecurityPolicyAction.WARN,
                policy_name=name,
                reason=reason,
                warnings=warnings or [reason],
            )

        if policy.action == SecurityPolicyAction.ALLOW:
            return PolicyEvaluationResult(
                allowed=True,
                action=SecurityPolicyAction.ALLOW,
                policy_name=name,
                reason=reason,
                warnings=warnings or [reason],
            )

        return PolicyEvaluationResult(
            allowed=False,
            action=SecurityPolicyAction.BLOCK,
            policy_name=name,
            reason=reason,
            warnings=warnings,
        )

    # --------------------------------------------------------
    # Evaluators
    # --------------------------------------------------------

    @staticmethod
    def _get_evaluator(policy_type: SecurityPolicyType):
        evaluators = {
            SecurityPolicyType.INPUT: SecurityPolicyManager._evaluate_input,
            SecurityPolicyType.DOCUMENT: SecurityPolicyManager._evaluate_document,
            SecurityPolicyType.URL: SecurityPolicyManager._evaluate_url,
            SecurityPolicyType.ACCESS: SecurityPolicyManager._evaluate_access,
            SecurityPolicyType.CONTENT: SecurityPolicyManager._evaluate_content,
            SecurityPolicyType.PIPELINE: SecurityPolicyManager._evaluate_pipeline,
        }

        return evaluators.get(policy_type)

    @staticmethod
    def _evaluate_input(
        policy: SecurityPolicy,
        context: Mapping[str, Any],
    ) -> tuple[bool, str, list[str]]:
        value = context.get("value")

        if not isinstance(value, str):
            return False, "Input value must be a string.", []

        maximum = policy.parameters.get("max_length", 100_000)

        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or maximum <= 0
        ):
            return False, "Invalid max_length policy configuration.", []

        if not value.strip():
            return False, "Input cannot be empty.", []

        if len(value) > maximum:
            return False, "Input exceeds the configured length limit.", []

        if "\x00" in value:
            return False, "Input contains a null byte.", []

        return True, "Input satisfies the policy.", []

    @staticmethod
    def _evaluate_document(
        policy: SecurityPolicy,
        context: Mapping[str, Any],
    ) -> tuple[bool, str, list[str]]:
        extension = context.get("extension")
        size = context.get("size_bytes")

        if not isinstance(extension, str):
            return False, "Document extension is required.", []

        normalized = extension.lower()

        if not normalized.startswith("."):
            normalized = f".{normalized}"

        allowed = policy.parameters.get(
            "allowed_extensions",
            tuple(SUPPORTED_DOCUMENT_EXTENSIONS),
        )

        allowed_extensions = {
            str(item).lower()
            if str(item).startswith(".")
            else f".{str(item).lower()}"
            for item in allowed
        }

        if normalized not in allowed_extensions:
            return False, "Document extension is not permitted.", []

        maximum = policy.parameters.get(
            "max_size_bytes",
            20 * 1024 * 1024,
        )

        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or maximum <= 0
        ):
            return False, "Invalid maximum document size configuration.", []

        if (
            isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
        ):
            return False, "Document size must be a non-negative integer.", []

        if size > maximum:
            return False, "Document exceeds the maximum permitted size.", []

        return True, "Document satisfies the policy.", []

    @staticmethod
    def _evaluate_url(
        policy: SecurityPolicy,
        context: Mapping[str, Any],
    ) -> tuple[bool, str, list[str]]:
        from urllib.parse import urlsplit

        url = context.get("url")

        if not isinstance(url, str) or not url.strip():
            return False, "A valid URL is required.", []

        maximum = policy.parameters.get("max_length", 2048)

        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or maximum <= 0
        ):
            return False, "Invalid URL length configuration.", []

        if len(url) > maximum:
            return False, "URL exceeds the maximum permitted length.", []

        try:
            parsed = urlsplit(url.strip())
            allowed_schemes = policy.parameters.get(
                "allowed_schemes",
                ("http", "https"),
            )

            if parsed.scheme.lower() not in allowed_schemes:
                return False, "URL scheme is not permitted.", []

            if not parsed.hostname:
                return False, "URL hostname is missing.", []

            if parsed.username or parsed.password:
                return True, "URL contains embedded credentials.", [
                    "URL contains embedded user credentials."
                ]

        except ValueError:
            return False, "URL structure is invalid.", []

        return True, "URL satisfies the policy.", []

    @staticmethod
    def _evaluate_access(
        policy: SecurityPolicy,
        context: Mapping[str, Any],
    ) -> tuple[bool, str, list[str]]:
        authenticated = context.get("authenticated", False)
        authorized = context.get("authorized", False)

        if not isinstance(authenticated, bool):
            return False, "Authentication state must be boolean.", []

        if not isinstance(authorized, bool):
            return False, "Authorization state must be boolean.", []

        if not authenticated:
            return False, "Principal is not authenticated.", []

        if not authorized:
            return False, "Principal is not authorized.", []

        return True, "Access requirements satisfied.", []

    @staticmethod
    def _evaluate_content(
        policy: SecurityPolicy,
        context: Mapping[str, Any],
    ) -> tuple[bool, str, list[str]]:
        content = context.get("content")

        if not isinstance(content, str):
            return False, "Content must be a string.", []

        maximum = policy.parameters.get("max_length", 100_000)

        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or maximum <= 0
        ):
            return False, "Invalid content length configuration.", []

        if len(content) > maximum:
            return False, "Content exceeds the maximum permitted length.", []

        forbidden = policy.parameters.get("forbidden_terms", ())

        if not isinstance(forbidden, (list, tuple, set)):
            return False, "Invalid forbidden_terms configuration.", []

        lowered = content.casefold()

        matches = [
            term
            for term in forbidden
            if isinstance(term, str)
            and term
            and term.casefold() in lowered
        ]

        if matches:
            return False, "Content contains forbidden terms.", [
                f"Matched forbidden terms: {', '.join(matches)}"
            ]

        return True, "Content satisfies the policy.", []

    @staticmethod
    def _evaluate_pipeline(
        policy: SecurityPolicy,
        context: Mapping[str, Any],
    ) -> tuple[bool, str, list[str]]:
        stage = context.get("stage")

        if not isinstance(stage, str) or not stage.strip():
            return False, "Pipeline stage is required.", []

        allowed_stages = policy.parameters.get("allowed_stages")

        if allowed_stages is not None:
            if not isinstance(allowed_stages, (list, tuple, set)):
                return False, "Invalid allowed_stages configuration.", []

            if stage not in allowed_stages:
                return False, "Pipeline stage is not permitted.", []

        return True, "Pipeline stage satisfies the policy.", []

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    def clear(self) -> int:
        """Remove all registered policies."""
        with self._lock:
            count = len(self._policies)
            self._policies.clear()
            return count

    def __len__(self) -> int:
        with self._lock:
            return len(self._policies)
