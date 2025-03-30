import asyncio
import os
import pathlib
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from zipfile import ZipFile, ZIP_DEFLATED

import aiofiles
from ebooklib import epub

from src import config as config
from .telegraph_service import TelegraphService


class FileService:
    @staticmethod
    def _is_string_empty_or_whitespace(value: str) -> bool:
        if value == "" or value.strip() == "":
            return True
        return False

    @staticmethod
    def _is_valid_path(value: str) -> bool:
        if pathlib.Path(value).is_dir():
            return True
        return False

    @staticmethod
    def _skip_existed_file(path: str) -> bool:
        if not os.path.exists(path):
            return False

        if config.SKIP_EXISTED_FILE:
            return True
        else:
            os.remove(path)
            return False

    @staticmethod
    def write_zip(file_name: str, target_path: str, origin_path: str, dir_name: Optional[str] = None):
        """
        从“源路径”中获取待压缩文件，并创建压缩文件。

        如果 dir_name 不为空 => 压缩文件存放于 "/目标路径/文件夹名称/文件名.zip"

        如果 dir_name 为空 => 压缩文件存放于 "/目标路径/文件名.zip"。

        :param file_name: 压缩文件打包后的文件名（不含后缀）
        :param target_path: 压缩文件目标存放的文件夹
        :param origin_path: 源文件所在的文件夹
        :param dir_name: 目标文件夹名称（可选）
        :raises RuntimeError: 如果在压缩过程中发生IO异常时抛出。
        """
        if FileService._is_string_empty_or_whitespace(file_name):
            raise ValueError(f"Invalid file name '{file_name}'")
        if not FileService._is_valid_path(target_path):
            raise ValueError(f"Invalid target path '{target_path}'")
        if not FileService._is_valid_path(origin_path):
            raise ValueError(f"Invalid origin path '{origin_path}'")

        create_path = os.path.join(target_path, dir_name) if dir_name else target_path
        os.makedirs(create_path, exist_ok = True)
        zip_path = os.path.join(create_path, f"{file_name}.zip")

        if FileService._skip_existed_file(zip_path):
            return

        try:
            with ZipFile(zip_path, 'w', ZIP_DEFLATED) as f:
                for root, _, files in os.walk(origin_path):
                    files.sort()
                    for file in files:
                        file_path = os.path.join(root, file)
                        f.write(file_path, os.path.relpath(file_path, origin_path))
        except Exception as e:
            raise RuntimeError(f"Create Zip file error because {e}.")

    @staticmethod
    async def write_zip_async(file_name: str, target_path: str, origin_path: str, dir_name: Optional[str] = None):
        """Async version of FileService.write_zip()"""
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, FileService.write_zip, file_name, target_path, origin_path, dir_name)

    @staticmethod
    async def write_epub(service: TelegraphService, target_path: str, origin_path: str, dir_name: Optional[str] = None):
        if not FileService._is_valid_path(target_path):
            raise ValueError(f"Invalid target path '{target_path}'")
        if not FileService._is_valid_path(origin_path):
            raise ValueError(f"Invalid origin path '{origin_path}'")

        telegraph = service.telegraph
        create_path = os.path.join(target_path, dir_name) if dir_name else target_path
        file_name = service.get_file_name()
        if FileService._skip_existed_file(os.path.join(create_path, file_name)):
            return

        sorted_images = sorted(
            [f for f in os.listdir(origin_path) if
             os.path.isfile(os.path.join(origin_path, f)) and f.endswith('.jpg')],
            key = lambda x: int(re.search(r'\d+', x).group())
        )
        book = epub.EpubBook()
        book.set_title(telegraph.title)

        if telegraph.tags.artist:
            for artist in telegraph.tags.artist:
                book.add_author(artist)

        if telegraph.tags.language.__contains__("汉语") or telegraph.tags.language.__contains__("翻译"):
            book.set_language("zh")

        async with aiofiles.open(os.path.join(origin_path, sorted_images[0]), "rb") as f:
            book.set_cover("cover.jpg", await f.read())

        for i, path in enumerate(sorted_images):
            html = epub.EpubHtml(title = f"Page {i + 1}", file_name = f"page_{i + 1}.xhtml",
                                 content = f"<html><body><img src='{path}'></body></html>".encode('utf8'))
            async with aiofiles.open(os.path.join(origin_path, path), "rb") as f:
                image = epub.EpubImage(uid = path, file_name = path, media_type = "image/jpg", content = await f.read())
                book.add_item(image)

            book.add_item(html)
            book.spine.append(html)
            book.toc.append(epub.Link(html.file_name, html.title, ''))

        book.add_item(epub.EpubNav())
        book.add_item(epub.EpubNcx())

        os.makedirs(create_path, exist_ok = True)
        epub.write_epub(f"{create_path}/{file_name}.epub", book, {})
