from datetime import datetime
from mailbox import Message
from typing import Callable


class Dialog:
    @staticmethod
    def _time_greetings() -> str:
        hour = datetime.now().hour
        if 0 <= hour < 6:
            return "夜猫子还没睡呢"
        elif 6 <= hour < 12:
            return "上午好"
        elif 12 <= hour < 14:
            return "中午好"
        elif 14 <= hour < 18:
            return "下午好"
        elif 18 <= hour <= 23:
            return "晚上好"

        return "Hi"

    # -- INFO -- #
    KOMGA_HANDLER_USER_UNAUTHORIZED: Callable[[Message], str] = (
        staticmethod(lambda m: f"{m.from_user.username} 没有此权限哦"))

    KOMGA_HANDLER_USER_AUTHORIZED: Callable[[Message], str] = (
        staticmethod(lambda m: f"{Dialog._time_greetings()}{m.from_user.username}, 请发送给我漫画消息吧)")
    )

    KOMGA_TASK_FAILED: Callable[[Exception], str] = (
        staticmethod(lambda err: f"`{err}`\n\n如果你确定这条消息有效，请稍后再试试\n\n"
                                 f"[🔍 Search error on Google](https://www.google.com/search?q=Python: {err})"))
