"""控制台演示：预置示例指标点并逐条输出达成度。"""

from .models import IndicatorPoint
from .service import IndicatorService

SEPARATOR = "=" * 64

DEMO_INDICATORS = (
    IndicatorPoint(
        indicator_id="1.1",
        name="能够运用数学、自然科学和工程科学知识表述复杂工程问题",
        graduation_requirement="毕业要求 1：工程知识",
        course_name="高等数学",
        course_score=86.5,
        support_weight=0.35,
    ),
    IndicatorPoint(
        indicator_id="2.2",
        name="能够基于工程科学原理设计实验方案并分析与解释数据",
        graduation_requirement="毕业要求 2：问题分析",
        course_name="大学物理实验",
        course_score=91.0,
        support_weight=0.40,
    ),
    IndicatorPoint(
        indicator_id="3.1",
        name="能够设计满足特定需求的软件系统并在设计中体现创新意识",
        graduation_requirement="毕业要求 3：设计/开发解决方案",
        course_name="软件工程",
        course_score=78.0,
        support_weight=0.30,
    ),
)


def seed_demo_indicators(service: IndicatorService) -> bool:
    """数据为空时写入示例指标点，返回是否执行了写入。"""
    if len(service) > 0:
        return False
    for indicator in DEMO_INDICATORS:
        service.add_indicator(indicator)
    return True


def print_indicators(service: IndicatorService) -> None:
    """逐条输出指标点信息与对应达成度。"""
    records = service.list_indicators()

    print(SEPARATOR)
    print("工程教育专业认证支撑平台 —— 认证指标管理与达成度计算")
    print(SEPARATOR)
    print(f"达成度 = 课程成绩 × 支撑权重（保留两位小数），共 {len(records)} 个指标点")
    print()

    for index, record in enumerate(records, start=1):
        print(f"[{index}] 指标点 {record['indicator_id']}  {record['name']}")
        print(f"    所属毕业要求：{record['graduation_requirement']}")
        print(f"    支撑课程：{record['course_name']}")
        print(
            f"    课程成绩：{record['course_score']:.2f}    "
            f"支撑权重：{record['support_weight']:.2f}"
        )
        print(
            f"    达成度：{record['course_score']:.2f} × "
            f"{record['support_weight']:.2f} = {record['attainment']:.2f}"
        )
        print("-" * 64)


def run() -> None:
    """模块入口：加载数据、必要时初始化示例数据，并输出达成度。"""
    service = IndicatorService()
    if seed_demo_indicators(service):
        print(f"已初始化 {len(DEMO_INDICATORS)} 条示例指标点：{service.data_file}\n")
    print_indicators(service)
