"""Detection engine that analyzes responses and creates findings."""

from __future__ import annotations

from ssrfhunter.analysis import Analyzer
from ssrfhunter.models import Finding


class DetectionEngine:
    """Create findings from HTTP responses."""

    def __init__(self) -> None:
        self.analyzer = Analyzer()

    def analyze(self, url: str, status: int, headers: dict[str, str], body: str) -> Finding:
        severity, score = self.analyzer.score(status, headers, body, url)
        description = (
            "Observed response indicates potential SSRF exposure."
            if severity != "Informational"
            else "No strong SSRF signal observed."
        )
        return Finding(
            title="Potential SSRF Exposure",
            severity=severity,
            description=description,
            evidence=body[:200],
            url=url,
            metadata={"status": status, "score": score, "headers": headers},
        )
