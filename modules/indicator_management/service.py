"""指标点业务逻辑：JSON 持久化、查询与达成度计算。"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import IndicatorPoint

# 默认数据文件：<项目根目录>/data/indicators.json
DEFAULT_DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "indicators.json"


class IndicatorService:
    """指标点管理服务。

    负责指标点的添加与查询、JSON 文件读写，以及达成度计算。
    """

    def __init__(self, data_file: Optional[Union[str, Path]] = None) -> None:
        self.data_file = Path(data_file) if data_file else DEFAULT_DATA_FILE
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._indicators: List[IndicatorPoint] = []
        self.load()

    # ---------- 持久化 ----------

    def load(self) -> None:
        """从 JSON 文件加载指标点；文件不存在或为空时视为空列表。"""
        if not self.data_file.exists():
            self._indicators = []
            return

        text = self.data_file.read_text(encoding="utf-8").strip()
        if not text:
            self._indicators = []
            return

        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"指标点数据文件格式错误：{self.data_file}") from exc
        if not isinstance(raw, list):
            raise ValueError(f"指标点数据文件应为 JSON 数组：{self.data_file}")

        self._indicators = [IndicatorPoint.from_dict(item) for item in raw]

    def save(self) -> None:
        """将内存中的指标点写回 JSON 文件。"""
        payload = [item.to_dict() for item in self._indicators]
        self.data_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    # ---------- 指标点管理 ----------

    def add_indicator(
        self, indicator: IndicatorPoint, *, overwrite: bool = False
    ) -> IndicatorPoint:
        """添加指标点并立即持久化。

        :param overwrite: 编号重复时是否覆盖已有指标点
        :raises ValueError: 编号重复且未允许覆盖
        """
        for index, existing in enumerate(self._indicators):
            if existing.indicator_id == indicator.indicator_id:
                if not overwrite:
                    raise ValueError(f"指标点编号已存在：{indicator.indicator_id}")
                self._indicators[index] = indicator
                self.save()
                return indicator

        self._indicators.append(indicator)
        self.save()
        return indicator

    def get_indicator(self, indicator_id: str) -> Optional[IndicatorPoint]:
        """按编号查询单个指标点，未找到返回 None。"""
        for item in self._indicators:
            if item.indicator_id == indicator_id:
                return item
        return None

    # ---------- 达成度 ----------

    @staticmethod
    def calculate_attainment(indicator: IndicatorPoint) -> float:
        """计算单个指标点的达成度：课程成绩 × 支撑权重（保留两位小数）。"""
        return indicator.attainment

    def list_indicators(self) -> List[Dict[str, Any]]:
        """查询全部指标点及其达成度，按添加顺序返回。"""
        return [item.to_dict(include_attainment=True) for item in self._indicators]

    def __len__(self) -> int:
        return len(self._indicators)
