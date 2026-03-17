"""
辅助函数模块

提供排序、过滤、Markdown格式化、表格打印等辅助函数。
"""
import os
from datetime import datetime
from typing import List, Optional
from core_task import Task
from utils.config import OUTPUT_DIR, TABLE_HEADERS, TABLE_COLUMN_WIDTHS


def print_task_table(tasks: List[Task]) -> None:
    """
    以表格形式打印任务列表
    
    Args:
        tasks: 要打印的任务列表
    """
    if not tasks:
        print("没有任务")
        return
    
    widths = TABLE_COLUMN_WIDTHS
    
    separator = "+" + "+".join([
        "-" * (widths["id"] + 2),
        "-" * (widths["status"] + 2),
        "-" * (widths["priority"] + 2),
        "-" * (widths["description"] + 2),
        "-" * (widths["due_date"] + 2),
        "-" * (widths["category"] + 2)
    ]) + "+"
    
    header = "|" + "|".join([
        " ID ".center(widths["id"]),
        " 状态 ".center(widths["status"]),
        " 优先级 ".center(widths["priority"]),
        " 描述 ".ljust(widths["description"]),
        " 截止日期 ".center(widths["due_date"]),
        " 类别 ".center(widths["category"])
    ]) + "|"
    
    print(separator)
    print(header)
    print(separator)
    
    for task in tasks:
        status = "✓ 已完成" if task.completed else "○ 未完成"
        priority_text = f"P{task.priority}"
        description = truncate_text(task.description, widths["description"])
        due_date = task.due_date if task.due_date else "-"
        category = truncate_text(task.category, widths["category"])
        
        if task.is_overdue():
            due_date = f"!{due_date}"
        
        row = "|" + "|".join([
            f" {str(task.id)} ".center(widths["id"]),
            f" {status} ".center(widths["status"]),
            f" {priority_text} ".center(widths["priority"]),
            f" {description} ".ljust(widths["description"] + 1),
            f" {due_date} ".center(widths["due_date"]),
            f" {category} ".center(widths["category"])
        ]) + "|"
        
        print(row)
    
    print(separator)


def truncate_text(text: str, max_length: int) -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sort_tasks(tasks: List[Task], sort_by: str, manager) -> List[Task]:
    """
    根据指定方式排序任务
    
    Args:
        tasks: 要排序的任务列表
        sort_by: 排序方式 (priority/date/id)
        manager: 数据管理器实例
        
    Returns:
        排序后的任务列表
    """
    if sort_by == "priority":
        return manager.sort_by_priority(tasks)
    elif sort_by == "date":
        return manager.sort_by_due_date(tasks)
    elif sort_by == "id":
        return sorted(tasks, key=lambda t: t.id)
    else:
        return tasks


def export_to_markdown(tasks: List[Task], filename: str) -> str:
    """
    将任务列表导出为Markdown格式报告
    
    Args:
        tasks: 要导出的任务列表
        filename: 输出文件名
        
    Returns:
        输出文件的完整路径
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    lines = []
    lines.append("# Todo List 报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**任务总数**: {len(tasks)}")
    lines.append("")
    
    completed_tasks = [t for t in tasks if t.completed]
    incomplete_tasks = [t for t in tasks if not t.completed]
    
    lines.append("## 统计概览")
    lines.append("")
    lines.append(f"- 总任务数: {len(tasks)}")
    lines.append(f"- 已完成: {len(completed_tasks)}")
    lines.append(f"- 未完成: {len(incomplete_tasks)}")
    lines.append(f"- 已过期: {len([t for t in tasks if t.is_overdue()])}")
    lines.append("")
    
    if incomplete_tasks:
        lines.append("## 未完成任务")
        lines.append("")
        lines.append("| ID | 优先级 | 描述 | 截止日期 | 类别 |")
        lines.append("|----|--------|------|----------|------|")
        for task in incomplete_tasks:
            due = task.due_date if task.due_date else "-"
            overdue_marker = " ⚠️" if task.is_overdue() else ""
            lines.append(f"| {task.id} | P{task.priority} | {task.description}{overdue_marker} | {due} | {task.category} |")
        lines.append("")
    
    if completed_tasks:
        lines.append("## 已完成任务")
        lines.append("")
        lines.append("| ID | 优先级 | 描述 | 类别 |")
        lines.append("|----|--------|------|------|")
        for task in completed_tasks:
            lines.append(f"| {task.id} | P{task.priority} | {task.description} | {task.category} |")
        lines.append("")
    
    categories = {}
    for task in tasks:
        if task.category not in categories:
            categories[task.category] = []
        categories[task.category].append(task)
    
    lines.append("## 按类别分组")
    lines.append("")
    for category, category_tasks in sorted(categories.items()):
        lines.append(f"### {category} ({len(category_tasks)} 个任务)")
        lines.append("")
        for task in category_tasks:
            status = "✓" if task.completed else "○"
            lines.append(f"- {status} #{task.id} (P{task.priority}) {task.description}")
        lines.append("")
    
    content = "\n".join(lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


def format_task_summary(task: Task) -> str:
    """
    格式化任务摘要信息
    
    Args:
        task: 任务对象
        
    Returns:
        格式化的任务摘要字符串
    """
    status = "✓" if task.completed else "○"
    due = f" (截止: {task.due_date})" if task.due_date else ""
    overdue = " ⚠️ 已过期" if task.is_overdue() else ""
    return f"{status} #{task.id} [P{task.priority}] {task.description}{due}{overdue}"
