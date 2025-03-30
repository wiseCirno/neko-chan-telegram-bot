import asyncio
import json
import re
from typing import List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from src import config as config
from src.model import Telegraph, TelegraphHeaders
from ._client import new_async_client
from ._parser import TelegraphParser
from ._sql_service import SqlService


class TelegraphService:
    def __init__(self, telegraph: Telegraph):
        self.telegraph: Telegraph | None = telegraph
        self._navigate_list: List[str] = []

    @classmethod
    async def get_from_message(cls, message: str) -> "TelegraphService":
        """
        通过消息内容生成必要的 Telegraph 类，如果获取失败的话 self.telegraph 会变成 None
        :param message: text_html_urled 字段的消息段
        :return:
        """
        telegraph = TelegraphParser(message).parse()
        service = cls(telegraph)
        await service._get_information()
        return service

    import re

    def _get_title_from_raw_title(self) -> None:
        raw = self.telegraph.raw_title
        dash_index = raw.rfind("–")
        if dash_index == -1:
            dash_index = raw.rfind("-")
        if dash_index != -1:
            raw = raw[:dash_index].strip()

        preprocessed_title = raw
        patterns = [
            r"^\s*$[^)]*$\s*$[^$]+\]\s*(.+?)(?=\s*$)",
            r"^\s*$$[^$]+$$\s*(.+?)(?=\s*$)",
            r"(?<=$)\s*(.+?)\s*(?=$)",
            r"(?<=$)\s*(.+?)\s*(?=\()",
            r"(?<=\])\s*(.+?)(?=\s*\[)"
        ]

        for pattern in patterns:
            match = re.search(pattern, preprocessed_title)
            if match:
                title = match.group(1).strip()
                if title:
                    self.telegraph.title = title
                    break
        else:
            self.telegraph.title = preprocessed_title

    async def _get_information(self) -> None:
        async with new_async_client(TelegraphHeaders.DEFAULT) as client:
            # 解析出来发现这个 url 不是想要的 url，直接把字段清空方便后面的处理逻辑
            if not self.telegraph.url.startswith("https://telegra.ph"):
                self.telegraph.url = ""
                return

            response = await client.get(self.telegraph.url)
            if response.status_code != 200:
                self.telegraph = None
                return

            soup = BeautifulSoup(response.text, "html.parser")
            for a_tag in soup.find("body").find_all("a", href = True):
                full_url = urljoin(str(response.url), a_tag["href"])
                if full_url.startswith("https://telegra.ph"):
                    self._navigate_list.append(full_url)

            if not self._navigate_list:
                pages_to_fetch = [response]
            else:
                pages_to_fetch = await asyncio.gather(
                    *[client.get(url) for url in self._navigate_list]
                )

            self.telegraph.image_list = [
                urljoin(str(r_ex.url), img_src)
                for r_ex in pages_to_fetch
                for img_src in re.findall(r'img src="(.*?)"', r_ex.text)
            ]
            if not self.telegraph.image_list:
                self.telegraph = None
                return
            else:
                self.telegraph.image_list = [u for u in self.telegraph.image_list if TelegraphService._is_valid_url(u)]

            self.telegraph.raw_title = soup.find("title").text
            self.telegraph.thumb = self.telegraph.image_list[0]
            if self.telegraph.tags.pages == 0:
                self.telegraph.tags.pages = len(self.telegraph.image_list)

        self._get_title_from_raw_title()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)

    @staticmethod
    async def _initialize_table() -> None:
        telegraph_sql = """
        CREATE TABLE IF NOT EXISTS Telegraph (
            id TEXT PRIMARY KEY,
            raw_title TEXT NOT NULL,
            title TEXT NOT NULL,
            time_added DATETIME NOT NULL,
            url TEXT NOT NULL,
            original TEXT,
            thumb TEXT NOT NULL,
            image_list TEXT NOT NULL,
            file_path TEXT
        );
        """
        telegraph_tag_sql = """
        CREATE TABLE IF NOT EXISTS TelegraphTag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegraph_id TEXT NOT NULL,
            language TEXT,
            original TEXT,
            team TEXT,
            artist TEXT,
            others TEXT,
            male TEXT,
            female TEXT,
            mix TEXT,
            rating REAL DEFAULT 0.0,
            pages INTEGER DEFAULT 0,
            FOREIGN KEY (telegraph_id) REFERENCES Telegraph(id)
        );
        """
        await SqlService.execute_non_query(telegraph_sql)
        await SqlService.execute_non_query(telegraph_tag_sql)
        config.DATABASE_TELEGRAPH_INITIALIZED = True

    async def add_to_database(self) -> None:
        if not config.DATABASE_TELEGRAPH_INITIALIZED:
            await self._initialize_table()

        insert_sql = """
        INSERT INTO Telegraph (id, raw_title, title, time_added, url, original, thumb, image_list, file_path) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = [
            str(self.telegraph.id),
            self.telegraph.raw_title,
            self.telegraph.title,
            self.telegraph.time_added.isoformat(),
            self.telegraph.url,
            self.telegraph.original,
            self.telegraph.thumb,
            json.dumps(self.telegraph.image_list),
            self.telegraph.file_path
        ]
        await SqlService.execute_non_query(insert_sql, parameters)
        insert_sql = """
        INSERT INTO TelegraphTag 
        (telegraph_id, language, original, team, artist, others, male, female, mix, rating, pages) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """
        parameters = [
            str(self.telegraph.id),
            json.dumps(self.telegraph.tags.language),
            json.dumps(self.telegraph.tags.original),
            json.dumps(self.telegraph.tags.team),
            json.dumps(self.telegraph.tags.artist),
            json.dumps(self.telegraph.tags.others),
            json.dumps(self.telegraph.tags.male),
            json.dumps(self.telegraph.tags.female),
            json.dumps(self.telegraph.tags.mix),
            json.dumps(self.telegraph.tags.rating),
            json.dumps(self.telegraph.tags.pages)
        ]
        await SqlService.execute_non_query(insert_sql, parameters)

    def get_file_name(self) -> str:
        """
        根据 self.telegraph.title 生成合法的文件名，自动替换操作系统非法字符。
        """
        file_name = re.sub(r'[\\/:*?"<>|]', '_', self.telegraph.title).strip()
        max_length = 255
        if len(file_name) > max_length:
            file_name = file_name[:max_length]
        return file_name
