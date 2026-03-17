"""
main.py - 程序主入口
负责子命令解析与程序调度
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli_commands import create_parser, run_command


def main() -> int:
    """
    主函数入口
    
    Returns:
        退出码
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        run_command(args)
        return 0
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        print(f"程序错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
