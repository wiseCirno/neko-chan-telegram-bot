import asyncio
import imghdr
import io
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import PIL.Image


@dataclass
class Image:
    is_jpg: bool = field(default = False)
    is_png: bool = field(default = False)
    is_gif: bool = field(default = False)
    is_bmp: bool = field(default = False)
    is_tiff: bool = field(default = False)
    is_webp: bool = field(default = False)
    is_unknown: bool = field(default = False)
    raw_bytes: bytes = field(default = None)

    @classmethod
    def get_type(cls, image_byte: bytes) -> str:
        """
        根据输入的 image_byte 判断图片格式。
        """
        img_type = imghdr.what(None, h = image_byte)
        if img_type == 'jpeg':
            return 'jpg'
        elif img_type in ('png', 'gif', 'bmp', 'tiff'):
            return img_type
        elif cls._is_webp(image_byte):
            return 'webp'
        else:
            return 'unknown'

    @staticmethod
    def _is_webp(image_byte: bytes) -> bool:
        """
        检测图片数据是否为 webp 格式。
        webp 通常以字节 "RIFF" 开头，并在偏移 8 处含有 "WEBP" 标记。
        """
        return (
                len(image_byte) >= 12 and
                image_byte[0:4] == b'RIFF' and
                image_byte[8:12] == b'WEBP'
        )

    @classmethod
    def from_bytes(cls, image_byte: bytes) -> "Image":
        """
        辅助方法，根据 image_byte 构造 ImageType 对象，
        同时设置各个格式标志位。如果图片格式未识别，则将 is_unknown 置 True。
        """
        img_format = cls.get_type(image_byte)
        return cls(
            is_jpg = (img_format == 'jpg'),
            is_png = (img_format == 'png'),
            is_gif = (img_format == 'gif'),
            is_bmp = (img_format == 'bmp'),
            is_tiff = (img_format == 'tiff'),
            is_webp = (img_format == 'webp'),
            is_unknown = (img_format == 'unknown'),
            raw_bytes = image_byte
        )

    @staticmethod
    async def convert(image_byte: bytes, target_extension: str) -> bytes:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                Image._convert_sync,
                image_byte,
                target_extension
            )
        return result

    @staticmethod
    def _convert_sync(image_byte: bytes, ext: str) -> bytes:
        try:
            image_stream = io.BytesIO(image_byte)
            with PIL.Image.open(image_stream) as img:
                if ext.lower() in ("jpg", "jpeg") and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                out_stream = io.BytesIO()
                save_format = "JPEG" if ext.lower() in ("jpg", "jpeg") else ext.upper()
                img.save(out_stream, format = save_format)
                return out_stream.getvalue()
        except Exception as e:
            raise RuntimeError(f"Format conversion failed: {e}")
