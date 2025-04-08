from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TelegraphTag:
    # 语言
    language: Optional[List[str]] = None
    # 原作
    original: Optional[List[str]] = None
    # 团队
    team: Optional[List[str]] = None
    # 艺术家
    artist: Optional[List[str]] = None
    # 其他
    others: Optional[List[str]] = None
    # 男性
    male: Optional[List[str]] = None
    # 女性
    female: Optional[List[str]] = None
    # 混合
    mix: Optional[List[str]] = None
    # 评分
    rating: float = 0.0
    # 页数
    pages: int = 0
