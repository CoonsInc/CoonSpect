import httpx

DEFAULT_TIMEOUT = httpx.Timeout(10.0)
LONG_TIMEOUT = httpx.Timeout(1800.0, read=1800.0)

_http_client = httpx.AsyncClient(timeout=LONG_TIMEOUT)


async def get_http_client() -> httpx.AsyncClient:
    return _http_client
