from __future__ import annotations

from typing import Any
from urllib.parse import urljoin, urlparse, urldefrag

from ssrfhunter.parser.extractor import ContentExtractor
from ssrfhunter.requester.client import AsyncHttpClient
from ssrfhunter.config.settings import ScanConfig


class Crawler:
    """Intelligent crawler for SSRF target discovery."""

    def __init__(self, client: AsyncHttpClient, config: ScanConfig, logger: Any) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.extractor = ContentExtractor()

    async def crawl(self, start_url: str) -> dict[str, list[Any]]:
        visited: set[str] = set()
        url_queue: list[tuple[str, int]] = [(start_url, 0)]
        discovered_urls: set[str] = set()
        forms: list[dict[str, Any]] = []
        json_endpoints: list[str] = []

        while url_queue:
            url, depth = url_queue.pop(0)
            normalized = self._normalize(url)
            if normalized in visited or depth > self.config.max_depth:
                continue
            visited.add(normalized)
            self.logger.debug("Crawling %s at depth %d", normalized, depth)
            try:
                status, headers, body = await self.client.get(normalized)
            except Exception as error:
                self.logger.debug("Skipping %s because of error: %s", normalized, error)
                continue

            content_type = headers.get("content-type", "")
            discovered_urls.add(normalized)
            if "text/html" in content_type:
                links = self.extractor.extract_links(body)
                forms.extend(self.extractor.extract_forms(body))
                for link in links:
                    absolute = self._resolve_url(normalized, link)
                    if self._should_follow(absolute):
                        url_queue.append((absolute, depth + 1))
            if "application/json" in content_type or body.strip().startswith("{"):
                json_endpoints.extend(self.extractor.extract_json_endpoints(body))
            if "/robots.txt" in normalized or normalized.endswith("sitemap.xml"):
                discovered_urls.update(self.extractor.extract_robots(body))
                sitemap_urls = self.extractor.extract_sitemap_urls(body)
                for sitemap_url in sitemap_urls:
                    absolute = self._resolve_url(normalized, sitemap_url)
                    if self._should_follow(absolute):
                        url_queue.append((absolute, depth + 1))

            openapi_urls = self.extractor.extract_openapi_urls(body)
            for api_url in openapi_urls:
                absolute = self._resolve_url(normalized, api_url)
                if self._should_follow(absolute):
                    json_endpoints.append(absolute)

        return {
            "urls": sorted(discovered_urls),
            "forms": forms,
            "json_endpoints": sorted(set(json_endpoints)),
        }

    def _normalize(self, url: str) -> str:
        cleaned, _ = urldefrag(url)
        return cleaned

    def _resolve_url(self, base: str, target: str) -> str:
        if target.startswith("/"):
            parsed = urlparse(base)
            return f"{parsed.scheme}://{parsed.netloc}{target}"
        return urljoin(base, target)

    def _should_follow(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if self.config.domain_restriction:
            base_host = urlparse(self.config.target).netloc
            return parsed.netloc == base_host
        return True
