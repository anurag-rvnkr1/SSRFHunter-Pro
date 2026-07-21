"""Project-specific exceptions."""

from __future__ import annotations


class SSRFHunterError(Exception):
    """Base exception for SSRFHunter Pro."""


class ConfigurationError(SSRFHunterError):
    """Raised when configuration is invalid."""


class ScanError(SSRFHunterError):
    """Raised when a scan fails."""


class RequestError(SSRFHunterError):
    """Raised when an HTTP request fails."""
