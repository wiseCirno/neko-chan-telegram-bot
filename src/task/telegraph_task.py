import os.path
from typing import Dict

from telegram import Message

from src import config as config
from src.service import TelegraphService, FileService, ImageService


class TelegraphTask:
    @staticmethod
    async def run(task_wrapper: Dict):
        """
        :raise ValueError: 不受支持的参数
        :return:
        """
        task_id: str = task_wrapper['id']
        srv: TelegraphService = task_wrapper['srv']
        message: Message = task_wrapper['update'].message
        task_type: str = task_wrapper['task_type']

        if srv is None or getattr(srv, 'telegraph', None) is None:
            srv = await TelegraphService.get_from_message(message.text_html_urled)
            if srv.telegraph is None:
                raise RuntimeError(f"Can not get Telegraph information from Task<{task_id}>.")
            task_wrapper['srv'] = srv

        if task_type == "no_file":
            await srv.add_to_database()
            return

        # 获取艺术家名称
        artist = srv.telegraph.tags.artist[0] if srv.telegraph.tags.artist else config.TELEGRAPH_TASK_FALLBACK_ARTIST
        file_name = srv.get_file_name()
        download_path = os.path.join(config.TELEGRAPH_DOWNLOAD_PATH, str(srv.telegraph.id))

        # 从图片列表下载
        await ImageService.download(srv.telegraph.image_list, download_path)

        if task_type == "zip":
            await FileService.write_zip_async(file_name, config.TELEGRAPH_KOMGA_PATH, download_path, artist)
            srv.telegraph.file_path = f"{config.TELEGRAPH_KOMGA_PATH}/{artist}/{file_name}.zip"
            await srv.add_to_database()
            return

        if task_type == "epub":
            await FileService.write_epub(srv, config.TELEGRAPH_KOMGA_PATH, download_path, artist)
            srv.telegraph.file_path = f"{config.TELEGRAPH_KOMGA_PATH}/{artist}/{file_name}.epub"
            await srv.add_to_database()
            return

        raise ValueError(f"Unsupported task type {task_type} from Task<{task_id}>")
