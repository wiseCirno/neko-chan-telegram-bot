import asyncio
import html
import json
import re
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from src import config as config
from src.model.telegraph import Telegraph, TelegraphHeaders, TelegraphTag
from ._parser import TelegraphParser
from ._sql_service import SqlService
from .client_service import new_async_client


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

    def _get_title_from_raw_title(self) -> None:
        raw = self.telegraph.raw_title
        dash_index = raw.rfind("–")
        if dash_index == -1:
            dash_index = raw.rfind("-")
        if dash_index != -1:
            raw = raw[:dash_index].strip()

        self.telegraph.raw_title = raw
        patterns = [
            r"^\s*$[^)]*$\s*$[^$]+\]\s*(.+?)(?=\s*$)",
            r"^\s*$$[^$]+$$\s*(.+?)(?=\s*$)",
            r"(?<=$)\s*(.+?)\s*(?=$)",
            r"(?<=$)\s*(.+?)\s*(?=\()",
            r"(?<=\])\s*(.+?)(?=\s*\[)"
        ]

        for pattern in patterns:
            match = re.search(pattern, self.telegraph.raw_title)
            if match:
                title = match.group(1).strip()
                if title:
                    self.telegraph.title = title
                    break
        else:
            self.telegraph.title = self.telegraph.raw_title

    @staticmethod
    def _map_to_telegraph_tag(tags: Dict) -> TelegraphTag:
        return TelegraphTag(
            language = json.loads(tags["language"]) if tags["language"] != 'null' else None,
            original = json.loads(tags["original"]) if tags["original"] != 'null' else None,
            team = json.loads(tags["team"]) if tags["team"] != 'null' else None,
            artist = json.loads(tags["artist"]) if tags["artist"] != 'null' else None,
            others = json.loads(tags["others"]) if tags["others"] != 'null' else None,
            male = json.loads(tags["male"]) if tags["male"] != 'null' else None,
            female = json.loads(tags["female"]) if tags["female"] != 'null' else None,
            mix = json.loads(tags["mix"]) if tags["mix"] != 'null' else None,
            rating = tags["rating"],
            pages = tags["pages"]
        )

    @staticmethod
    def _map_to_telegraph(data: Dict) -> Telegraph:
        return Telegraph(
            id = uuid.UUID(data['id']),
            raw_title = data['raw_title'],
            title = data['title'],
            time_added = datetime.fromisoformat(data['time_added']),
            url = data['url'],
            original = data['original'],
            thumb = data['thumb'],
            image_list = json.loads(data['image_list']),
            file_path = data['file_path']
        )

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
        config.DATABASE_INITIALIZED = True

    async def add_to_database(self) -> None:
        if not config.DATABASE_INITIALIZED:
            await self._initialize_table()

        query_sql = "SELECT title, file_path FROM Telegraph WHERE title = ?"
        rows = await SqlService.execute_reader(query_sql, [self.telegraph.title])

        # 避免重复插入
        if rows:
            row = rows[0]
            db_file_path = row["file_path"]
            db_original = row["original"]
            updates = {}
            if not db_file_path and self.telegraph.file_path:
                updates["file_path"] = self.telegraph.file_path
            if not db_original and self.telegraph.original:
                updates["original"] = self.telegraph.original
            if updates:
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                update_sql = f"UPDATE Telegraph SET {set_clause} WHERE title = ?"
                parameters = list(updates.values()) + [self.telegraph.title]
                await SqlService.execute_non_query(update_sql, parameters)
            else:
                return

        insert_sql = """
        INSERT INTO Telegraph 
        (id, raw_title, title, time_added, url, original, thumb, image_list, file_path) 
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

        insert_tag_sql = """
        INSERT INTO TelegraphTag 
        (telegraph_id, language, original, team, artist, others, male, female, mix, rating, pages) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        tag_parameters = [
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
        await SqlService.execute_non_query(insert_tag_sql, tag_parameters)

    @staticmethod
    async def query_from_database(
            title: Optional[str] = None,
            tags: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Telegraph]]:
        """
        从 Telegraph 和 TelegraphTag 表中进行联查，
        若两个参数都为 None 则返回一条随机记录。

        :param title: 搜索标题（模糊查询）
        :param tags: 根据标签搜索记录，采用等值匹配
        :return: telegraph 列表，未查到数据时返回 None
        """
        if not config.DATABASE_INITIALIZED:
            await TelegraphService._initialize_table()

        base_sql = """
        SELECT
            json_object(
                'id', t.id,
                'raw_title', t.raw_title,
                'title', t.title,
                'time_added', t.time_added,
                'url', t.url,
                'original', t.original,
                'thumb', t.thumb,
                'image_list', t.image_list,
                'file_path', t.file_path
            ) AS telegraph,
            json_object(
                'id', tt.id,
                'telegraph_id', tt.telegraph_id,
                'language', tt.language,
                'original', tt.original,
                'team', tt.team,
                'artist', tt.artist,
                'others', tt.others,
                'male', tt.male,
                'female', tt.female,
                'mix', tt.mix,
                'rating', tt.rating,
                'pages', tt.pages
            ) AS telegraph_tag
        FROM Telegraph t
        JOIN TelegraphTag tt ON t.id = tt.telegraph_id
        """

        params = []
        where_clauses = []

        # 随机返回一条记录
        if not title and not tags:
            sql = base_sql + " ORDER BY RANDOM() LIMIT 1"
            result = await SqlService.execute_reader(sql)
            if not result:
                return None

            telegraph_obj = TelegraphService._map_to_telegraph(json.loads(result[0]['telegraph']))
            telegraph_obj.tags = TelegraphService._map_to_telegraph_tag(json.loads(result[0]['telegraph_tag']))
            return [telegraph_obj]

        if title:
            where_clauses.append("t.title LIKE ?")
            params.append(f"%{title}%")

        if tags:
            for field, value in tags.items():
                if value and isinstance(value, list):
                    for val in value:
                        where_clauses.append(f"tt.{field} LIKE ?")
                        params.append(f"%{json.dumps(val)}%")

        if not where_clauses:
            return None

        base_sql += " WHERE " + " AND ".join(where_clauses)
        result = await SqlService.execute_reader(base_sql, params)
        if not result:
            return None

        telegraphs = []
        for r in result:
            telegraph_obj = TelegraphService._map_to_telegraph(json.loads(r['telegraph']))
            telegraph_obj.tags = TelegraphService._map_to_telegraph_tag(json.loads(r['telegraph_tag']))
            telegraphs.append(telegraph_obj)

        return telegraphs

    def get_file_name(self) -> str:
        """
        根据 self.telegraph.title 生成合法的文件名，自动替换操作系统非法字符。
        """
        file_name = re.sub(r'[\\/:*?"<>|]', '_', self.telegraph.title).strip()
        max_length = 255
        if len(file_name) > max_length:
            file_name = file_name[:max_length]
        return file_name

    @staticmethod
    def telegraph_message(telegraph: Telegraph) -> str:
        m = ""
        tags = telegraph.tags

        def format_tags(label: str, tag_list: Optional[List[str]]) -> str:
            if tag_list:
                escaped_label = html.escape(label)
                tags_str = " ".join(f"#{html.escape(tag)}" for tag in tag_list)
                return f"<code>{escaped_label}</code>: {tags_str}\n"
            return ""

        m += format_tags("语言", tags.language)
        m += format_tags("原作", tags.original)
        m += format_tags("团队", tags.team)
        m += format_tags("艺术家", tags.artist)
        m += format_tags("其他", tags.others)
        m += format_tags("男性", tags.male)
        m += format_tags("女性", tags.female)
        m += format_tags("混合", tags.mix)

        escaped_title = html.escape(telegraph.raw_title)
        m += f"<code>预览</code>: <a href=\"{telegraph.url}\">{escaped_title}</a>\n"
        if telegraph.original != "":
            m += f"<code>原始地址</code>: <a href=\"{telegraph.original}\">{telegraph.original}</a>\n"

        if tags.rating != 0.0:
            m += f"<code>评分</code>: {tags.rating}\n"
        m += f"<code>页数</code>: {tags.pages}\n"

        return m

    @staticmethod
    def telegraph_search_message(telegraphs: List[Telegraph]) -> str:
        m = ""
        for i, telegraph in enumerate(telegraphs):
            m += f"<code>结果{i}</code>: <a href=\"{telegraph.url}\">{telegraph.title}</a>\n\n"

        return m
