"""用户与权限业务逻辑：账号增删改查、登录校验、权限控制、操作日志。"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import ROLE_NAMES, OperationLog, User, hash_password

# 默认数据文件：<项目根目录>/data/users.json、data/operation_logs.json
DEFAULT_USER_FILE = Path(__file__).resolve().parents[2] / "data" / "users.json"
DEFAULT_LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "operation_logs.json"

# 连续登录失败达到该次数后锁定账号
MAX_LOGIN_FAILURES = 5


class UserService:
    """用户与权限管理服务。

    负责账号的增删改查、登录校验、基于角色的权限判断，
    以及登录与操作日志的持久化。
    """

    def __init__(
        self,
        user_file: Optional[Union[str, Path]] = None,
        log_file: Optional[Union[str, Path]] = None,
    ) -> None:
        self.user_file = Path(user_file) if user_file else DEFAULT_USER_FILE
        self.log_file = Path(log_file) if log_file else DEFAULT_LOG_FILE
        self.user_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self._users: List[User] = []
        self._logs: List[OperationLog] = []
        self._login_failures: Dict[str, int] = {}
        self.load()

    # ---------- 持久化 ----------

    def load(self) -> None:
        """从 JSON 文件加载账号与日志。"""
        self._users = [User.from_dict(item) for item in self._read_list(self.user_file)]
        self._logs = [
            OperationLog.from_dict(item) for item in self._read_list(self.log_file)
        ]

    def save(self) -> None:
        """将内存中的账号写回 JSON 文件。"""
        payload = [item.to_dict(include_password=True) for item in self._users]
        self.user_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def save_logs(self) -> None:
        """将内存中的操作日志写回 JSON 文件。"""
        payload = [item.to_dict() for item in self._logs]
        self.log_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _read_list(path: Path) -> List[Any]:
        """读取 JSON 数组文件，文件不存在或为空时返回空列表。"""
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"数据文件格式错误：{path}") from exc
        if not isinstance(raw, list):
            raise ValueError(f"数据文件应为 JSON 数组：{path}")
        return raw

    # ---------- 操作日志 ----------

    def log(self, operator: str, action: str, result: str, detail: str = "") -> OperationLog:
        """记录一条操作日志并立即持久化。"""
        entry = OperationLog(
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            operator=operator,
            action=action,
            result=result,
            detail=detail or "-",
        )
        self._logs.append(entry)
        self.save_logs()
        return entry

    def list_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """查询最近的日志记录。"""
        return [item.to_dict() for item in self._logs[-limit:]]

    # ---------- 账号增删改查 ----------

    def _next_user_id(self) -> int:
        return max((user.user_id for user in self._users), default=0) + 1

    def add_user(
        self, user_name: str, raw_password: str, role: str, real_name: str, *, operator: str = "system"
    ) -> User:
        """新增账号并立即持久化。

        :raises ValueError: 账号已存在或参数非法
        """
        user_name = str(user_name).strip()
        if self.get_user(user_name) is not None:
            raise ValueError(f"账号已存在：{user_name}")

        user = User(
            user_id=self._next_user_id(),
            user_name=user_name,
            password_hash=hash_password(raw_password),
            role=role,
            real_name=real_name,
        )
        self._users.append(user)
        self.save()
        self.log(operator, "新增账号", "成功", f"{user.user_name}（{user.role_name}）")
        return user

    def get_user(self, user_name: str) -> Optional[User]:
        """按账号查询用户，未找到返回 None。"""
        for user in self._users:
            if user.user_name == str(user_name).strip():
                return user
        return None

    def update_user(
        self, user_name: str, *, operator: str = "system", **fields: Any
    ) -> User:
        """修改账号信息（真实姓名、角色、密码）。

        :raises ValueError: 账号不存在或字段非法
        """
        user = self.get_user(user_name)
        if user is None:
            raise ValueError(f"账号不存在：{user_name}")

        if "real_name" in fields:
            user.real_name = str(fields["real_name"]).strip()
            if not user.real_name:
                raise ValueError("真实姓名不能为空")
        if "role" in fields:
            if fields["role"] not in ROLE_NAMES:
                raise ValueError(f"角色编码非法：{fields['role']}")
            user.role = str(fields["role"])
        if "password" in fields:
            user.password_hash = hash_password(str(fields["password"]))

        self.save()
        self.log(operator, "修改账号", "成功", user.user_name)
        return user

    def delete_user(self, user_name: str, *, operator: str = "system") -> User:
        """删除账号并立即持久化。

        :raises ValueError: 账号不存在
        """
        user = self.get_user(user_name)
        if user is None:
            raise ValueError(f"账号不存在：{user_name}")
        self._users.remove(user)
        self.save()
        self.log(operator, "删除账号", "成功", user.user_name)
        return user

    def list_users(self) -> List[Dict[str, Any]]:
        """查询全部账号（不含密码）。"""
        return [user.to_dict() for user in self._users]

    # ---------- 登录校验 ----------

    def login(self, user_name: str, raw_password: str) -> Dict[str, Any]:
        """登录校验：账号存在、密码正确、未超出失败次数。"""
        user = self.get_user(user_name)
        if user is None:
            self.log(user_name, "登录", "失败", "账号不存在")
            return {"success": False, "message": "账号或密码错误", "user": None}

        if self._login_failures.get(user.user_name, 0) >= MAX_LOGIN_FAILURES:
            self.log(user.user_name, "登录", "失败", "账号已锁定")
            return {"success": False, "message": "账号已锁定，请联系管理员", "user": None}

        if not user.check_password(raw_password):
            self._login_failures[user.user_name] = (
                self._login_failures.get(user.user_name, 0) + 1
            )
            self.log(user.user_name, "登录", "失败", "密码错误")
            return {"success": False, "message": "账号或密码错误", "user": None}

        self._login_failures[user.user_name] = 0
        self.log(user.user_name, "登录", "成功", f"角色 {user.role_name}")
        return {"success": True, "message": "登录成功", "user": user}

    # ---------- 权限控制 ----------

    def check_permission(self, user_name: str, permission: str) -> bool:
        """访问权限校验：判断账号是否具备指定权限码，并记录越权行为。"""
        user = self.get_user(user_name)
        if user is None:
            self.log(user_name, "权限校验", "失败", f"{permission}：账号不存在")
            return False

        allowed = permission in user.permissions
        self.log(
            user.user_name,
            "权限校验",
            "通过" if allowed else "拒绝",
            f"{permission}",
        )
        return allowed

    def __len__(self) -> int:
        return len(self._users)
