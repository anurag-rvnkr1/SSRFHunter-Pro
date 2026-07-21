"""Configuration loading and CLI overrides."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import]
from pydantic import BaseModel, ConfigDict, Field

from ssrfhunter.exceptions import ConfigurationError


class ScanConfig(BaseModel):
    """Runtime configuration for the scanner."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    target: str = ""
    input_file: str | None = None
    workers: int = 4
    timeout: int = 10
    headers: dict[str, str] = Field(default_factory=dict)
    cookies: dict[str, str] = Field(default_factory=dict)
    proxy: str | None = None
    user_agent: str = "SSRFHunter-Pro/0.1"
    output: str | None = None
    json_output: bool = False
    html_output: bool = False
    verbose: bool = False
    debug: bool = False
    max_depth: int = 2
    domain_restriction: bool = True
    allow_protocols: list[str] = Field(default_factory=lambda: ["http", "https"])
    payloads_path: str | None = None

    @classmethod
    def from_yaml(cls, path: str | Path | None = None) -> "ScanConfig":
        """Load configuration from a YAML file if present."""
        config_path = Path(path or "config.yml")
        if not config_path.exists():
            return cls()

        with config_path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}

        if not isinstance(raw, dict):
            raise ConfigurationError("Configuration file must contain a mapping.")

        try:
            return cls(**raw)
        except Exception as error:
            raise ConfigurationError(f"Invalid configuration: {error}") from error

    def merge(self, overrides: dict[str, Any]) -> "ScanConfig":
        """Override configuration values from CLI arguments."""
        values = self.model_dump()
        for key, value in overrides.items():
            if value is not None:
                values[key] = value
        return ScanConfig(**values)
