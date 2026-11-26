"""控制台演示：材料多条件组合检索、分页浏览、收藏与检索历史。"""

from typing import Any, Dict, List

from .favorite_service import FavoriteHistoryService
from .models import MaterialItem, SearchCondition, SearchPage
from .search_service import MaterialSearchService

SEPARATOR = "=" * 64
INNER = "-" * 64


def print_page(page: SearchPage) -> None:
    """输出一页检索结果。"""
    if not page.items:
        print("（无匹配材料）")
        print()
        return

    print(
        f"命中 {page.total} 条，共 {page.total_pages} 页，"
        f"当前第 {page.page} 页（每页 {page.page_size} 条）"
    )
    for index, item in enumerate(page.items, start=1):
        print(f"[{index}] 编号 {item.materialID}  {item.materialName}")
        print(
            f"    类型：{item.materialType}    "
            f"专业：{item.major}    年度：{item.year}"
        )
        print(f"    上传时间：{item.uploadTime}    上传用户：{item.uploadUserID}")
        print(f"    文件路径：{item.filePath}")
        print(INNER)
    print()


def run_search(
    service: MaterialSearchService,
    favorite: FavoriteHistoryService,
    title: str,
    condition: SearchCondition,
    *,
    page: int = 1,
    page_size: int = 5,
) -> SearchPage:
    """执行一次检索、记录历史并打印结果。"""
    print(f"\n【{title}】条件：{condition.describe()}")
    result = service.search(condition, page=page, page_size=page_size)
    favorite.record_history(condition, result.total)
    print_page(result)
    return result


def run() -> None:
    """模块入口：演示多条件组合检索、分页、收藏与检索历史。"""
    service = MaterialSearchService()
    favorite = FavoriteHistoryService()

    print(SEPARATOR)
    print("工程教育专业认证支撑平台 —— 材料检索与导出")
    print(SEPARATOR)
    print(f"材料库：{service.data_file}")
    print(f"当前共有 {len(service)} 条材料，按类型统计：")
    for material_type, count in service.count_by_type().items():
        print(f"  {material_type}：{count} 条")

    # 1. 不限条件，浏览第一页
    first = run_search(service, favorite, "1", SearchCondition())

    # 2. 材料类型 + 专业 组合检索
    run_search(
        service,
        favorite,
        "2",
        SearchCondition(materialType="试卷", major="软件工程"),
    )

    # 3. 年度 + 关键词 组合检索
    run_search(
        service,
        favorite,
        "3",
        SearchCondition(year=2025, keyword="实践"),
    )

    # 4. 四个条件组合检索
    run_search(
        service,
        favorite,
        "4",
        SearchCondition(
            materialType="实践报告",
            major="软件工程",
            year=2026,
            keyword="前端",
        ),
    )

    # 5. 分页浏览第二页
    run_search(service, favorite, "5", SearchCondition(), page=2)

    # 6. 收藏与检索历史（本人手写功能）
    print("\n【6】收藏与检索历史")
    for item in first.items[:2]:
        added = favorite.add_favorite(item.materialID)
        print(
            f"收藏材料 {item.materialID} {item.materialName}："
            f"{'成功' if added else '已收藏'}"
        )
    favorite.add_favorite(1012)
    print(f"\n当前收藏 {len(favorite.favorite_ids())} 条：")
    for item in favorite.list_favorites(service._materials):
        print(f"  [{item.materialID}] {item.materialName}（{item.materialType}）")

    print(f"\n检索历史共 {len(favorite.list_history())} 条：")
    for index, entry in enumerate(favorite.list_history(), start=1):
        cond = SearchCondition.from_dict(entry["condition"])
        print(
            f"  {index}. {entry['time']}  {cond.describe()}  "
            f"命中 {entry['matched']} 条"
        )

    replay = favorite.replay_history(2)
    if replay is not None:
        print(f"\n复用第 2 条历史条件重新检索：{replay.describe()}")
        again = service.search(replay)
        print_page(again)
