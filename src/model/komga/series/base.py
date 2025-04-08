import json
from typing import Optional

from ._sort import Sort
from .content import Content
from .pageable import Pageable


class KomgaSeries:
    def __init__(self):
        self.content: Optional[Content] = None
        self.empty: bool = False
        self.first: bool = False
        self.last: bool = False
        self.number: int = 0
        self.number_of_elements: int = 0
        self.pageable: Optional[Pageable] = None
        self.size: int = 0
        self.sort: Optional[Sort] = None
        self.total_elements: int = 0
        self.total_pages: int = 0

    @classmethod
    def from_json(cls, resp: json):
        instance = cls()
        instance.content = Content.from_json(resp["content"]) if resp.get("content") else None
        instance.empty = resp.get("empty", False)
        instance.first = resp.get("first", False)
        instance.last = resp.get("last", False)
        instance.number = resp.get("number", 0)
        instance.number_of_elements = resp.get("numberOfElements", 0)
        instance.pageable = Pageable.from_json(resp["pageable"]) if resp.get("pageable") else None
        instance.size = resp.get("size", 0)
        instance.sort = Sort.from_json(resp["sort"]) if resp.get("sort") else None
        instance.total_elements = resp.get("totalElements", 0)
        instance.total_pages = resp.get("totalPages", 0)
        return instance
