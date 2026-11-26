"""用户与权限数据模型（纯标准库实现）。

对应设计文档中的 T_User 表与 RBAC 授权模型：
用户 --(拥有)--> 角色 --(包含)--> 权限。
"""

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Dict, Set

# 角色编码 -> 角色名称
ROLE_NAMES: Dict[str, str] = {
    "admin": "专业认证管理员",
    "teacher": "授课教师",
    "student": "在校学生",
}

# 角色编码 -> 权限集合（权限码形如 模块:资源:动作）
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "user:view",
        "user:create",
        "user:update",
        "user:delete",
        "role:assign",
        "log:view",
        "indicator:view",
        "indicator:edit",
        "archive:upload",
        "search:export",
    },
    "teacher": {
        "user:view",
        "indicator:view",
        "archive:upload",
        "search:export",
    },
    "student": {
        "indicator:view",
    },
}


def hash_password(raw: str) -> str:
    """对明文密码做加盐哈希。

    演示项目不引入第三方库，使用 SHA-256 拼接固定盐值，
    保证落库的始终是哈希值而非明文（真实环境应使用 BCrypt）。
    """
    return sha256(f"userauth${raw}".encode("utf-8")).hexdigest()


@dataclass
class User:
    """平台账号。

    :param user_id: 用户 ID（自增主键）
    :param user_name: 登录账号，唯一
    :param password_hash: 密码哈希值
    :param role: 角色编码，admin/teacher/student
    :param real_name: 真实姓名
    """

    user_id: int
    user_name: str
    password_hash: str
    role: str
    real_name: str

    def __post_init__(self) -> None:
        self.user_id = int(self.user_id)
        self.user_name = str(self.user_name).strip()
        self.password_hash = str(self.password_hash).strip()
        self.role = str(self.role).strip()
        self.real_name = str(self.real_name).strip()

        if self.user_id <= 0:
            raise ValueError("用户 ID 必须为正整数")
        if not self.user_name:
            raise ValueError("登录账号不能为空")
        if not self.password_hash:
            raise ValueError(f"账号 {self.user_name} 的密码不能为空")
        if self.role not in ROLE_NAMES:
            raise ValueError(f"账号 {self.user_name} 的角色编码非法：{self.role}")
        if not self.real_name:
            raise ValueError(f"账号 {self.user_name} 的真实姓名不能为空")

    @property
    def role_name(self) -> str:
        """角色中文名称。"""
        return ROLE_NAMES.get(self.role, self.role)

    @property
    def permissions(self) -> Set[str]:
        """该账号通过角色获得的权限集合。"""
        return set(ROLE_PERMISSIONS.get(self.role, set()))

    def check_password(self, raw: str) -> bool:
        """校验明文密码是否正确。"""
        return self.password_hash == hash_password(raw)

    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """转换为字典，默认不输出密码哈希。"""
        data = asdict(self)
        if not include_password:
            data.pop("password_hash", None)
        data["role_name"] = self.role_name
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """从字典还原账号。"""
        required = ("user_id", "user_name", "password_hash", "role", "real_name")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"账号数据缺少字段：{', '.join(missing)}")
        return cls(**{key: data[key] for key in required})


@dataclass
class OperationLog:
    """操作日志（登录、授权、越权、增删改）。"""

    time: str
    operator: str
    action: str
    result: str
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationLog":
        required = ("time", "operator", "action", "result", "detail")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"日志数据缺少字段：{', '.join(missing)}")
        return cls(**{key: data[key] for key in required})
