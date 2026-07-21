from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import aiosqlite

from ssrfhunter.models.models import Finding, ScanResult, ScanSummary


class ScanRecord:
    def __init__(
        self,
        id: int,
        target: str,
        started_at: datetime,
        completed_at: datetime,
        duration_seconds: float,
        findings_count: int,
        payload: str,
    ) -> None:
        self.id = id
        self.target = target
        self.started_at = started_at
        self.completed_at = completed_at
        self.duration_seconds = duration_seconds
        self.findings_count = findings_count
        self.payload = payload

    def to_scan_result(self) -> ScanResult:
        data = json.loads(self.payload)
        summary = ScanSummary(
            scan_id=data["summary"]["scan_id"],
            target=data["summary"]["target"],
            started_at=datetime.fromisoformat(data["summary"]["started_at"]),
            completed_at=datetime.fromisoformat(data["summary"]["completed_at"]),
            duration_seconds=data["summary"]["duration_seconds"],
            findings=[Finding(**finding) for finding in data["findings"]],
            statistics=data["summary"]["statistics"],
        )
        return ScanResult(summary=summary, findings=summary.findings, reports={})


class ScanDatabase:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or "ssrfhunter_history.db")
        self.connection: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self.connection = await aiosqlite.connect(self.path)
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                findings_count INTEGER NOT NULL,
                payload TEXT NOT NULL
            )
            """)
        await self.connection.commit()

    async def save_scan(self, result: ScanResult) -> None:
        assert self.connection is not None
        payload = json.dumps(
            {
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
            }
        )
        await self.connection.execute(
            "INSERT INTO scans (target, started_at, completed_at, duration_seconds, findings_count, payload) VALUES (?, ?, ?, ?, ?, ?)",
            (
                result.summary.target,
                result.summary.started_at.isoformat(),
                result.summary.completed_at.isoformat(),
                result.summary.duration_seconds,
                len(result.findings),
                payload,
            ),
        )
        await self.connection.commit()

    async def list_scans(self, limit: int = 10) -> list[ScanRecord]:
        assert self.connection is not None
        cursor = await self.connection.execute(
            "SELECT id, target, started_at, completed_at, duration_seconds, findings_count, payload FROM scans ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            ScanRecord(
                id=row[0],
                target=row[1],
                started_at=datetime.fromisoformat(row[2]),
                completed_at=datetime.fromisoformat(row[3]),
                duration_seconds=row[4],
                findings_count=row[5],
                payload=row[6],
            )
            for row in rows
        ]

    async def get_scan(self, scan_id: int | None = None) -> ScanRecord | None:
        assert self.connection is not None
        if scan_id is None:
            cursor = await self.connection.execute(
                "SELECT id, target, started_at, completed_at, duration_seconds, findings_count, payload FROM scans ORDER BY id DESC LIMIT 1"
            )
        else:
            cursor = await self.connection.execute(
                "SELECT id, target, started_at, completed_at, duration_seconds, findings_count, payload FROM scans WHERE id = ?",
                (scan_id,),
            )
        row = await cursor.fetchone()
        if row is None:
            return None
        return ScanRecord(
            id=row[0],
            target=row[1],
            started_at=datetime.fromisoformat(row[2]),
            completed_at=datetime.fromisoformat(row[3]),
            duration_seconds=row[4],
            findings_count=row[5],
            payload=row[6],
        )
