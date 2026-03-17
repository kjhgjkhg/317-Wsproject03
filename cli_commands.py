"""
命令行子命令模块

使用 argparse 实现所有子命令（add, list, done, delete, edit, search, export）。
"""
import argparse
from typing import Any
from data_manager import DataManager
from utils.validators import (
    validate_priority,
    validate_date,
    validate_description,
    validate_task_id
)
from utils.helpers import (
    print_task_table,
    export_to_markdown,
    sort_tasks
)


def setup_parser() -> argparse.ArgumentParser:
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="命令行 Todo List 管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    _setup_add_parser(subparsers)
    _setup_list_parser(subparsers)
    _setup_done_parser(subparsers)
    _setup_delete_parser(subparsers)
    _setup_edit_parser(subparsers)
    _setup_search_parser(subparsers)
    _setup_export_parser(subparsers)
    
    return parser


def _setup_add_parser(subparsers: Any) -> None:
    """设置 add 子命令"""
    parser = subparsers.add_parser("add", help="添加新任务")
    parser.add_argument(
        "description",
        help="任务描述"
    )
    parser.add_argument(
        "-p", "--priority",
        type=int,
        default=3,
        help="优先级 (1-5, 1最高, 默认3)"
    )
    parser.add_argument(
        "-d", "--due",
        help="截止日期 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "-c", "--category",
        default="未分类",
        help="任务类别 (默认: 未分类)"
    )
    parser.set_defaults(func=cmd_add)


def _setup_list_parser(subparsers: Any) -> None:
    """设置 list 子命令"""
    parser = subparsers.add_parser("list", help="列出所有任务")
    parser.add_argument(
        "-s", "--sort",
        choices=["priority", "date", "id"],
        default="priority",
        help="排序方式 (priority/date/id, 默认priority)"
    )
    parser.add_argument(
        "-c", "--category",
        help="按类别过滤"
    )
    parser.add_argument(
        "--completed",
        action="store_true",
        help="只显示已完成的任务"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="显示所有任务（包括已完成）"
    )
    parser.set_defaults(func=cmd_list)


def _setup_done_parser(subparsers: Any) -> None:
    """设置 done 子命令"""
    parser = subparsers.add_parser("done", help="标记任务为已完成")
    parser.add_argument(
        "id",
        type=int,
        help="任务ID"
    )
    parser.set_defaults(func=cmd_done)


def _setup_delete_parser(subparsers: Any) -> None:
    """设置 delete 子命令"""
    parser = subparsers.add_parser("delete", help="删除任务")
    parser.add_argument(
        "id",
        type=int,
        help="任务ID"
    )
    parser.set_defaults(func=cmd_delete)


def _setup_edit_parser(subparsers: Any) -> None:
    """设置 edit 子命令"""
    parser = subparsers.add_parser("edit", help="修改任务")
    parser.add_argument(
        "id",
        type=int,
        help="任务ID"
    )
    parser.add_argument(
        "--desc",
        dest="description",
        help="新的任务描述"
    )
    parser.add_argument(
        "-p", "--priority",
        type=int,
        help="新的优先级 (1-5)"
    )
    parser.add_argument(
        "-d", "--due",
        help="新的截止日期 (YYYY-MM-DD, 使用 'none' 清除)"
    )
    parser.add_argument(
        "-c", "--category",
        help="新的类别"
    )
    parser.set_defaults(func=cmd_edit)


def _setup_search_parser(subparsers: Any) -> None:
    """设置 search 子命令"""
    parser = subparsers.add_parser("search", help="搜索任务")
    parser.add_argument(
        "keyword",
        help="搜索关键字"
    )
    parser.set_defaults(func=cmd_search)


def _setup_export_parser(subparsers: Any) -> None:
    """设置 export 子命令"""
    parser = subparsers.add_parser("export", help="导出任务为Markdown报告")
    parser.add_argument(
        "-f", "--filename",
        default="todo_report.md",
        help="输出文件名 (默认: todo_report.md)"
    )
    parser.add_argument(
        "-c", "--category",
        help="只导出指定类别的任务"
    )
    parser.add_argument(
        "--completed",
        action="store_true",
        help="只导出已完成的任务"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="导出所有任务（包括已完成）"
    )
    parser.set_defaults(func=cmd_export)


def cmd_add(manager: DataManager, args: argparse.Namespace) -> None:
    """执行添加任务命令"""
    try:
        description = validate_description(args.description)
        priority = validate_priority(args.priority)
        due_date = validate_date(args.due) if args.due else None
        category = args.category.strip() if args.category else "未分类"
        
        task = manager.add_task(
            description=description,
            priority=priority,
            due_date=due_date,
            category=category
        )
        print(f"✓ 任务已添加: #{task.id} - {task.description}")
    except ValueError as e:
        print(f"错误: {e}")


def cmd_list(manager: DataManager, args: argparse.Namespace) -> None:
    """执行列出任务命令"""
    if args.completed:
        tasks = manager.get_completed_tasks()
    elif args.all:
        tasks = manager.get_all_tasks()
    else:
        tasks = manager.get_incomplete_tasks()
    
    if args.category:
        tasks = [t for t in tasks if t.category == args.category]
    
    if not tasks:
        print("没有找到任务")
        return
    
    tasks = sort_tasks(tasks, args.sort, manager)
    print_task_table(tasks)
    
    stats = manager.get_statistics()
    print(f"\n统计: 总计 {stats['total']} | 已完成 {stats['completed']} | 未完成 {stats['incomplete']} | 已过期 {stats['overdue']}")


def cmd_done(manager: DataManager, args: argparse.Namespace) -> None:
    """执行标记完成命令"""
    try:
        task_id = validate_task_id(args.id, manager)
        if manager.mark_completed(task_id):
            task = manager.get_task_by_id(task_id)
            print(f"✓ 任务 #{task_id} 已标记为完成: {task.description if task else ''}")
        else:
            print(f"错误: 无法标记任务 #{task_id}")
    except ValueError as e:
        print(f"错误: {e}")


def cmd_delete(manager: DataManager, args: argparse.Namespace) -> None:
    """执行删除任务命令"""
    try:
        task_id = validate_task_id(args.id, manager)
        task = manager.get_task_by_id(task_id)
        if manager.delete_task(task_id):
            print(f"✓ 任务 #{task_id} 已删除: {task.description if task else ''}")
        else:
            print(f"错误: 无法删除任务 #{task_id}")
    except ValueError as e:
        print(f"错误: {e}")


def cmd_edit(manager: DataManager, args: argparse.Namespace) -> None:
    """执行修改任务命令"""
    try:
        task_id = validate_task_id(args.id, manager)
        
        description = None
        priority = None
        due_date = None
        category = None
        
        if args.description:
            description = validate_description(args.description)
        
        if args.priority is not None:
            priority = validate_priority(args.priority)
        
        if args.due is not None:
            if args.due.lower() == "none":
                due_date = ""
            else:
                due_date = validate_date(args.due)
        
        if args.category is not None:
            category = args.category.strip()
        
        if all(v is None for v in [description, priority, due_date, category]):
            print("错误: 请指定至少一个要修改的字段")
            return
        
        if manager.update_task(
            task_id=task_id,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category
        ):
            task = manager.get_task_by_id(task_id)
            print(f"✓ 任务 #{task_id} 已更新")
            print(f"  {task}")
        else:
            print(f"错误: 无法更新任务 #{task_id}")
    except ValueError as e:
        print(f"错误: {e}")


def cmd_search(manager: DataManager, args: argparse.Namespace) -> None:
    """执行搜索任务命令"""
    tasks = manager.search_tasks(args.keyword)
    
    if not tasks:
        print(f"没有找到包含 '{args.keyword}' 的任务")
        return
    
    print(f"找到 {len(tasks)} 个匹配的任务:\n")
    print_task_table(tasks)


def cmd_export(manager: DataManager, args: argparse.Namespace) -> None:
    """执行导出命令"""
    if args.completed:
        tasks = manager.get_completed_tasks()
    elif args.all:
        tasks = manager.get_all_tasks()
    else:
        tasks = manager.get_incomplete_tasks()
    
    if args.category:
        tasks = [t for t in tasks if t.category == args.category]
    
    if not tasks:
        print("没有任务可导出")
        return
    
    try:
        output_path = export_to_markdown(tasks, args.filename)
        print(f"✓ 已导出 {len(tasks)} 个任务到: {output_path}")
    except Exception as e:
        print(f"错误: 导出失败 - {e}")
