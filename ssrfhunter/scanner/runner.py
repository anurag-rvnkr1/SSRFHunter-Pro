from __future__ import annotations

from ssrfhunter.config.settings import ScanConfig
from ssrfhunter.crawler.crawler import Crawler
from ssrfhunter.logging.setup import build_logger
from ssrfhunter.requester.client import AsyncHttpClient


class Scanner:
    """Scanner wrapper for orchestration and configuration."""

    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self.logger = build_logger(verbose=config.verbose, debug=config.debug)
        self.http_client = AsyncHttpClient(
            timeout=config.timeout,
            headers={"User-Agent": config.user_agent, **config.headers},
            proxy=config.proxy,
            verify_ssl=True,
        )
        self.crawler = Crawler(self.http_client, config, self.logger)

    async def discover(self) -> dict[str, list[str]]:
        return await self.crawler.crawl(self.config.target)
