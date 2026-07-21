"""Data models for the SSRF scanner."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Finding(BaseModel):
    """Represents a finding discovered during scanning."""

    title: str
    severity: str
    description: str
    evidence: str
    url: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScanSummary(BaseModel):
    """Represents summary information for a scan."""

    scan_id: str
    target: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float = 0.0
    findings: list[Finding] = Field(default_factory=list)
    statistics: dict[str, int] = Field(default_factory=dict)


class ScanResult(BaseModel):
    """Represents the full scan result."""

    summary: ScanSummary
    findings: list[Finding] = Field(default_factory=list)
    reports: dict[str, str] = Field(default_factory=dict)
