import os
import shutil
from datetime import datetime, timedelta

# -- Variable -- #
DATABASE_INITIALIZED: bool = False
KOMGA_LIBRARY_INITIALIZED: bool = False
PATH_INITIALIZED: bool = False

# -- Docker Environment -- #
# [Required]
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
"""从 https://t.me/BotFather 获取的机器人 Token: str"""
KOMGA_API_KEY = os.getenv("KOMGA_API_KEY", "")
"""从 https://your-komga-server-domain/account/api-keys 中获取"""
KOMGA_BASE_URL = os.getenv("KOMGA_BASE_URL", "")
"""自己的 Komga 服务器地址"""
KOMGA_CONTAINER_PATH = os.getenv("KOMGA_CONTAINER_PATH", "/komga")
"""Komga 容器中存放漫画的根目录（注意是容器中的位置）"""
MY_USER_ID = int(os.getenv("MY_USER_ID", -1))
"""机器人创建者的账户 ID: int"""
# [Optional]
AUTO_DOWNLOAD_CACHE_CLEAN = int(os.getenv('AUTO_DOWNLOAD_CACHE_CLEAN', 7))
"""自动清理下载缓存的天数: int && 自然数"""
IMAGE_DOWNLOAD_BATCH_SIZE = int(os.getenv('IMAGE_DOWNLOAD_BATCH_SIZE', 1))
"""全局图片图片下载批次大小: int && 正整数"""
IMAGE_DOWNLOAD_RETRY_COUNT = int(os.getenv('IMAGE_DOWNLOAD_RETRY_COUNT', 3))
"""单张图片下载重试次数: int && 正整数"""
IS_DEBUG_MODE = bool(os.getenv("IS_DEBUG_MODE", True))
"""是否开启 DEBUG 模式: bool"""
KOMGA_FOLDER_NAME = os.getenv("KOMGA_FOLDER_NAME", "Telegraph")
"""Komga 根目录创建的存放漫画的文件夹名称，不能有系统非法字符"""
KOMGA_LIBRARY_NAME = os.getenv("KOMGA_LIBRARY_NAME", "Telegraph")
"""Komga 放 Telegraph 漫画的库名"""
PROXY = os.getenv("PROXY", None)
"""代理地址，支持 HTTP 和 socks5 (e.g.: http://127.0.0.1:7890, socks5://127.0.0.1:7891): str | None"""
SKIP_EXISTED_FILE = bool(os.getenv("SKIP_EXISTED_FILE", False))
"""是否跳过已存在的文件，不跳过则会覆盖原文件: bool"""
TELEGRAPH_HANDLER_BATCH_SIZE = int(os.getenv('TELEGRAPH_HANDLER_BATCH_SIZE', 1))
"""Telegraph 任务的批次大小: int && 正整数"""
TELEGRAPH_HANDLER_RETRY_COUNT = int(os.getenv('TELEGRAPH_HANDLER_RETRY_COUNT', 3))
"""Telegraph 任务的重试次数: int && 正整数"""
TELEGRAPH_HANDLER_IDLE_SLEEP_INTERVAL = int(os.getenv('TELEGRAPH_HANDLER_IDLE_SLEEP_INTERVAL', 30))
"""Telegraph 空闲状态循环睡眠时间: int && 正整数"""
TELEGRAPH_HANDLER_IDLE_THRESHOLD = int(os.getenv('TELEGRAPH_HANDLER_IDLE_THRESHOLD', 30))
"""Telegraph 进入空闲状态的秒数: int && 正整数"""
TELEGRAPH_SAVE_EXTENSION = os.getenv("TELEGRAPH_SAVE_EXTENSION", "zip")
"""保存的文件扩展名: str && 限定 ["zip", "epub"] 二选一"""
TELEGRAPH_SAVE_FOLDER_TYPE = os.getenv("TELEGRAPH_SAVE_FOLDER_TYPE", "title")
"""保存文件的文件夹名称: str && 限定 ["artist", "title"] 二选一"""
TELEGRAPH_TASK_FALLBACK_ARTIST = os.getenv('TELEGRAPH_TASK_FALLBACK_ARTIST', "その他")
"""Telegraph 任务艺术家名称为空时的回调: str && NotNullOrWhitespace"""

# -- Files and Directories -- #
DATABASE = "/container/database.sqlite"
KOMGA_PATH = f"/container/komga/{KOMGA_FOLDER_NAME}"
LOG_PATH = "/container/logs"
TELEGRAPH_DOWNLOAD_PATH = "/container/download/telegraph"

# [MARK TO BE REMOVED]
CHAT_ANYWHERE_KEY = os.getenv('CHAT_ANYWHERE_KEY', None)
CHAT_ANYWHERE_MODEL = os.getenv('CHAT_ANYWHERE_MODEL', "gpt-4o-mini")
CHAT_ANYWHERE_PROMPT = os.getenv(
    'CHAT_ANYWHERE_PROMPT',
    "请你扮演一个名为 Neko 的小动物角色，具有日本萌系风格，给人宅宅的感觉。"
    "在聊天中，适时使用日本常见的颜文字。"
    "请用简单自然的口语表达，灵活调整结束语，确保回答与上下文相关，模拟真实对话，增加互动性。"
)
BOT_COMMAND = {
    '📺': "anime",
    '👋': "bye",
    '💬': "chat",
    '❤️': ["cuddle", "hug", "kiss", "pet", "snog"],
    '❔': "help",
    '📖': "komga",
    '🐉': "long",
    '👀': "start",
}


def _init():
    global PATH_INITIALIZED

    if not PATH_INITIALIZED:
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        if not os.path.exists(TELEGRAPH_DOWNLOAD_PATH):
            os.makedirs(TELEGRAPH_DOWNLOAD_PATH, exist_ok = True)
        if not os.path.exists(KOMGA_PATH):
            os.makedirs(KOMGA_PATH, exist_ok = True)
        PATH_INITIALIZED = True

    if AUTO_DOWNLOAD_CACHE_CLEAN != 0:
        for root, dirs, _ in os.walk(TELEGRAPH_DOWNLOAD_PATH):
            for temp_dir in dirs:
                path = os.path.join(root, temp_dir)
                modified_time = datetime.fromtimestamp(os.path.getmtime(path))
                if datetime.now() - modified_time > timedelta(days = AUTO_DOWNLOAD_CACHE_CLEAN):
                    shutil.rmtree(path)


_init()
