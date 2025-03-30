from typing import Dict

from httpx import AsyncClient

from src.config import PROXY
from .proxy_service import ProxyService


def new_async_client(headers: Dict) -> AsyncClient:
    if PROXY:
        return AsyncClient(proxy = ProxyService.new_proxy(PROXY), headers = headers)
    return AsyncClient(headers = headers)
