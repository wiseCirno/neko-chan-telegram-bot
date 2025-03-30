import re
import urllib.parse

from src.model import Telegraph


class TelegraphParser:
    _DICT = {
        # TelegraphTag
        "语言": "language",
        "原作": "original",
        "团队": "team",
        "艺术家": "artist",
        "其他": "others",
        "男性": "male",
        "女性": "female",
        "混合": "mix",
        "评分": "rating",
        "页数": "pages",
        # Telegraph
        "预览": "url",
        "原始地址": "original"
    }

    def __init__(self, html_text: str):
        self._html_text = html_text
        self._pre_format()

    def _pre_format(self) -> None:
        self._html_text = re.sub(
            r':\s+(?=[#<])',
            ':',
            re.sub(
                r'<code>(.*?)</code>',
                lambda m: "".join(m.group(1).split()),
                self._html_text,
                flags = re.DOTALL
            )
        )

    def _fallback(self) -> Telegraph:
        """
        Telegram 的链接是无法以纯文本的方式发送的，也就是如果这是一个合法的链接格式，消息就一定会以 href 包裹
        在客户端中会表现为这个链接的颜色不是白色的文本，而且可以被点击
        :return: Telegraph 类
        """
        m = re.search(r'href="([^"]+)"', self._html_text)
        return Telegraph(url = urllib.parse.unquote(m.group(1)) if m else "")

    def parse(self) -> Telegraph:
        """
        解析 _html_text 中的内容，根据 _DICT 映射将数据填充到 Telegraph 对象中。
        规则说明：
         - 每行格式：键:值
         - 对于标签字段（语言、原作、团队、艺术家、男性、女性、其他、混合、评分、页数），
           预设用以空格分隔的片段，其中标签前缀为 '#'，我们会去掉 '#' 并构造成列表。
         - 对于预览和原始地址，值为 <a> 标签，使用正则提取 href 属性。
        """
        telegraph = Telegraph()

        for line in self._html_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if ':' not in line:
                continue

            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if key in self._DICT:
                attr_name = self._DICT[key]

                if key in ("预览", "原始地址"):
                    m = re.search(r'href="([^"]+)"', value)
                    url = urllib.parse.unquote(m.group(1)) if m else value
                    setattr(telegraph, attr_name, url)
                else:
                    if key in ("评分", "页数"):
                        converted = float(value) if key == "评分" else int(value)
                        setattr(telegraph.tags, attr_name, converted)
                    else:
                        if value:
                            tags = [tag.lstrip('#') for tag in value.split() if tag.startswith('#')]
                            setattr(telegraph.tags, attr_name, tags)

        if telegraph.url:
            return telegraph

        return self._fallback()
