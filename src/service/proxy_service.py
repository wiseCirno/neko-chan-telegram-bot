from typing import Union

from httpx import URL, Proxy, Client, ProxyError
from httpx_socks import SyncProxyTransport


class ProxyService:
    @staticmethod
    def new_proxy(url: Union[URL, str], test_url: str = "https://api.telegram.org") -> Proxy:
        """
        给定 URL 创建一个代理
        :param url: 代理链接
        :param test_url: 测试网址，默认为 "https://api.telegram.org"
        :exception ProxyError: 代理没有指定协议，端口，或者代理不可用
        :return: httpx.Proxy
        """
        if isinstance(url, str):
            url = URL(url)

        if url.scheme not in ("http", "https", "socks5"):
            raise ProxyError(f"Unknown scheme for {url}.")

        if url.port is None:
            raise ProxyError(f"No port specified in {url}.")

        ProxyService._test(str(url), test_url)

        auth = None
        if url.username and url.password is not None:
            auth = (url.username, url.password)

        return Proxy(url = url, auth = auth)

    @staticmethod
    def _test(proxy_url: str, test_url: str) -> None:
        transport = SyncProxyTransport.from_url(proxy_url)

        try:
            with Client(transport = transport) as client:
                response = client.get(test_url, follow_redirects = True)
                response.raise_for_status()
        except Exception as exc:
            raise ProxyError(f"Error occurred when initializing proxy because {exc}.")
