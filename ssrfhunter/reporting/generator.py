from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jinja2
import orjson

from ssrfhunter.models.models import ScanResult


class ReportGenerator:
    """Generate reports in HTML, JSON, and Markdown formats."""

    def __init__(self, template_dir: str | Path | None = None) -> None:
        loader = jinja2.FileSystemLoader(str(template_dir or Path("templates")))
        self.environment = jinja2.Environment(loader=loader, autoescape=True)

    def generate_html(self, result: ScanResult) -> str:
        template = self.environment.get_template("report.html.j2")
        return template.render(
            result=self._serialize_result(result),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def generate_markdown(self, result: ScanResult) -> str:
        template = self.environment.get_template("report.md.j2")
        return template.render(
            result=self._serialize_result(result),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def generate_json(self, result: ScanResult) -> str:
        payload = self._serialize_result(result)
        return orjson.dumps(payload, option=orjson.OPT_INDENT_2).decode("utf-8")

    def _serialize_result(self, result: ScanResult) -> dict[str, Any]:
        return {
            "summary": {
                "scan_id": result.summary.scan_id,
                "target": result.summary.target,
                "started_at": result.summary.started_at.isoformat(),
                "completed_at": result.summary.completed_at.isoformat(),
                "duration_seconds": result.summary.duration_seconds,
                "statistics": result.summary.statistics,
            },
            "findings": [
                {
                    "title": finding.title,
                    "severity": finding.severity,
                    "description": finding.description,
                    "evidence": finding.evidence,
                    "url": finding.url,
                    "metadata": finding.metadata,
                }
                for finding in result.findings
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
