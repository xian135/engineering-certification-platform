"""工程教育专业认证支撑平台 —— 功能模块演示入口。"""

from modules.indicator_management.console import run as run_indicator_demo
from modules.material_archive.console import run as run_material_archive_demo


def main() -> None:
    """依次运行各功能模块的控制台演示。"""
    run_indicator_demo()
    run_material_archive_demo()


if __name__ == "__main__":
    main()
