import json
from datetime import datetime
from typing import Optional

from .book_metadata import BookMetadata
from .metadata import Metadata


class Content:
    def __init__(self):
        self.books_count: int = 0
        self.books_in_progress_count: int = 0
        self.books_metadata: Optional[BookMetadata] = None
        self.books_read_count: int = 0
        self.books_unread_count: int = 0
        self.created: Optional[datetime] = None
        self.deleted: bool = False
        self.file_last_modified: Optional[datetime] = None
        self.id: Optional[str] = None
        self.last_modified: Optional[datetime] = None
        self.library_id: Optional[str] = None
        self.metadata: Optional[Metadata] = None
        self.name: Optional[str] = None
        self.oneshot: bool = False
        self.url: Optional[str] = None

    @classmethod
    def from_json(cls, resp: json):
        instance = cls()
        instance.books_count = resp.get("booksCount", 0)
        instance.books_in_progress_count = resp.get("booksInProgressCount", 0)
        instance.books_metadata = BookMetadata.from_json(resp["booksMetadata"]) if resp.get("booksMetadata") else None
        instance.books_read_count = resp.get("booksReadCount", 0)
        instance.books_unread_count = resp.get("booksUnreadCount", 0)
        instance.created = datetime.fromisoformat(resp["created"]) if resp.get("created") else None
        instance.deleted = resp.get("deleted", False)
        instance.file_last_modified = datetime.fromisoformat(resp["fileLastModified"]) if resp.get(
            "fileLastModified") else None
        instance.id = resp.get("id")
        instance.last_modified = datetime.fromisoformat(resp["lastModified"]) if resp.get("lastModified") else None
        instance.library_id = resp.get("libraryId")
        instance.metadata = Metadata.from_json(resp["metadata"]) if resp.get("metadata") else None
        instance.name = resp.get("name")
        instance.oneshot = resp.get("oneshot", False)
        instance.url = resp.get("url")
        return instance
