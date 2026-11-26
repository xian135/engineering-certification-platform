"""控制台演示：账号增删改查、登录校验、权限控制与操作日志。"""

from .models import ROLE_NAMES, User, hash_password
from .service import UserService

SEPARATOR = "=" * 64

# 首次运行时写入的示例账号
DEMO_USERS = (
    ("admin", "admin123", "admin", "张三"),
    ("songzy", "123456", "teacher", "宋老师"),
    ("student01", "123456", "student", "李同学"),
)


def seed_demo_users(service: UserService) -> bool:
    """账号表为空时写入示例账号，返回是否执行了写入。"""
    if len(service) > 0:
        return False
    for user_name, password, role, real_name in DEMO_USERS:
        service.add_user(user_name, password, role, real_name, operator="system")
    return True


def print_users(service: UserService) -> None:
    """以表格形式输出全部账号及其角色、权限数量。"""
    records = service.list_users()

    print(SEPARATOR)
    print("工程教育专业认证支撑平台 —— 用户与权限管理模块")
    print(SEPARATOR)
    print(f"账号总数：{len(records)}")
    print()
    print(f"{'ID':<4}{'账号':<12}{'姓名':<8}{'角色':<12}{'权限数':<6}")
    print("-" * 64)
    for record in records:
        user = service.get_user(record["user_name"])
        print(
            f"{record['user_id']:<4}{record['user_name']:<12}"
            f"{record['real_name']:<8}{record['role_name']:<12}"
            f"{len(user.permissions) if user else 0:<6}"
        )
    print("-" * 64)


def demo_crud(service: UserService) -> None:
    """演示账号的增、改、删。"""
    print("\n【账号增删改查】")
    if service.get_user("teacher02") is None:
        user = service.add_user("teacher02", "123456", "teacher", "王老师", operator="admin")
        print(f"  新增账号：{user.user_name}（{user.role_name}，ID={user.user_id}）")

    user = service.update_user("teacher02", operator="admin", role="admin", real_name="王老师（已授权）")
    print(f"  修改账号：{user.user_name} 角色调整为 {user.role_name}")

    print(f"  查询账号：{service.get_user('teacher02').to_dict()}")

    service.delete_user("teacher02", operator="admin")
    print("  删除账号：teacher02 已移除")
    print(f"  删除后账号总数：{len(service)}")


def demo_login(service: UserService) -> None:
    """演示登录校验：正确密码、错误密码、账号不存在。"""
    print("\n【登录校验】")
    for account, password in (("songzy", "123456"), ("songzy", "wrong"), ("nobody", "123456")):
        result = service.login(account, password)
        print(f"  {account:<10} / {password:<8} -> {result['message']}")


def demo_permission(service: UserService) -> None:
    """演示访问权限控制：不同角色访问同一权限码的结果。"""
    print("\n【访问权限控制】")
    checks = (
        ("admin", "user:create"),
        ("songzy", "user:create"),
        ("songzy", "archive:upload"),
        ("student01", "user:view"),
    )
    for account, permission in checks:
        allowed = service.check_permission(account, permission)
        print(f"  {account:<10} 请求 {permission:<16} -> {'允许' if allowed else '拒绝（403）'}")


def print_logs(service: UserService, limit: int = 12) -> None:
    """输出最近的操作日志。"""
    print("\n【操作日志】")
    print(f"{'时间':<20}{'操作人':<12}{'动作':<10}{'结果':<8}{'详情'}")
    print("-" * 64)
    for record in service.list_logs(limit):
        print(
            f"{record['time']:<20}{record['operator']:<12}"
            f"{record['action']:<10}{record['result']:<8}{record['detail']}"
        )
    print("-" * 64)


def run() -> None:
    """模块入口：加载数据、初始化示例账号并演示各项功能。"""
    service = UserService()
    if seed_demo_users(service):
        print(f"已初始化 {len(DEMO_USERS)} 个示例账号：{service.user_file}\n")

    print_users(service)
    demo_crud(service)
    demo_login(service)
    demo_permission(service)
    print_logs(service)
    print(f"\n操作日志已保存：{service.log_file}")


if __name__ == "__main__":
    run()
