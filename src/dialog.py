from datetime import datetime
from typing import Callable, List

from telegram import Message

from src.model.telegraph import Telegraph
from src.service import TelegraphService


class KomgaDialog:
    @staticmethod
    def _greeting(m: Message):
        hour = datetime.now().hour
        if 0 <= hour < 6:
            return f"早点睡哦 {m.from_user.username}"
        elif 6 <= hour < 12:
            return f"おはよう，{m.from_user.username}"
        elif 12 <= hour < 18:
            return f"こんにちは、{m.from_user.username} マスター"
        elif 18 <= hour <= 23:
            return f"こんばんは、{m.from_user.username}"

    USER_UNAUTHORIZED: Callable[[Message], str] = staticmethod(
        lambda m: f"{m.from_user.username} 没有此权限"
    )
    USER_AUTHORIZED: Callable[[Message], str] = staticmethod(
        lambda m: f"{KomgaDialog._greeting(m)}\n把那些不忍直视的消息转发过来吧，我会好好记录你的 XP 的"
    )
    TASK_FAILED: Callable[[Exception], str] = staticmethod(
        lambda err: f"`{err}`\n\n如果你确定这条消息有效，请稍后再试试\n\n"
                    f"[🔍 Search error on Google](https://www.google.com/search?q=Python: {err})"
    )
    ALREADY_STARTED = "当前同步任务正在运行"
    NOT_STARTED = "没有正在运行的同步"
    EMPTY = "此命令需要参数 `/komga <param>`\n使用 /komga help 获取帮助"
    HELP = (
        "/komga help - 获取此命令的帮助信息\n"
        "/komga start - 启动 Telegraph 下载同步，空闲五分钟后自动关闭\n"
        "/komga stop - 手动关闭 Telegraph 下载同步\n"
        "/komga status - 查看当前任务队列状态\n"
        "/komga random - 随机返回一条已保存过的条目\n"
        "/komga search - 通过指定的搜索格式查询保存过的条目"
    )
    RANDOM: Callable[[List[Telegraph] | None], str] = staticmethod(
        lambda t: "亲爱的你的数据库是空的"
        if not t
        else TelegraphService.telegraph_message(t[0])
    )
    SEARCH: Callable[[List[Telegraph] | None], str] = staticmethod(
        lambda t: "没有查到符合的搜索结果"
        if not t
        else TelegraphService.telegraph_search_message(t)
    )
    SEARCH_FALLBACK = (
        "此命令需要参数 `/komga search <param>`，请按照下面的模板构造搜索条件：\n\n"
        "【注意】：\n"
        " · 仅修改值，不要修改键名或格式；\n"
        " · 标签值请用双引号，多个标签请用逗号分隔放在数组内；\n"
        " · 如果某个字段不需要筛选，保持为空或空数组即可。\n"
        "【模板】:\n"
        "```json\n"
        "{\n"
        '  "title": "",\n'
        '  "language": [],\n'
        '  "original": [],\n'
        '  "team": [],\n'
        '  "artist": [],\n'
        '  "others": [],\n'
        '  "male": [],\n'
        '  "female": [],\n'
        '  "mix": []\n'
        "}\n"
        "```\n\n"
        "【样例】：\n"
        "```json\n"
        "{\n"
        '  "title": "",\n'
        '  "language": ["汉语"],\n'
        '  "original": ["蔚蓝档案"],\n'
        '  "team": ["DOGYEAR"],\n'
        '  "artist": [],\n'
        '  "others": [],\n'
        '  "male": [],\n'
        '  "female": ["单女主"],\n'
        '  "mix": []\n'
        "}\n"
        "```\n"
        "请直接复制模板，然后修改对应的值后发送。"
    )
    STATUS: Callable[[int, int], str] = staticmethod(
        lambda length, size: f"{length} 个任务待处理，{size} 个活跃任务"
    )
    STOP: Callable[[bool], str] = staticmethod(
        lambda empty: f"停止接受新消息{' (现有任务队列不为空，你仍可能会收到来自任务的消息)' if not empty else ''}"
    )
    UNSUPPORTED: Callable[[str], str] = staticmethod(
        lambda param: f"不支持的参数 '{param}'"
    )
