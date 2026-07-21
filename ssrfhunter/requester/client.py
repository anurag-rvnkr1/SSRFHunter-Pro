"""Reusable asynchronous HTTP client for safe SSRF testing."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import httpx

from ssrfhunter.exceptions import RequestError


class AsyncHttpClient:
    """Small async HTTP client with support for common HTTP methods."""

    def __init__(
        self,
        timeout: int = 10,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
        verify_ssl: bool = True,
        cookies: dict[str, str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.headers = headers or {}
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.cookies = cookies or {}
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self.headers,
            proxy=self.proxy,
            verify=self.verify_ssl,
            http2=True,
            cookies=self.cookies,
            follow_redirects=True,
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        data: Any = None,
        allow_redirects: bool = True,
    ) -> tuple[int, dict[str, str], str]:
        """Perform an HTTP request and return status, headers, and body."""
        merged_headers = {**self.headers, **(headers or {})}
        try:
            response = await self.client.request(
                method,
                url,
                headers=merged_headers,
                cookies={**self.cookies, **(cookies or {})},
                content=data,
                follow_redirects=allow_redirects,
            )
            return response.status_code, dict(response.headers), response.text
        except httpx.HTTPError as error:
            raise RequestError(f"HTTP request failed for {url}: {error}") from error

    async def get(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs: Any) -> tuple[int, dict[str, str], str]:
        return await self.request("OPTIONS", url, **kwargs)

    async def close(self) -> None:
        await self.client.aclose()

    def resolve_url(self, base_url: str, target: str) -> str:
        return urljoin(base_url, target)
