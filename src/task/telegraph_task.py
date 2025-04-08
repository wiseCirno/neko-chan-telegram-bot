import os.path
from typing import Dict

from telegram import Message

from src.config import (
    TELEGRAPH_DOWNLOAD_PATH,
    KOMGA_PATH,
    TELEGRAPH_SAVE_FOLDER_TYPE,
    TELEGRAPH_TASK_FALLBACK_ARTIST
)
from src.model.telegraph import TelegraphHeaders
from src.service import TelegraphService, FileService, ImageService


class TelegraphTask:
    @staticmethod
    async def run(task_wrapper: Dict):
        task_id: str = task_wrapper['id']
        srv: TelegraphService = task_wrapper['srv']
        message: Message = task_wrapper['update'].message
        task_type: str = task_wrapper['task_type']

        if srv is None or getattr(srv, 'telegraph', None) is None:
            srv = await TelegraphService.get_from_message(message.text_html_urled)
            if srv.telegraph is None:
                raise RuntimeError(f"Can not get Telegraph information from Task<{task_id}>.")
            # 该消息和本任务无关，直接标记完成，跳过
            if srv.telegraph.url == "":
                task_wrapper['return'] = f"Task<{task_id}> completed，type: <skip>"
                return
            task_wrapper['srv'] = srv

        if task_type == "no_file":
            await srv.add_to_database()
            task_wrapper['return'] = f"Task<{task_id}> completed，type: <no_file>"
            return

        # 获取艺术家名称
        artist = srv.telegraph.tags.artist[0] if srv.telegraph.tags.artist else TELEGRAPH_TASK_FALLBACK_ARTIST
        file_name = srv.get_file_name()
        download_path = os.path.join(TELEGRAPH_DOWNLOAD_PATH, str(srv.telegraph.id))

        # 从图片列表下载，这里可能抛出异常
        await ImageService.download_to_local(srv.telegraph.image_list, download_path, "jpg", TelegraphHeaders.DOWNLOAD)
        dir_name = artist if TELEGRAPH_SAVE_FOLDER_TYPE == "artist" else file_name

        if task_type == "zip":
            await FileService.write_zip_async(file_name, KOMGA_PATH, download_path, dir_name)
            srv.telegraph.file_path = f"{KOMGA_PATH}/{dir_name}/{file_name}.zip"
            await srv.add_to_database()
            task_wrapper['return'] = f"Task<{task_id}> completed，type: <zip>"
            return

        if task_type == "epub":
            await FileService.convert_telegraph_to_epub(
                srv.telegraph, file_name, KOMGA_PATH, download_path, dir_name)
            srv.telegraph.file_path = f"{KOMGA_PATH}/{dir_name}/{file_name}.epub"
            await srv.add_to_database()
            task_wrapper['return'] = f"Task<{task_id}> completed，type: <epub>"
            return
