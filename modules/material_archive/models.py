"""教学成果资料归档数据模型（纯标准库实现）。"""

from dataclasses import asdict, dataclass
from typing import Any, Dict

# 预设成果类型
ACHIEVEMENT_TYPES = (
    "课程考核材料",
    "实践教学材料",
    "毕业设计（论文）材料",
    "学科竞赛成果",
    "教研教改成果",
)

# 归档状态
STATUS_ARCHIVED = "已归档"
STATUS_PENDING = "待归档"
ARCHIVE_STATUSES = (STATUS_ARCHIVED, STATUS_PENDING)


@dataclass
class ArchiveRecord:
    """教学成果资料归档记录。

    :param archive_id: 归档编号，如 "AR2026001"
    :param material_name: 材料名称
    :param achievement_type: 成果类型，取值见 ACHIEVEMENT_TYPES
    :param course_name: 关联课程名称
    :param semester: 开课学期，如 "2025-2026-1"
    :param file_path: 资料文件路径
    :param uploader: 上传人
    :param upload_time: 上传时间，如 "2026-01-12 10:30"
    :param status: 归档状态，取值见 ARCHIVE_STATUSES
    """

    archive_id: str
    material_name: str
    achievement_type: str
    course_name: str
    semester: str
    file_path: str
    uploader: str
    upload_time: str
    status: str

    def __post_init__(self) -> None:
        self.archive_id = str(self.archive_id).strip()
        self.material_name = str(self.material_name).strip()
        self.achievement_type = str(self.achievement_type).strip()
        self.course_name = str(self.course_name).strip()
        self.semester = str(self.semester).strip()
        self.file_path = str(self.file_path).strip()
        self.uploader = str(self.uploader).strip()
        self.upload_time = str(self.upload_time).strip()
        self.status = str(self.status).strip()

        if not self.archive_id:
            raise ValueError("归档编号不能为空")
        if not self.material_name:
            raise ValueError(f"归档记录 {self.archive_id} 的材料名称不能为空")
        if self.achievement_type not in ACHIEVEMENT_TYPES:
            allowed = "、".join(ACHIEVEMENT_TYPES)
            raise ValueError(
                f"归档记录 {self.archive_id} 的成果类型必须是以下之一：{allowed}"
            )
        if not self.course_name:
            raise ValueError(f"归档记录 {self.archive_id} 的关联课程不能为空")
        if not self.semester:
            raise ValueError(f"归档记录 {self.archive_id} 的学期不能为空")
        if not self.file_path:
            raise ValueError(f"归档记录 {self.archive_id} 的文件路径不能为空")
        if not self.uploader:
            raise ValueError(f"归档记录 {self.archive_id} 的上传人不能为空")
        if not self.upload_time:
            raise ValueError(f"归档记录 {self.archive_id} 的上传时间不能为空")
        if self.status not in ARCHIVE_STATUSES:
            allowed = "、".join(ARCHIVE_STATUSES)
            raise ValueError(
                f"归档记录 {self.archive_id} 的归档状态必须是以下之一：{allowed}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchiveRecord":
        """从字典还原归档记录。"""
        required = (
            "archive_id",
            "material_name",
            "achievement_type",
            "course_name",
            "semester",
            "file_path",
            "uploader",
            "upload_time",
            "status",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"归档记录数据缺少字段：{', '.join(missing)}")
        return cls(**{key: data[key] for key in required})
