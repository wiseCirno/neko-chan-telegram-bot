import json
from typing import Optional, List


class KomgaLibrary:
    def __init__(self):
        self.analyze_dimensions: bool = True
        """分析页面尺寸"""
        self.convert_to_cbz: bool = False
        """自动转换为 CBZ 格式"""
        self.empty_trash_after_scan: bool = True
        """每次扫描后自动清理垃圾"""
        self.hash_files: bool = True
        """计算文件哈希"""
        self.hash_koreader: bool = False
        """计算 KOReader 文件的哈希值"""
        self.hash_pages: bool = True
        """计算页面哈希"""
        self.id: str = ""
        """库的 ID"""
        self.import_barcode_isbn: bool = True
        """从条形码中导入 ISBN"""
        self.import_comic_info_book: bool = False
        """书籍元数据"""
        self.import_comic_info_collection: bool = False
        """收藏"""
        self.import_comic_info_read_list: bool = False
        """阅读列表"""
        self.import_comic_info_series: bool = False
        """系列元数据"""
        self.import_comic_info_series_append_volume: bool = False
        """在系列标题中添加卷号"""
        self.import_epub_book: bool = True
        """导入书籍元数据"""
        self.import_epub_series: bool = True
        """导入系列元数据"""
        self.import_local_artwork: bool = True
        """导入本地媒体"""
        self.import_mylar_series: bool = False
        """导入 Mylar 生成的元数据"""
        self.name: str = ""
        """名称"""
        self.oneshots_directory: str = ""
        """单行本目录"""
        self.repair_extensions: bool = True
        """自动修复不正确的文件扩展名"""
        self.root: str = ""
        """根文件夹"""
        self.scan_cbx: bool = True
        """扫描漫画书存档"""
        self.scan_directory_exclusions: Optional[List[str]] = None
        """扫描时排除的目录列表"""
        self.scan_epub: bool = True
        """扫描 EPUB"""
        self.scan_force_modified_time: bool = False
        """强制目录修改时间"""
        self.scan_interval: str = "DAILY"
        """扫描间隔"""
        self.scan_on_startup: bool = False
        """启动时扫描"""
        self.scan_pdf: bool = True
        """扫描 PDF"""
        self.series_cover: str = "FIRST"
        """系列封面设置"""
        self.unavailable: bool = True
        """可用"""

    @classmethod
    def new(cls, name: str, root: str) -> "KomgaLibrary":
        instance = cls()
        instance.name = name
        instance.root = root
        return instance

    @classmethod
    def from_json(cls, resp: json) -> "KomgaLibrary":
        instance = cls()
        instance.analyze_dimensions = resp["analyzeDimensions"]
        instance.convert_to_cbz = resp["convertToCbz"]
        instance.empty_trash_after_scan = resp["emptyTrashAfterScan"]
        instance.hash_files = resp["hashFiles"]
        instance.hash_koreader = resp["hashKoreader"]
        instance.hash_pages = resp["hashPages"]
        instance.id = resp["id"]
        instance.import_barcode_isbn = resp["importBarcodeIsbn"]
        instance.import_comic_info_book = resp["importComicInfoBook"]
        instance.import_comic_info_collection = resp["importComicInfoCollection"]
        instance.import_comic_info_read_list = resp["importComicInfoReadList"]
        instance.import_comic_info_series = resp["importComicInfoSeries"]
        instance.import_comic_info_series_append_volume = resp["importComicInfoSeriesAppendVolume"]
        instance.import_epub_book = resp["importEpubBook"]
        instance.import_epub_series = resp["importEpubSeries"]
        instance.import_local_artwork = resp["importLocalArtwork"]
        instance.import_mylar_series = resp["importMylarSeries"]
        instance.name = resp["name"]
        instance.oneshots_directory = resp["oneshotsDirectory"]
        instance.repair_extensions = resp["repairExtensions"]
        instance.root = resp["root"]
        instance.scan_cbx = resp["scanCbx"]
        instance.scan_directory_exclusions = resp["scanDirectoryExclusions"]
        instance.scan_epub = resp["scanEpub"]
        instance.scan_force_modified_time = resp["scanForceModifiedTime"]
        instance.scan_interval = resp["scanInterval"]
        instance.scan_on_startup = resp["scanOnStartup"]
        instance.scan_pdf = resp["scanPdf"]
        instance.series_cover = resp["seriesCover"]
        instance.unavailable = resp["unavailable"]
        return instance

    def get_payload(self) -> json:
        return {
            "analyzeDimensions": self.analyze_dimensions,
            "convertToCbz": self.convert_to_cbz,
            "emptyTrashAfterScan": self.empty_trash_after_scan,
            "hashFiles": self.hash_files,
            "hashKoreader": self.hash_koreader,
            "hashPages": self.hash_pages,
            "importBarcodeIsbn": self.import_barcode_isbn,
            "importComicInfoBook": self.import_comic_info_book,
            "importComicInfoCollection": self.import_comic_info_collection,
            "importComicInfoReadList": self.import_comic_info_read_list,
            "importComicInfoSeries": self.import_comic_info_series,
            "importComicInfoSeriesAppendVolume": self.import_comic_info_series_append_volume,
            "importEpubBook": self.import_epub_book,
            "importEpubSeries": self.import_epub_series,
            "importLocalArtwork": self.import_local_artwork,
            "importMylarSeries": self.import_mylar_series,
            "name": self.name,
            "oneshotsDirectory": self.oneshots_directory,
            "repairExtensions": self.repair_extensions,
            "root": self.root,
            "scanCbx": self.scan_cbx,
            "scanDirectoryExclusions": self.scan_directory_exclusions,
            "scanEpub": self.scan_epub,
            "scanForceModifiedTime": self.scan_force_modified_time,
            "scanInterval": self.scan_interval,
            "scanOnStartup": self.scan_on_startup,
            "scanPdf": self.scan_pdf,
            "seriesCover": self.series_cover
        }
