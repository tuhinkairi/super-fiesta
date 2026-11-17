"""Exceptions used by utility modules."""


class UtilityError(Exception):
    """Base exception for utility-related errors."""


class ConversionError(UtilityError):
    """Raised when a value cannot be converted."""


class FormattingError(UtilityError):
    """Raised when a value cannot be formatted."""


class CollectionError(UtilityError):
    """Raised when a collection operation fails."""


class SerializationError(UtilityError):
    """Raised when serialization or deserialization fails."""


class ValidationUtilityError(UtilityError):
    """Raised when utility-level validation fails."""


class PathUtilityError(UtilityError):
    """Raised when a path operation fails."""
