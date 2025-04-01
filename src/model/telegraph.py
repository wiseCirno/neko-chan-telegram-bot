import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.model.telegraph_tag import TelegraphTag


@dataclass
class Telegraph:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    # 原始标题
    raw_title: str = ""
    # 正则过滤过的标题
    title: str = ""
    # 添加时间
    time_added: datetime = field(default_factory=datetime.now)
    # 预览
    url: str = ""
    # 原始地址
    original: str = ""
    # 预览图片
    thumb: str = ""
    # 图片列表
    image_list: list[str] = field(default_factory=list)
    # 标签
    tags: TelegraphTag = field(default_factory=TelegraphTag)
    # 文件位置
    file_path: str = ""
