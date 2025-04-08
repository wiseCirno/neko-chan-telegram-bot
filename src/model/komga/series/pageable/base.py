import json
from typing import Optional

from .._sort import Sort


class Pageable:
    def __init__(self):
        self.offset: int = 0
        self.page_number: int = 0
        self.page_size: int = 20  # 设置一个合理的默认值
        self.paged: bool = False
        self.sort: Optional[Sort] = None
        self.unpaged: bool = True

    @classmethod
    def from_json(cls, resp: json) -> "Pageable":
        instance = cls()
        instance.offset = resp.get("offset", 0)
        instance.page_number = resp.get("pageNumber", 0)
        instance.page_size = resp.get("pageSize", 20)
        instance.paged = resp.get("paged", False)
        instance.sort = Sort.from_json(resp["sort"]) if resp.get("sort") else None
        instance.unpaged = resp.get("unpaged", True)
        return instance
