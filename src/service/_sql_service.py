from sqlite3 import Row
from typing import Any, List, Optional

import aiosqlite

from src.config import DATABASE


class SqlService:
    @staticmethod
    async def execute_reader(sql: str, parameters: Optional[List[Any]] = None) -> List[Row]:
        """
        执行查询操作，返回所有行数据。
        """
        parameters = parameters or []
        async with aiosqlite.connect(DATABASE) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(sql, parameters) as cursor:
                rows = await cursor.fetchall()
                return rows

    @staticmethod
    async def execute_non_query(sql: str, parameters: Optional[List[Any]] = None) -> int:
        """
        执行 INSERT、UPDATE 或 DELETE 操作，返回受影响的行数。
        """
        parameters = parameters or []
        async with aiosqlite.connect(DATABASE) as conn:
            async with conn.execute(sql, parameters) as cursor:
                await conn.commit()
                return cursor.rowcount

    @staticmethod
    async def execute_scalar(sql: str, parameters: Optional[List[Any]] = None) -> Any:
        """
        执行查询操作，仅返回第一行的第一列数据。
        """
        parameters = parameters or []
        async with aiosqlite.connect(DATABASE) as conn:
            async with conn.execute(sql, parameters) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return None
