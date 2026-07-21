"""Load payloads from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import]


class PayloadLoader:
    """Load YAML payload definitions for different categories."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or "payloads/default.yml")

    def load(self) -> dict[str, list[str]]:
        """Load payloads from the YAML file or fall back to bundled defaults."""
        if not self.path.exists():
            return self._default_payloads()
        with self.path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        payloads = {key: list(value) for key, value in data.items() if isinstance(value, list)}
        if not payloads:
            return self._default_payloads()
        return payloads

    def _default_payloads(self) -> dict[str, list[str]]:
        return {
            "basic": ["http://127.0.0.1", "https://127.0.0.1"],
            "localhost": ["http://localhost", "https://localhost"],
            "cloud metadata": ["http://169.254.169.254/latest/meta-data/"],
            "internal network": ["http://10.0.0.1"],
            "protocol-specific": ["http://127.0.0.1"],
        }
