import json
from datetime import datetime, date
from typing import List, Optional

from ._author import Author


class BookMetadata:
    def __init__(self):
        self.authors: List[Author] = []
        self.created: Optional[datetime] = None
        self.last_modified: Optional[datetime] = None
        self.release_date: Optional[date] = None
        self.summary: Optional[str] = None
        self.summary_number: Optional[str] = None
        self.tags: List[str] = []

    @classmethod
    def new(
            cls,
            authors: List[Author],
            created: datetime,
            last_modified: Optional[datetime],
            release_date: Optional[date],
            summary: Optional[str],
            summary_number: Optional[str],
            tags: List[str],
    ) -> "BookMetadata":
        instance = BookMetadata()
        instance.authors = authors
        instance.created = created
        instance.last_modified = last_modified
        instance.release_date = release_date
        instance.summary = summary
        instance.summary_number = summary_number
        instance.tags = tags
        return instance

    @classmethod
    def from_json(cls, resp: json) -> "BookMetadata":
        instance = BookMetadata()
        instance.authors = [
            Author.from_json(author_data)
            for author_data in resp.get("authors", [])
        ]
        instance.created = datetime.fromisoformat(resp["created"]) if resp.get("created") else None
        instance.last_modified = datetime.fromisoformat(resp["lastModified"]) if resp.get("lastModified") else None
        instance.release_date = date.fromisoformat(resp["releaseDate"]) if resp.get("releaseDate") else None
        instance.summary = resp.get("summary")
        instance.summary_number = resp.get("summaryNumber")
        instance.tags = resp.get("tags", [])
        return instance
