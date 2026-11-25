"""控制台演示：预置示例归档记录并展示查询、筛选与统计结果。"""

from typing import Any, Dict, List

from .models import ArchiveRecord
from .service import MaterialArchiveService

SEPARATOR = "=" * 64

DEMO_RECORDS = (
    ArchiveRecord(
        archive_id="AR2026001",
        material_name="《数据结构》期末考试试卷及成绩单",
        achievement_type="课程考核材料",
        course_name="数据结构",
        semester="2025-2026-1",
        file_path="files/archives/数据结构_期末试卷_2025-2026-1.pdf",
        uploader="王老师",
        upload_time="2026-01-12 10:30",
        status="已归档",
    ),
    ArchiveRecord(
        archive_id="AR2026002",
        material_name="《软件工程》课程设计报告（优秀样例）",
        achievement_type="课程考核材料",
        course_name="软件工程",
        semester="2025-2026-1",
        file_path="files/archives/软件工程_课程设计报告_样例.pdf",
        uploader="李老师",
        upload_time="2026-01-18 14:05",
        status="已归档",
    ),
    ArchiveRecord(
        archive_id="AR2026003",
        material_name="《大学物理实验》实验报告汇编",
        achievement_type="实践教学材料",
        course_name="大学物理实验",
        semester="2025-2026-1",
        file_path="files/archives/大学物理实验_实验报告汇编.pdf",
        uploader="赵老师",
        upload_time="2026-01-09 09:15",
        status="已归档",
    ),
    ArchiveRecord(
        archive_id="AR2026004",
        material_name="2026 年蓝桥杯程序设计大赛获奖证书及作品",
        achievement_type="学科竞赛成果",
        course_name="程序设计实践",
        semester="2025-2026-2",
        file_path="files/archives/蓝桥杯_获奖证书及作品.pdf",
        uploader="陈老师",
        upload_time="2026-05-21 16:40",
        status="已归档",
    ),
    ArchiveRecord(
        archive_id="AR2026005",
        material_name="《数据结构》实验指导书修订稿",
        achievement_type="教研教改成果",
        course_name="数据结构",
        semester="2025-2026-2",
        file_path="files/archives/数据结构_实验指导书_修订稿.docx",
        uploader="王老师",
        upload_time="2026-06-03 11:20",
        status="待归档",
    ),
)


def seed_demo_records(service: MaterialArchiveService) -> bool:
    """数据为空时写入示例归档记录，返回是否执行了写入。"""
    if len(service) > 0:
        return False
    for record in DEMO_RECORDS:
        service.add_record(record)
    return True


def print_records(records: List[Dict[str, Any]]) -> None:
    """逐条输出归档记录信息。"""
    if not records:
        print("（无匹配记录）")
        print()
        return

    for index, record in enumerate(records, start=1):
        print(f"[{index}] 编号 {record['archive_id']}  {record['material_name']}")
        print(
            f"    成果类型：{record['achievement_type']}    "
            f"归档状态：{record['status']}"
        )
        print(f"    关联课程：{record['course_name']}    学期：{record['semester']}")
        print(f"    文件路径：{record['file_path']}")
        print(f"    上传人：{record['uploader']}    上传时间：{record['upload_time']}")
        print("-" * 64)


def print_type_statistics(counts: Dict[str, int]) -> None:
    """按成果类型输出数量统计。"""
    total = sum(counts.values())
    if not total:
        print("（暂无归档记录，无法统计）")
        print()
        return

    print(f"共 {total} 条归档记录：")
    for achievement_type, count in counts.items():
        percentage = count / total * 100
        print(f"  {achievement_type}：{count} 条（{percentage:.1f}%）")
    print()


def run() -> None:
    """模块入口：加载数据、必要时初始化示例数据，并演示查询、筛选与统计。"""
    service = MaterialArchiveService()
    if seed_demo_records(service):
        print(f"已初始化 {len(DEMO_RECORDS)} 条示例归档记录：{service.data_file}\n")

    print(SEPARATOR)
    print("工程教育专业认证支撑平台 —— 教学成果资料上传归档")
    print(SEPARATOR)

    print("\n【1】全部归档记录")
    print_records(service.list_records())

    demo_type = "课程考核材料"
    print(f"\n【2】按成果类型筛选：{demo_type}")
    matched = service.filter_by_type(demo_type)
    print(f"筛选结果：{len(matched)} 条")
    print_records(matched)

    demo_course = "数据结构"
    print(f"\n【3】按关联课程筛选：{demo_course}")
    matched = service.filter_by_course(demo_course)
    print(f"筛选结果：{len(matched)} 条")
    print_records(matched)

    print("\n【4】按成果类型统计数量")
    print_type_statistics(service.count_by_type())
