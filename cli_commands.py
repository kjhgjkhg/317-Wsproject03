"""
CLI 命令模块
使用 argparse 实现所有子命令 (add, list, done, delete, edit, search, export)
"""
import argparse
import os
from typing import Optional

from data_manager import DataManager
from utils.config import OUTPUT_BUILD_DIR, VALID_CATEGORIES
from utils.validators import validate_priority, validate_date, validate_id
from utils.helpers import (
    sort_tasks_by_priority,
    sort_tasks_by_due_date,
    filter_tasks_by_category,
    filter_tasks_by_status,
    search_tasks,
    print_tasks_table,
    format_markdown_report,
    generate_export_filename,
)


class CLICommands:
    """CLI命令处理器"""
    
    def __init__(self):
        """初始化CLI命令处理器"""
        self.data_manager = DataManager()
    
    def cmd_add(self, args: argparse.Namespace) -> None:
        """
        添加任务命令
        
        Args:
            args: 命令行参数
        """
        valid, priority_val, error = validate_priority(str(args.priority))
        if not valid:
            print(f"错误: {error}")
            return
        
        valid, due_date_val, error = validate_date(args.due_date or "")
        if not valid:
            print(f"错误: {error}")
            return
        
        category = args.category if args.category else "未分类"
        
        success, task_id, error = self.data_manager.add_task(
            description=args.description,
            priority=priority_val,
            due_date=due_date_val,
            category=category,
        )
        
        if success:
            print(f"成功: 已添加任务 ID={task_id}")
        else:
            print(f"错误: {error}")
    
    def cmd_list(self, args: argparse.Namespace) -> None:
        """
        列出任务命令
        
        Args:
            args: 命令行参数
        """
        tasks = self.data_manager.get_tasks_as_dicts()
        
        if args.category:
            tasks = filter_tasks_by_category(tasks, args.category)
        
        if args.completed_only:
            tasks = filter_tasks_by_status(tasks, "completed")
        elif args.pending_only:
            tasks = filter_tasks_by_status(tasks, "pending")
        
        if args.sort_by == "priority":
            tasks = sort_tasks_by_priority(tasks, descending=False)
        elif args.sort_by == "due_date":
            tasks = sort_tasks_by_due_date(tasks, ascending=True)
        
        print_tasks_table(tasks)
    
    def cmd_done(self, args: argparse.Namespace) -> None:
        """
        标记任务完成命令
        
        Args:
            args: 命令行参数
        """
        valid, task_id, error = validate_id(str(args.id))
        if not valid:
            print(f"错误: {error}")
            return
        
        success, error = self.data_manager.mark_completed(task_id)
        if success:
            print(f"成功: 任务 ID={task_id} 已标记为完成")
        else:
            print(f"错误: {error}")
    
    def cmd_delete(self, args: argparse.Namespace) -> None:
        """
        删除任务命令
        
        Args:
            args: 命令行参数
        """
        valid, task_id, error = validate_id(str(args.id))
        if not valid:
            print(f"错误: {error}")
            return
        
        success, error = self.data_manager.delete_task(task_id)
        if success:
            print(f"成功: 已删除任务 ID={task_id}")
        else:
            print(f"错误: {error}")
    
    def cmd_edit(self, args: argparse.Namespace) -> None:
        """
        编辑任务命令
        
        Args:
            args: 命令行参数
        """
        valid, task_id, error = validate_id(str(args.id))
        if not valid:
            print(f"错误: {error}")
            return
        
        priority_val = None
        if args.priority is not None:
            valid, priority_val, error = validate_priority(str(args.priority))
            if not valid:
                print(f"错误: {error}")
                return
        
        due_date_val = None
        if args.due_date is not None:
            valid, due_date_val, error = validate_date(args.due_date)
            if not valid:
                print(f"错误: {error}")
                return
        
        success, error = self.data_manager.update_task(
            task_id=task_id,
            description=args.description,
            priority=priority_val,
            due_date=due_date_val,
            category=args.category,
        )
        
        if success:
            print(f"成功: 已更新任务 ID={task_id}")
        else:
            print(f"错误: {error}")
    
    def cmd_search(self, args: argparse.Namespace) -> None:
        """
        搜索任务命令
        
        Args:
            args: 命令行参数
        """
        tasks = self.data_manager.get_tasks_as_dicts()
        results = search_tasks(tasks, args.keyword)
        
        if results:
            print(f"找到 {len(results)} 条匹配的任务:")
            print_tasks_table(results)
        else:
            print(f"未找到包含 '{args.keyword}' 的任务")
    
    def cmd_export(self, args: argparse.Namespace) -> None:
        """
        导出任务报告命令
        
        Args:
            args: 命令行参数
        """
        tasks = self.data_manager.get_tasks_as_dicts()
        
        if not tasks:
            print("警告: 没有任务可导出")
            return
        
        report_content = format_markdown_report(tasks, title=args.title or "待办事项报告")
        
        filename = args.output or generate_export_filename()
        if not filename.endswith(".md"):
            filename += ".md"
        
        output_path = os.path.join(OUTPUT_BUILD_DIR, filename)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"成功: 报告已导出到 {output_path}")
        except PermissionError:
            print(f"错误: 无权限写入文件 {output_path}")
        except Exception as e:
            print(f"错误: 导出失败: {e}")


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
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    parser_add = subparsers.add_parser("add", help="添加新任务")
    parser_add.add_argument("description", help="任务描述")
    parser_add.add_argument("-p", "--priority", type=int, default=3, help="优先级 (1-5, 默认3)")
    parser_add.add_argument("-d", "--due-date", dest="due_date", help="截止日期 (YYYY-MM-DD)")
    parser_add.add_argument("-c", "--category", help=f"类别 ({', '.join(VALID_CATEGORIES)})")
    
    parser_list = subparsers.add_parser("list", help="列出所有任务")
    parser_list.add_argument("-c", "--category", help="按类别过滤")
    parser_list.add_argument("-s", "--sort-by", dest="sort_by", choices=["priority", "due_date"], default="priority", help="排序方式")
    parser_list.add_argument("--completed", dest="completed_only", action="store_true", help="仅显示已完成任务")
    parser_list.add_argument("--pending", dest="pending_only", action="store_true", help="仅显示待办任务")
    
    parser_done = subparsers.add_parser("done", help="标记任务为已完成")
    parser_done.add_argument("id", type=int, help="任务ID")
    
    parser_delete = subparsers.add_parser("delete", help="删除任务")
    parser_delete.add_argument("id", type=int, help="任务ID")
    
    parser_edit = subparsers.add_parser("edit", help="修改任务")
    parser_edit.add_argument("id", type=int, help="任务ID")
    parser_edit.add_argument("-d", "--description", help="新任务描述")
    parser_edit.add_argument("-p", "--priority", type=int, help="新优先级 (1-5)")
    parser_edit.add_argument("--due-date", dest="due_date", help="新截止日期 (YYYY-MM-DD)")
    parser_edit.add_argument("-c", "--category", help="新类别")
    
    parser_search = subparsers.add_parser("search", help="搜索任务")
    parser_search.add_argument("keyword", help="搜索关键字")
    
    parser_export = subparsers.add_parser("export", help="导出任务报告")
    parser_export.add_argument("-t", "--title", help="报告标题")
    parser_export.add_argument("-o", "--output", help="输出文件名")
    
    return parser


def execute_command(args: argparse.Namespace) -> None:
    """
    执行命令
    
    Args:
        args: 解析后的命令行参数
    """
    cli = CLICommands()
    
    command_handlers = {
        "add": cli.cmd_add,
        "list": cli.cmd_list,
        "done": cli.cmd_done,
        "delete": cli.cmd_delete,
        "edit": cli.cmd_edit,
        "search": cli.cmd_search,
        "export": cli.cmd_export,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print("错误: 未知命令。使用 -h 查看帮助。")
