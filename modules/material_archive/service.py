"""归档业务逻辑：JSON 持久化、查询筛选与类型统计。"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import ArchiveRecord

# 默认数据文件：<项目根目录>/data/archives.json
DEFAULT_DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "archives.json"


class MaterialArchiveService:
    """教学成果资料归档服务。

    负责归档记录的添加与查询、JSON 文件读写、
    按成果类型/关联课程筛选，以及按成果类型统计数量。
    """

    def __init__(self, data_file: Optional[Union[str, Path]] = None) -> None:
        self.data_file = Path(data_file) if data_file else DEFAULT_DATA_FILE
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[ArchiveRecord] = []
        self.load()

    # ---------- 持久化 ----------

    def load(self) -> None:
        """从 JSON 文件加载归档记录；文件不存在或为空时视为空列表。"""
        if not self.data_file.exists():
            self._records = []
            return

        text = self.data_file.read_text(encoding="utf-8").strip()
        if not text:
            self._records = []
            return

        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"归档记录数据文件格式错误：{self.data_file}") from exc
        if not isinstance(raw, list):
            raise ValueError(f"归档记录数据文件应为 JSON 数组：{self.data_file}")

        self._records = [ArchiveRecord.from_dict(item) for item in raw]

    def save(self) -> None:
        """将内存中的归档记录写回 JSON 文件。"""
        payload = [item.to_dict() for item in self._records]
        self.data_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    # ---------- 归档记录管理 ----------

    def add_record(
        self, record: ArchiveRecord, *, overwrite: bool = False
    ) -> ArchiveRecord:
        """添加归档记录并立即持久化。

        :param overwrite: 编号重复时是否覆盖已有记录
        :raises ValueError: 编号重复且未允许覆盖
        """
        for index, existing in enumerate(self._records):
            if existing.archive_id == record.archive_id:
                if not overwrite:
                    raise ValueError(f"归档编号已存在：{record.archive_id}")
                self._records[index] = record
                self.save()
                return record

        self._records.append(record)
        self.save()
        return record

    # ---------- 查询与筛选 ----------

    def list_records(self) -> List[Dict[str, Any]]:
        """查询全部归档记录，按添加顺序返回。"""
        return [item.to_dict() for item in self._records]

    def filter_by_type(self, achievement_type: str) -> List[Dict[str, Any]]:
        """按成果类型筛选（精确匹配），返回匹配的归档记录。"""
        return [
            item.to_dict()
            for item in self._records
            if item.achievement_type == achievement_type.strip()
        ]

    def filter_by_course(self, course_name: str) -> List[Dict[str, Any]]:
        """按关联课程筛选（课程名称包含匹配，不区分大小写），返回匹配的归档记录。"""
        keyword = course_name.strip().lower()
        return [
            item.to_dict()
            for item in self._records
            if keyword in item.course_name.lower()
        ]

    # ---------- 统计 ----------

    def count_by_type(self) -> Dict[str, int]:
        """按成果类型统计数量，按数量降序（同数量按类型名升序）返回。"""
        counts: Dict[str, int] = {}
        for item in self._records:
            counts[item.achievement_type] = counts.get(item.achievement_type, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def __len__(self) -> int:
        return len(self._records)
