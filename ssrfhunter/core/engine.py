from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from ssrfhunter.analysis import Analyzer
from ssrfhunter.config.settings import ScanConfig
from ssrfhunter.crawler.crawler import Crawler
from ssrfhunter.detection.engine import DetectionEngine
from ssrfhunter.models.models import Finding, ScanResult, ScanSummary
from ssrfhunter.payloads.loader import PayloadLoader
from ssrfhunter.requester.client import AsyncHttpClient


class ScanEngine:
    """Scan orchestration engine for SSRFHunter Pro."""

    def __init__(self, config: ScanConfig, logger: Any) -> None:
        self.config = config
        self.logger = logger
        self.client = AsyncHttpClient(
            timeout=config.timeout,
            headers={"User-Agent": config.user_agent, **config.headers},
            proxy=config.proxy,
            verify_ssl=True,
        )
        self.payloads = PayloadLoader(config.payloads_path).load()
        self.crawler = Crawler(self.client, config, logger)
        self.detector = DetectionEngine()
        self.analyzer = Analyzer()
        self.semaphore = asyncio.Semaphore(config.workers)

    async def discover(self) -> dict[str, list[str]]:
        target = self.config.target
        if not target:
            raise ValueError("Target URL is required for discovery.")
        return await self.crawler.crawl(target)

    async def scan(self) -> ScanResult:
        target = self.config.target
        if not target:
            raise ValueError("Target URL is required for scanning.")

        discovery = await self.crawler.crawl(target)
        candidates = self._build_candidates(discovery)
        tasks: list[asyncio.Task[Finding | None]] = []
        for url, payload_category in candidates:
            tasks.append(asyncio.create_task(self._evaluate_url(url, payload_category)))

        findings: list[Finding] = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None and result.severity != "Informational":
                findings.append(result)

        scan_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        completed_at = datetime.now(timezone.utc)
        summary = ScanSummary(
            scan_id=scan_id,
            target=target,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=0.0,
            findings=findings,
            statistics={
                "urls_tested": len(candidates),
                "findings": len(findings),
                "payload_categories": len(self.payloads),
            },
        )
        return ScanResult(summary=summary, findings=findings, reports={})

    def _build_candidates(self, discovery: dict[str, list[Any]]) -> list[tuple[str, str]]:
        candidates: list[tuple[str, str]] = []
        payload_urls = self.payloads.get("basic", [])
        for url in discovery.get("urls", []):
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if query:
                for category, payloads in self.payloads.items():
                    for payload in payloads:
                        parameters = {key: payload for key in query}
                        candidate = urlunparse(
                            parsed._replace(query=urlencode(parameters, doseq=True))
                        )
                        candidates.append((candidate, category))
            else:
                for payload in payload_urls:
                    candidate = f"{url}?ssrf={payload}"
                    candidates.append((candidate, "basic"))
        for endpoint in discovery.get("json_endpoints", []):
            for category, payloads in self.payloads.items():
                for payload in payloads:
                    candidates.append((f"{endpoint}?payload={payload}", category))
        for form in discovery.get("forms", []):
            action = form.get("action") or self.config.target
            if not action.startswith("http"):
                action = self.client.resolve_url(self.config.target, action)
            for category, payloads in self.payloads.items():
                for payload in payloads[:2]:
                    candidates.append((action, category))
        return list(dict.fromkeys(candidates))

    async def _evaluate_url(self, url: str, category: str) -> Finding | None:
        async with self.semaphore:
            try:
                status, headers, body = await self.client.get(url)
            except Exception as error:
                self.logger.debug("Request failed for %s: %s", url, error)
                return None
            finding = self.detector.analyze(url, status, headers, body)
            self.logger.debug("Evaluated %s with severity %s", url, finding.severity)
            return finding

    async def close(self) -> None:
        await self.client.close()
