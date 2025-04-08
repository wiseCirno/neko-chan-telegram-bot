from typing import Dict, Optional

from httpx import AsyncClient

from src.config import PROXY
from .proxy_service import ProxyService


def new_async_client(
        headers: Optional[Dict] = None,
        base_url: Optional[str] = ""
) -> AsyncClient:
    if PROXY:
        return AsyncClient(
            headers = headers,
            proxy = ProxyService.new_proxy(PROXY),
            base_url = base_url
        )

    return AsyncClient(
        headers = headers,
        base_url = base_url
    )
