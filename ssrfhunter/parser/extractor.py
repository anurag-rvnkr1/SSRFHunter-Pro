"""HTML and API content extraction utilities."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup


class ContentExtractor:
    """Extract links, forms, parameters, and JSON endpoints from content."""

    def extract_links(self, html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []
        for tag in soup.find_all("a"):
            href = tag.get("href")
            if isinstance(href, str) and href.startswith(("http://", "https://", "/")):
                links.append(href)
        return links

    def extract_forms(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        forms: list[dict[str, Any]] = []
        for form in soup.find_all("form"):
            action = form.get("action") or ""
            method_value = form.get("method")
            method = (method_value if isinstance(method_value, str) else "get").upper()
            inputs = []
            for input_tag in form.find_all("input"):
                inputs.append(
                    {"name": input_tag.get("name"), "type": input_tag.get("type", "text")}
                )
            forms.append({"action": action, "method": method, "inputs": inputs})
        return forms

    def extract_query_params(self, text: str) -> list[str]:
        matches = re.findall(r"([A-Za-z0-9_\-]+)=", text)
        return list(dict.fromkeys(matches))

    def extract_json_endpoints(self, text: str) -> list[str]:
        return re.findall(r"https?://[^\s'\"<>]+", text)

    def extract_openapi_paths(self, text: str) -> list[str]:
        matches = re.findall(r'"(/[A-Za-z0-9_\-/\.]+)"', text)
        return [path for path in set(matches)]

    def extract_openapi_urls(self, text: str) -> list[str]:
        return re.findall(r"https?://[^\s'\"<>]+/openapi(?:\.json|\.yaml|\.yml)?", text)

    def extract_sitemap_urls(self, text: str) -> list[str]:
        return re.findall(r"<loc>(https?://[^<]+)</loc>", text)

    def extract_robots(self, text: str) -> list[str]:
        return [
            line.split(":", 1)[1].strip()
            for line in text.splitlines()
            if line.startswith("Disallow:")
        ]

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed._replace(query="", fragment="").geturl()
