import json
from datetime import datetime
from typing import List, Optional

from ._alternative_title import AlternativeTitle
from ._link import Link


class Metadata:
    def __init__(self):
        self.age_rating: int = 0
        self.age_rating_lock: bool = False
        self.alternate_titles: List[AlternativeTitle] = []
        self.alternate_titles_lock: bool = False
        self.created: Optional[datetime] = None
        self.genres: List[str] = []
        self.genres_lock: bool = False
        self.language: Optional[str] = None
        self.language_lock: bool = False
        self.last_modified: Optional[datetime] = None
        self.last_modified_lock: bool = False
        self.links: List[Link] = []
        self.links_lock: bool = False
        self.publisher: Optional[str] = None
        self.publisher_lock: bool = False
        self.reading_direction: Optional[str] = None
        self.reading_direction_lock: bool = False
        self.sharing_labels: List[str] = []
        self.sharing_labels_lock: bool = False
        self.status: Optional[str] = None
        self.status_lock: bool = False
        self.summary: Optional[str] = None
        self.summary_lock: bool = False
        self.tags: List[str] = []
        self.tags_lock: bool = False
        self.title: Optional[str] = None
        self.title_lock: bool = False
        self.title_sort: Optional[str] = None
        self.title_sort_lock: bool = False
        self.total_book_count: int = 0
        self.total_book_count_lock: bool = False

    @classmethod
    def from_json(cls, resp: json) -> "Metadata":
        instance = Metadata()
        instance.age_rating = resp.get("ageRating", 0)
        instance.age_rating_lock = resp.get("ageRatingLock", False)
        instance.alternate_titles = [
            AlternativeTitle.from_json(item)
            for item in resp.get("alternateTitles", [])
        ]
        instance.alternate_titles_lock = resp.get("alternateTitlesLock", False)
        instance.created = datetime.fromisoformat(resp["created"]) if resp.get("created") else None
        instance.genres = resp.get("genres", [])
        instance.genres_lock = resp.get("genresLock", False)
        instance.language = resp.get("language")
        instance.language_lock = resp.get("languageLock", False)
        instance.last_modified = datetime.fromisoformat(resp["lastModified"]) if resp.get("lastModified") else None
        instance.last_modified_lock = resp.get("lastModifiedLock", False)
        instance.links = [
            Link.from_json(item)
            for item in resp.get("links", [])
        ]
        instance.links_lock = resp.get("linksLock", False)
        instance.publisher = resp.get("publisher")
        instance.publisher_lock = resp.get("publisherLock", False)
        instance.reading_direction = resp.get("readingDirection")
        instance.reading_direction_lock = resp.get("readingDirectionLock", False)
        instance.sharing_labels = resp.get("sharingLabels", [])
        instance.sharing_labels_lock = resp.get("sharingLabelsLock", False)
        instance.status = resp.get("status")
        instance.status_lock = resp.get("statusLock", False)
        instance.summary = resp.get("summary")
        instance.summary_lock = resp.get("summaryLock", False)
        instance.tags = resp.get("tags", [])
        instance.tags_lock = resp.get("tagsLock", False)
        instance.title = resp.get("title")
        instance.title_lock = resp.get("titleLock", False)
        instance.title_sort = resp.get("titleSort")
        instance.title_sort_lock = resp.get("titleSortLock", False)
        instance.total_book_count = resp.get("totalBookCount", 0)
        instance.total_book_count_lock = resp.get("totalBookCountLock", False)
        return instance
