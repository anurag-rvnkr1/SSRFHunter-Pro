"""Severity scoring and analysis helpers."""

from __future__ import annotations


class Analyzer:
    """Assign severity based on observed evidence."""

    def score(self, status: int, headers: dict[str, str], body: str, url: str) -> tuple[str, int]:
        severity = "Informational"
        score = 0
        if status >= 500:
            severity = "High"
            score = 7
        elif status >= 400:
            severity = "Medium"
            score = 5
        elif any(
            key.lower() in {k.lower() for k in headers}
            for key in ["x-remote-address", "x-forwarded-for"]
        ):
            severity = "High"
            score = 8
        elif "169.254.169.254" in body or "10." in body or "127.0.0.1" in body:
            severity = "Critical"
            score = 10
        elif url.startswith("http://"):
            severity = "Low"
            score = 3
        return severity, score
