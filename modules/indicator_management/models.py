"""认证指标点数据模型（纯标准库实现）。"""

from dataclasses import asdict, dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict


def round_half_up(value: float, digits: int = 2) -> float:
    """四舍五入，避免内置 round 的银行家舍入与浮点误差。"""
    quantizer = Decimal(1).scaleb(-digits)
    return float(Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP))


@dataclass
class IndicatorPoint:
    """毕业要求指标点。

    :param indicator_id: 指标点编号，如 "1.1"
    :param name: 指标点名称
    :param graduation_requirement: 所属毕业要求，如 "毕业要求 1：工程知识"
    :param course_name: 支撑课程名称
    :param course_score: 课程成绩（百分制，0~100）
    :param support_weight: 支撑权重（0~1）
    """

    indicator_id: str
    name: str
    graduation_requirement: str
    course_name: str
    course_score: float
    support_weight: float

    def __post_init__(self) -> None:
        self.indicator_id = str(self.indicator_id).strip()
        self.name = str(self.name).strip()
        self.graduation_requirement = str(self.graduation_requirement).strip()
        self.course_name = str(self.course_name).strip()
        self.course_score = float(self.course_score)
        self.support_weight = float(self.support_weight)

        if not self.indicator_id:
            raise ValueError("指标点编号不能为空")
        if not self.name:
            raise ValueError(f"指标点 {self.indicator_id} 的名称不能为空")
        if not self.graduation_requirement:
            raise ValueError(f"指标点 {self.indicator_id} 的所属毕业要求不能为空")
        if not self.course_name:
            raise ValueError(f"指标点 {self.indicator_id} 的支撑课程不能为空")
        if not 0 <= self.course_score <= 100:
            raise ValueError(f"指标点 {self.indicator_id} 的课程成绩应在 0~100 之间")
        if not 0 <= self.support_weight <= 1:
            raise ValueError(f"指标点 {self.indicator_id} 的支撑权重应在 0~1 之间")

    @property
    def attainment(self) -> float:
        """达成度 = 课程成绩 × 支撑权重，保留两位小数。"""
        return round_half_up(self.course_score * self.support_weight)

    def to_dict(self, include_attainment: bool = False) -> Dict[str, Any]:
        """转换为字典，可选附带计算出的达成度。"""
        data = asdict(self)
        if include_attainment:
            data["attainment"] = self.attainment
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndicatorPoint":
        """从字典还原指标点（忽略 attainment 等派生字段）。"""
        required = (
            "indicator_id",
            "name",
            "graduation_requirement",
            "course_name",
            "course_score",
            "support_weight",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"指标点数据缺少字段：{', '.join(missing)}")
        return cls(**{key: data[key] for key in required})
