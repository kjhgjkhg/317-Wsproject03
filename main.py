"""
Todo List 管理工具 - 主入口模块

负责子命令解析与程序调度。
"""
import sys
from cli_commands import setup_parser
from data_manager import DataManager
from utils.config import DATA_DIR, DATA_FILE


def main() -> None:
    parser = setup_parser()
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(0)
    
    try:
        manager = DataManager(DATA_FILE)
        args.func(manager, args)
    except FileNotFoundError as e:
        print(f"错误: 数据目录不存在 - {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"错误: 权限不足 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
