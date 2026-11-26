"""收藏与检索历史服务（本人独立编写，未使用 AI 编程工具生成）。

对应设计文档 2.5 节“收藏与检索历史”功能：
- 收藏常用材料、取消收藏，并列出当前全部收藏；
- 每次检索自动记录检索时间、条件与命中数量；
- 支持按序号复用历史检索条件，免去重复输入。
数据暂存于内存列表，后续接入数据库时替换为持久化仓储。
"""

from datetime import datetime
from typing import Dict, List, Optional

from .models import MaterialItem, SearchCondition


class FavoriteHistoryService:
    """收藏与检索历史服务。"""

    def __init__(self) -> None:
        # 收藏的材料编号，按收藏先后顺序保存
        self._favorites: List[int] = []
        # 检索历史：每条包含时间、条件、命中数量
        self._history: List[Dict] = []

    # ---------- 收藏 ----------

    def add_favorite(self, material_id: int) -> bool:
        """收藏材料；已收藏时返回 False，不重复添加。"""
        material_id = int(material_id)
        if material_id in self._favorites:
            return False
        self._favorites.append(material_id)
        return True

    def cancel_favorite(self, material_id: int) -> bool:
        """取消收藏；未收藏时返回 False。"""
        material_id = int(material_id)
        if material_id not in self._favorites:
            return False
        self._favorites.remove(material_id)
        return True

    def favorite_ids(self) -> List[int]:
        """返回收藏材料编号列表（按收藏顺序）。"""
        return list(self._favorites)

    def list_favorites(self, materials: List[MaterialItem]) -> List[MaterialItem]:
        """按收藏顺序返回收藏材料对象，已被删除的材料自动跳过。"""
        index = {item.materialID: item for item in materials}
        return [index[mid] for mid in self._favorites if mid in index]

    # ---------- 检索历史 ----------

    def record_history(
        self, condition: SearchCondition, matched_total: int
    ) -> Dict:
        """记录一次检索，返回该条历史记录。"""
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "condition": condition.to_dict(),
            "matched": int(matched_total),
        }
        self._history.append(entry)
        return entry

    def list_history(self) -> List[Dict]:
        """返回全部检索历史（按发生顺序）。"""
        return [dict(item) for item in self._history]

    def replay_history(self, index: int) -> Optional[SearchCondition]:
        """按序号（从 1 开始）取出历史条件用于复用检索。"""
        if index < 1 or index > len(self._history):
            return None
        return SearchCondition.from_dict(self._history[index - 1]["condition"])

    def clear_history(self) -> None:
        """清空检索历史。"""
        self._history.clear()
