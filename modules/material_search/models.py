"""材料检索与导出模块数据模型（纯标准库实现）。"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

# 预设材料类型
MATERIAL_TYPES = (
    "课程材料",
    "试卷",
    "实验报告",
    "实践报告",
    "毕业论文",
    "教案课件",
)

# 预设专业
MAJORS = (
    "软件工程",
    "计算机科学与技术",
    "网络工程",
    "数据科学与大数据技术",
)

# 预设年度
YEARS = (2023, 2024, 2025, 2026)

# 默认每页条数
DEFAULT_PAGE_SIZE = 5


@dataclass
class MaterialItem:
    """教学材料条目（对应设计文档 2.2 节的 T_Material 表）。

    :param materialID: 材料编号
    :param materialName: 材料名称
    :param materialType: 材料类型，取值见 MATERIAL_TYPES
    :param major: 所属专业，取值见 MAJORS
    :param year: 所属年度，取值见 YEARS
    :param uploadUserID: 上传用户编号
    :param uploadTime: 上传时间，格式 "YYYY-MM-DD HH:MM"
    :param filePath: 文件存储路径
    :param content: 材料正文摘要，用于关键词检索
    """

    materialID: int
    materialName: str
    materialType: str
    major: str
    year: int
    uploadUserID: int
    uploadTime: str
    filePath: str
    content: str

    def __post_init__(self) -> None:
        self.materialID = int(self.materialID)
        self.year = int(self.year)
        self.uploadUserID = int(self.uploadUserID)
        self.materialName = str(self.materialName).strip()
        self.materialType = str(self.materialType).strip()
        self.major = str(self.major).strip()
        self.uploadTime = str(self.uploadTime).strip()
        self.filePath = str(self.filePath).strip()
        self.content = str(self.content).strip()

        if self.materialID <= 0:
            raise ValueError("材料编号必须为正整数")
        if not self.materialName:
            raise ValueError(f"材料 {self.materialID} 的名称不能为空")
        if self.materialType not in MATERIAL_TYPES:
            allowed = "、".join(MATERIAL_TYPES)
            raise ValueError(
                f"材料 {self.materialID} 的类型必须是以下之一：{allowed}"
            )
        if self.major not in MAJORS:
            allowed = "、".join(MAJORS)
            raise ValueError(f"材料 {self.materialID} 的专业必须是以下之一：{allowed}")
        if self.year not in YEARS:
            raise ValueError(f"材料 {self.materialID} 的年度必须在 {YEARS[0]}~{YEARS[-1]} 之间")
        if not self.uploadTime:
            raise ValueError(f"材料 {self.materialID} 的上传时间不能为空")
        if not self.filePath:
            raise ValueError(f"材料 {self.materialID} 的文件路径不能为空")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaterialItem":
        """从字典还原材料条目。"""
        required = (
            "materialID",
            "materialName",
            "materialType",
            "major",
            "year",
            "uploadUserID",
            "uploadTime",
            "filePath",
            "content",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"材料数据缺少字段：{', '.join(missing)}")
        return cls(**{key: data[key] for key in required})


@dataclass
class SearchCondition:
    """多条件组合检索条件，四个条件均为可选，全部为空表示不限制。

    :param materialType: 材料类型（精确匹配）
    :param major: 所属专业（精确匹配）
    :param year: 所属年度（精确匹配）
    :param keyword: 关键词，在材料名称与正文中做包含匹配（不区分大小写）
    """

    materialType: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    keyword: Optional[str] = None

    def is_empty(self) -> bool:
        """四个条件是否全部为空。"""
        return not any(
            (
                (self.materialType or "").strip(),
                (self.major or "").strip(),
                self.year,
                (self.keyword or "").strip(),
            )
        )

    def describe(self) -> str:
        """把条件拼成便于展示的一行文字。"""
        parts: List[str] = []
        if self.materialType:
            parts.append(f"材料类型={self.materialType}")
        if self.major:
            parts.append(f"专业={self.major}")
        if self.year:
            parts.append(f"年度={self.year}")
        if self.keyword:
            parts.append(f"关键词={self.keyword}")
        return "、".join(parts) if parts else "（无筛选条件）"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，便于收藏与历史记录复用。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchCondition":
        """从字典还原检索条件。"""
        return cls(
            materialType=data.get("materialType"),
            major=data.get("major"),
            year=data.get("year"),
            keyword=data.get("keyword"),
        )


@dataclass
class SearchPage:
    """分页检索结果。

    :param items: 当前页的材料条目
    :param total: 命中总条数
    :param page: 当前页码，从 1 开始
    :param page_size: 每页条数
    """

    items: List[MaterialItem]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """总页数（无命中时返回 0）。"""
        if self.total <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return {
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
        }
