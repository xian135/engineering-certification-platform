"""材料检索与导出模块。

对外暴露数据模型、检索服务与收藏历史服务，供主入口统一调度。
"""

from .favorite_service import FavoriteHistoryService
from .models import (
    DEFAULT_PAGE_SIZE,
    MAJORS,
    MATERIAL_TYPES,
    YEARS,
    MaterialItem,
    SearchCondition,
    SearchPage,
)
from .search_service import MaterialSearchService

__all__ = [
    "DEFAULT_PAGE_SIZE",
    "MAJORS",
    "MATERIAL_TYPES",
    "YEARS",
    "FavoriteHistoryService",
    "MaterialItem",
    "MaterialSearchService",
    "SearchCondition",
    "SearchPage",
]
