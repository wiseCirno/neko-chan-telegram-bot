import os
import shutil
from datetime import datetime, timedelta


# -- Const -- #
DATABASE_PATH = "/container/app.db"
TELEGRAPH_DOWNLOAD_PATH = "/container/telegraph/download"
TELEGRAPH_KOMGA_PATH = "/container/telegraph/komga"


# -- Internal Variable -- #
DATABASE_TELEGRAPH_INITIALIZED: bool = False
PATH_INITIALIZED: bool = False


# -- Docker Environment -- #
# [Required]
BOT_TOKEN: str | None = os.getenv("BOT_TOKEN", None)

PROXY: str | None = os.getenv("PROXY", None)

MY_USER_ID = int(os.getenv("MY_USER_ID", None))
# [Optional]
AUTO_DOWNLOAD_CACHE_CLEAN = abs(int(os.getenv('AUTO_DOWNLOAD_CLEAN', 0)))

_BOT_TELEGRAPH_SAVE_FORMAT = os.getenv("BOT_TELEGRAPH_SAVE_FORMAT", "zip").lower()
BOT_TELEGRAPH_SAVE_FORMAT = _BOT_TELEGRAPH_SAVE_FORMAT if _BOT_TELEGRAPH_SAVE_FORMAT in ["zip", "epub", "no_file"] else "zip"

IMAGE_DOWNLOAD_BATCH_SIZE = abs(int(os.getenv('TELEGRAPH_DOWNLOAD_BATCH_SIZE', 1)))

IMAGE_DOWNLOAD_RETRY_COUNT = abs(int(os.getenv('TELEGRAPH_DOWNLOAD_RETRY_COUNT', 3)))

IS_DEBUG_MODE: bool = bool(os.getenv("IS_DEBUG_MODE", False))

SKIP_EXISTED_FILE = os.getenv("SKIP_EXISTED_FILE", False)

TELEGRAPH_HANDLER_BATCH_SIZE = abs(int(os.getenv('TELEGRAPH_HANDLER_BATCH_SIZE', 1)))

TELEGRAPH_HANDLER_RETRY_COUNT = abs(int(os.getenv('TELEGRAPH_HANDLER_RETRY_COUNT', 3)))

TELEGRAPH_HANDLER_IDLE_SLEEP_INTERVAL = abs(int(os.getenv('TELEGRAPH_HANDLER_IDLE_SLEEP_INTERVAL', 10)))

TELEGRAPH_HANDLER_IDLE_THRESHOLD = abs(int(os.getenv('TELEGRAPH_HANDLER_IDLE_THRESHOLD', 30)))

_TELEGRAPH_TASK_FALLBACK_ARTIST = os.getenv('TELEGRAPH_TASK_FALLBACK_ARTIST', "その他")
TELEGRAPH_TASK_FALLBACK_ARTIST = "その他" if _TELEGRAPH_TASK_FALLBACK_ARTIST.strip() == "" else _TELEGRAPH_TASK_FALLBACK_ARTIST


# [Compatible]
CHAT_ANYWHERE_KEY = os.getenv('CHAT_ANYWHERE_KEY', None)
CHAT_ANYWHERE_MODEL = os.getenv('CHAT_ANYWHERE_MODEL', "gpt-4o-mini")
CHAT_ANYWHERE_PROMPT = os.getenv(
    'CHAT_ANYWHERE_PROMPT',
    "请你扮演一个名为 Neko 的小动物角色，具有日本萌系风格，给人宅宅的感觉。"
    "在聊天中，适时使用日本常见的颜文字。"
    "请用简单自然的口语表达，灵活调整结束语，确保回答与上下文相关，模拟真实对话，增加互动性。"
)
CF_WORKER_PROXY = os.getenv('CF_WORKER_PROXY', None)
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
    if PATH_INITIALIZED:
        return
    else:
        if not os.path.exists(TELEGRAPH_DOWNLOAD_PATH):
            os.makedirs(TELEGRAPH_DOWNLOAD_PATH, exist_ok = True)
        if not os.path.exists(TELEGRAPH_KOMGA_PATH):
            os.makedirs(TELEGRAPH_KOMGA_PATH, exist_ok = True)
        PATH_INITIALIZED = True

    if AUTO_DOWNLOAD_CACHE_CLEAN != 0:
        for root, dirs, _ in os.walk(TELEGRAPH_DOWNLOAD_PATH):
            for temp_dir in dirs:
                path = os.path.join(root, temp_dir)
                modified_time = datetime.fromtimestamp(os.path.getmtime(path))
                if datetime.now() - modified_time > timedelta(days = AUTO_DOWNLOAD_CACHE_CLEAN):
                    shutil.rmtree(path)


_init()
