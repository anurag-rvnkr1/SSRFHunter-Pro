import pytest

from ssrfhunter.requester.client import AsyncHttpClient


@pytest.mark.asyncio
async def test_async_http_client_request(monkeypatch):
    class FakeResponse:
        def __init__(self) -> None:
            self.status_code = 200
            self.headers = {"content-type": "text/plain"}
            self.text = "OK"

    class FakeClient:
        async def request(self, method, url, **kwargs):
            assert method == "GET"
            assert url == "https://example.com"
            return FakeResponse()

        async def aclose(self) -> None:
            return None

    monkeypatch.setattr(
        "ssrfhunter.requester.client.httpx.AsyncClient", lambda **kwargs: FakeClient()
    )
    client = AsyncHttpClient(timeout=5, headers={"Foo": "bar"})
    status, headers, body = await client.get("https://example.com")
    assert status == 200
    assert body == "OK"
    assert headers["content-type"] == "text/plain"
    await client.close()
