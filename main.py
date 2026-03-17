"""
Todo List 管理工具 - 程序入口
负责子命令解析与程序调度
"""
import sys

from cli_commands import create_parser, execute_command


def main() -> int:
    """
    主函数入口
    
    Returns:
        退出码
    """
    parser = create_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        args = parser.parse_args()
        execute_command(args)
        return 0
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
