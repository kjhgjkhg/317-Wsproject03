"""
cli_commands.py - 命令行命令模块
使用argparse实现所有子命令 (add, list, done, delete, edit, search, export)
"""
import argparse
from typing import Optional, List

from data_manager import DataManager
from core_task import Task, TaskValidator
from utils.validators import validate_task_id
from utils.helpers import (
    sort_tasks,
    filter_tasks,
    search_tasks,
    print_table,
    format_markdown,
    save_markdown_report,
    get_status_display,
    get_priority_display
)
from utils.config import (
    PRIORITY_DEFAULT,
    CATEGORY_DEFAULT,
    STATUS_PENDING,
    VALID_CATEGORIES
)


class TodoCLI:
    """
    Todo命令行接口类
    封装所有子命令的实现
    """
    
    def __init__(self):
        """初始化CLI"""
        self.manager = DataManager()
    
    def cmd_add(self, args: argparse.Namespace) -> None:
        """
        添加任务命令
        
        Args:
            args: 命令行参数
        """
        validator = TaskValidator()
        result = validator.validate_create(
            description=args.description,
            priority=str(args.priority),
            deadline=args.deadline or "",
            category=args.category or ""
        )
        
        if not result["valid"]:
            for error in result["errors"]:
                print(f"错误: {error}")
            return
        
        for warning in result["warnings"]:
            print(f"警告: {warning}")
        
        task_id = self.manager.get_next_id()
        task = Task(
            task_id=task_id,
            description=result["data"]["description"],
            priority=result["data"]["priority"],
            deadline=result["data"]["deadline"],
            category=result["data"]["category"]
        )
        
        self.manager.add_task(task)
        print(f"成功添加任务 [ID: {task_id}]")
        print(f"  描述: {task.description}")
        print(f"  优先级: {get_priority_display(task.priority)}")
        if task.deadline:
            print(f"  截止日期: {task.deadline}")
        print(f"  类别: {task.category}")
    
    def cmd_list(self, args: argparse.Namespace) -> None:
        """
        列出任务命令
        
        Args:
            args: 命令行参数
        """
        tasks = self.manager.get_all_tasks()
        
        if not tasks:
            print("暂无任务")
            return
        
        if args.category:
            tasks = [t for t in tasks if t.category == args.category]
        
        if args.status:
            status_filter = "completed" if args.status in ("completed", "done", "已完成") else "pending"
            tasks = [t for t in tasks if t.status == status_filter]
        
        if args.sort:
            sort_field = args.sort
            reverse = args.order == "desc"
            if sort_field == "priority":
                reverse = args.order != "asc"
            tasks_data = [t.to_dict() for t in tasks]
            tasks_data = sort_tasks(tasks_data, sort_field, reverse)
            tasks = [Task.from_dict(t) for t in tasks_data]
        
        print_table([t.to_dict() for t in tasks])
    
    def cmd_done(self, args: argparse.Namespace) -> None:
        """
        标记任务完成命令
        
        Args:
            args: 命令行参数
        """
        existing_ids = self.manager.get_task_ids()
        valid, task_id, error = validate_task_id(str(args.id), existing_ids)
        
        if not valid:
            print(f"错误: {error}")
            return
        
        task = self.manager.mark_completed(task_id)
        if task:
            print(f"任务 [ID: {task_id}] 已标记为完成")
            print(f"  描述: {task.description}")
        else:
            print(f"错误: 无法更新任务 [ID: {task_id}]")
    
    def cmd_delete(self, args: argparse.Namespace) -> None:
        """
        删除任务命令
        
        Args:
            args: 命令行参数
        """
        existing_ids = self.manager.get_task_ids()
        valid, task_id, error = validate_task_id(str(args.id), existing_ids)
        
        if not valid:
            print(f"错误: {error}")
            return
        
        task = self.manager.get_task_by_id(task_id)
        if task:
            print(f"即将删除任务 [ID: {task_id}]: {task.description}")
            if args.force or input("确认删除? (y/N): ").lower() == "y":
                self.manager.delete_task(task_id)
                print(f"任务 [ID: {task_id}] 已删除")
            else:
                print("已取消删除")
        else:
            print(f"错误: 任务 [ID: {task_id}] 不存在")
    
    def cmd_edit(self, args: argparse.Namespace) -> None:
        """
        编辑任务命令
        
        Args:
            args: 命令行参数
        """
        existing_ids = self.manager.get_task_ids()
        valid, task_id, error = validate_task_id(str(args.id), existing_ids)
        
        if not valid:
            print(f"错误: {error}")
            return
        
        task = self.manager.get_task_by_id(task_id)
        if not task:
            print(f"错误: 任务 [ID: {task_id}] 不存在")
            return
        
        print(f"当前任务信息:")
        print(f"  ID: {task.id}")
        print(f"  描述: {task.description}")
        print(f"  优先级: {get_priority_display(task.priority)}")
        print(f"  截止日期: {task.deadline or '未设置'}")
        print(f"  类别: {task.category}")
        print(f"  状态: {get_status_display(task.status)}")
        print()
        
        validator = TaskValidator()
        result = validator.validate_update(
            description=args.description,
            priority=str(args.priority) if args.priority else None,
            deadline=args.deadline,
            category=args.category
        )
        
        if not result["valid"]:
            for error in result["errors"]:
                print(f"错误: {error}")
            return
        
        for warning in result["warnings"]:
            print(f"警告: {warning}")
        
        if not result["data"]:
            print("没有要更新的字段")
            return
        
        self.manager.update_task(task_id, **result["data"])
        print(f"任务 [ID: {task_id}] 已更新")
        
        updated_task = self.manager.get_task_by_id(task_id)
        if updated_task:
            print(f"  描述: {updated_task.description}")
            print(f"  优先级: {get_priority_display(updated_task.priority)}")
            print(f"  截止日期: {updated_task.deadline or '未设置'}")
            print(f"  类别: {updated_task.category}")
    
    def cmd_search(self, args: argparse.Namespace) -> None:
        """
        搜索任务命令
        
        Args:
            args: 命令行参数
        """
        if not args.keyword:
            print("错误: 请提供搜索关键字")
            return
        
        tasks = self.manager.search_tasks(args.keyword)
        
        if not tasks:
            print(f"未找到包含 '{args.keyword}' 的任务")
            return
        
        print(f"搜索结果 (关键字: '{args.keyword}'):")
        print_table([t.to_dict() for t in tasks])
    
    def cmd_export(self, args: argparse.Namespace) -> None:
        """
        导出任务报告命令
        
        Args:
            args: 命令行参数
        """
        tasks = self.manager.get_all_tasks()
        
        if args.status:
            status_filter = "completed" if args.status in ("completed", "done", "已完成") else "pending"
            tasks = [t for t in tasks if t.status == status_filter]
        
        if args.category:
            tasks = [t for t in tasks if t.category == args.category]
        
        title = args.title or "待办事项报告"
        markdown_content = format_markdown([t.to_dict() for t in tasks], title)
        
        filepath = save_markdown_report(markdown_content, args.output)
        print(f"报告已导出: {filepath}")
        print(f"共导出 {len(tasks)} 条任务")


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        ArgumentParser实例
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="命令行待办事项管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  todo add "完成项目报告" -p 1 -d 2024-12-31 -c 工作
  todo list --sort priority --order desc
  todo done 1
  todo edit 1 -d "新的描述"
  todo search 项目
  todo export --output report.md
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    add_parser = subparsers.add_parser("add", help="添加新任务")
    add_parser.add_argument("description", help="任务描述")
    add_parser.add_argument("-p", "--priority", type=int, default=PRIORITY_DEFAULT,
                           help=f"优先级 (1-5, 默认{PRIORITY_DEFAULT})")
    add_parser.add_argument("-d", "--deadline", default="",
                           help="截止日期 (YYYY-MM-DD)")
    add_parser.add_argument("-c", "--category", default=CATEGORY_DEFAULT,
                           help=f"类别 (默认: {CATEGORY_DEFAULT})")
    
    list_parser = subparsers.add_parser("list", help="列出所有任务")
    list_parser.add_argument("-c", "--category", help="按类别过滤")
    list_parser.add_argument("-s", "--status", help="按状态过滤 (pending/completed)")
    list_parser.add_argument("--sort", choices=["priority", "deadline", "category", "id"],
                            default="priority", help="排序字段")
    list_parser.add_argument("--order", choices=["asc", "desc"], default="desc",
                            help="排序顺序")
    
    done_parser = subparsers.add_parser("done", help="标记任务为已完成")
    done_parser.add_argument("id", type=int, help="任务ID")
    
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("id", type=int, help="任务ID")
    delete_parser.add_argument("-f", "--force", action="store_true",
                              help="强制删除，不确认")
    
    edit_parser = subparsers.add_parser("edit", help="编辑任务")
    edit_parser.add_argument("id", type=int, help="任务ID")
    edit_parser.add_argument("-d", "--description", help="新描述")
    edit_parser.add_argument("-p", "--priority", type=int, help="新优先级 (1-5)")
    edit_parser.add_argument("--deadline", help="新截止日期 (YYYY-MM-DD)")
    edit_parser.add_argument("-c", "--category", help="新类别")
    
    search_parser = subparsers.add_parser("search", help="搜索任务")
    search_parser.add_argument("keyword", help="搜索关键字")
    
    export_parser = subparsers.add_parser("export", help="导出任务报告")
    export_parser.add_argument("-o", "--output", help="输出文件名")
    export_parser.add_argument("-t", "--title", help="报告标题")
    export_parser.add_argument("-c", "--category", help="按类别过滤")
    export_parser.add_argument("-s", "--status", help="按状态过滤")
    
    return parser


def run_command(args: argparse.Namespace) -> None:
    """
    执行命令
    
    Args:
        args: 解析后的命令行参数
    """
    cli = TodoCLI()
    
    command_map = {
        "add": cli.cmd_add,
        "list": cli.cmd_list,
        "done": cli.cmd_done,
        "delete": cli.cmd_delete,
        "edit": cli.cmd_edit,
        "search": cli.cmd_search,
        "export": cli.cmd_export
    }
    
    if args.command is None:
        print("请指定命令。使用 --help 查看帮助。")
        return
    
    handler = command_map.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            print(f"错误: {e}")
    else:
        print(f"未知命令: {args.command}")
