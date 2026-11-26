"""材料检索服务：多条件组合检索、按上传时间倒序与分页。

说明：本文件的检索过滤与分页核心逻辑由 IDE 中的 AI 编程助手（文心快码）
根据需求描述生成，本人核对命名规范、参数校验与模块对接后接入本项目。
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from .models import DEFAULT_PAGE_SIZE, MaterialItem, SearchCondition, SearchPage

# 默认数据文件：<项目根目录>/data/materials.json
DEFAULT_DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "materials.json"


class MaterialSearchService:
    """材料多条件组合检索服务。

    负责加载材料数据、按材料类型/专业/年度/关键词四项条件组合过滤，
    并把命中结果按上传时间倒序分页返回。
    """

    def __init__(self, data_file: Optional[Union[str, Path]] = None) -> None:
        self.data_file = Path(data_file) if data_file else DEFAULT_DATA_FILE
        self._materials: List[MaterialItem] = []
        self.load()

    # ---------- 数据加载 ----------

    def load(self) -> None:
        """从 JSON 文件加载材料数据；文件不存在或为空时视为空列表。"""
        if not self.data_file.exists():
            self._materials = []
            return

        text = self.data_file.read_text(encoding="utf-8").strip()
        if not text:
            self._materials = []
            return

        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"材料数据文件格式错误：{self.data_file}") from exc
        if not isinstance(raw, list):
            raise ValueError(f"材料数据文件应为 JSON 数组：{self.data_file}")

        self._materials = [MaterialItem.from_dict(item) for item in raw]

    # ---------- 条件匹配 ----------

    def match(self, item: MaterialItem, condition: SearchCondition) -> bool:
        """判断单条材料是否满足全部非空条件（条件之间为“与”关系）。"""
        material_type = (condition.materialType or "").strip()
        if material_type and item.materialType != material_type:
            return False

        major = (condition.major or "").strip()
        if major and item.major != major:
            return False

        if condition.year and item.year != int(condition.year):
            return False

        keyword = (condition.keyword or "").strip().lower()
        if keyword:
            haystack = f"{item.materialName} {item.content}".lower()
            if keyword not in haystack:
                return False

        return True

    # ---------- 检索 ----------

    def search(
        self,
        condition: Optional[SearchCondition] = None,
        *,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> SearchPage:
        """按条件检索材料，结果按上传时间倒序分页返回。

        :param condition: 检索条件，为空表示不限制
        :param page: 页码，从 1 开始
        :param page_size: 每页条数
        :raises ValueError: 页码或每页条数不合法
        """
        if page < 1:
            raise ValueError("页码必须从 1 开始")
        if page_size < 1:
            raise ValueError("每页条数必须为正整数")

        cond = condition or SearchCondition()
        matched = [item for item in self._materials if self.match(item, cond)]

        # 按上传时间倒序；时间格式统一为 "YYYY-MM-DD HH:MM"，字符串比较即可
        matched.sort(key=lambda item: item.uploadTime, reverse=True)

        total = len(matched)
        start = (page - 1) * page_size
        end = start + page_size
        return SearchPage(
            items=matched[start:end],
            total=total,
            page=page,
            page_size=page_size,
        )

    # ---------- 辅助 ----------

    def count_by_type(self) -> dict:
        """按材料类型统计数量，按数量降序返回，用于检索页侧边统计。"""
        counts: dict = {}
        for item in self._materials:
            counts[item.materialType] = counts.get(item.materialType, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def __len__(self) -> int:
        return len(self._materials)
