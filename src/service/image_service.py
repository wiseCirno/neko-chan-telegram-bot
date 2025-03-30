import asyncio
import os
from typing import List

import aiofiles
from httpx import AsyncClient
from loguru import logger

from src import config as config
from src.model import TelegraphHeaders, Image
from ._client import new_async_client


class ImageService:
    @staticmethod
    async def _download_handler(urls: List[str], path: str, retries: int, ext: str) -> None:
        async def worker(q: asyncio.Queue, c: AsyncClient):
            while True:
                i, u, r = await q.get()
                # 退出循环就看这个
                if not u:
                    q.task_done()
                    break

                dest_path = os.path.join(path, f"{i}.jpg")
                if os.path.exists(dest_path):
                    q.task_done()
                    continue

                try:
                    response = await c.get(u)
                except Exception as e:
                    if r == retries:
                        q.task_done()
                        raise ConnectionError(f"Connection error for {u} because {e}.")
                    else:
                        q.task_done()
                        q.put_nowait((i, u, r + 1))
                        continue

                if response.status_code != 200 or not response.content:
                    if r == retries:
                        q.task_done()
                        raise EOFError(f"Failed to download {u} because of remote server limitations.")
                    else:
                        q.task_done()
                        q.put_nowait((i, u, r + 1))
                        continue

                # 根据图片类型决定是否需要转换
                image_type = Image.get_type(response.content)

                # 我很讨厌你说我不信下载的 content 还能出问题，返回 unknown 说明这张图像就是破损了，不要狡辩
                if image_type == "unknown":
                    q.task_done()
                    if r < retries:
                        q.put_nowait((i, u, r + 1))
                    continue

                # 同格式无需转换
                if ext == image_type:
                    b = response.content
                else:
                    b = await ImageService.convert(response.content, ext)

                async with aiofiles.open(dest_path, "wb") as f:
                    await f.write(b)
                    logger.debug(f"Write {dest_path} from URL {u}.")

                q.task_done()

        download_queue = asyncio.Queue()
        for index, url in enumerate(urls):
            download_queue.put_nowait((index, url, 0))

        # 根据批处理数量设置 worker 的数量
        worker_count = config.IMAGE_DOWNLOAD_BATCH_SIZE

        # 让 worker 退出循环
        for _ in range(worker_count):
            download_queue.put_nowait((None, None, None))

        # 创建 HTTP client 并启动 worker 任务
        async with new_async_client(TelegraphHeaders.DOWNLOAD) as client:
            tasks = [
                asyncio.create_task(worker(download_queue, client))
                for _ in range(worker_count)
            ]
            await asyncio.gather(*tasks)

    @staticmethod
    def _is_integral(count: int, path: str) -> bool:
        for root, _, files in os.walk(path):
            if len(files) != count:
                return False
            for file in files:
                if os.path.getsize(os.path.join(root, file)) == 0:
                    return False
        return True

    @staticmethod
    async def download(urls: List[str], dir_path: str, extension: str = "jpg") -> None:
        """
        给定链接列表将图片下载到指定位置
        :param urls: 图片列表
        :param dir_path: 下载路径
        :param extension: 目标文件扩展名（默认".jpg"），支持 "jpg", "png", "gif", "bmp", "tiff", "webp"
        :exception EOFError: 下载出现非 200 返回值或返回内容为空
        :exception ConnectionError: 网络异常连接失败
        :exception ValueError: 文件完整性错误
        :return:
        """
        os.makedirs(dir_path, exist_ok = True)
        await ImageService._download_handler(urls, dir_path, config.IMAGE_DOWNLOAD_RETRY_COUNT, extension)
        if ImageService._is_integral(len(urls), dir_path):
            return
        raise ValueError(f"Images at {dir_path} are not integrated.")

    @staticmethod
    async def convert(image_byte: bytes, target_extension: str) -> bytes:
        """
        转换图片格式到 target_extension 指定的格式，
        """
        return await Image.convert(image_byte, target_extension)
