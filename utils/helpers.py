"""
utils/helpers.py - 辅助函数模块
提供排序、过滤、Markdown格式化、表格打印等功能
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from utils.config import (
    DATE_FORMAT,
    DATETIME_FORMAT,
    STATUS_PENDING,
    STATUS_COMPLETED,
    EXPORT_FILENAME_PREFIX,
    EXPORT_FILE_EXT,
    OUTPUT_BUILD_DIR
)


def sort_tasks(tasks: List[Dict[str, Any]], field: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    对任务列表进行排序
    
    Args:
        tasks: 任务列表
        field: 排序字段
        reverse: 是否降序
        
    Returns:
        排序后的任务列表
    """
    if not tasks:
        return tasks
    
    def sort_key(task: Dict[str, Any]) -> Any:
        value = task.get(field)
        if field == "deadline":
            if not value:
                return datetime.max
            try:
                return datetime.strptime(value, DATE_FORMAT)
            except ValueError:
                return datetime.max
        elif field == "priority":
            return -value if not reverse else value
        return value if value is not None else ""
    
    return sorted(tasks, key=sort_key, reverse=reverse if field != "priority" else not reverse)


def filter_tasks(tasks: List[Dict[str, Any]], 
                 category: Optional[str] = None,
                 status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    过滤任务列表
    
    Args:
        tasks: 任务列表
        category: 类别过滤
        status: 状态过滤
        
    Returns:
        过滤后的任务列表
    """
    result = tasks
    
    if category:
        result = [t for t in result if t.get("category") == category]
    
    if status:
        result = [t for t in result if t.get("status") == status]
    
    return result


def search_tasks(tasks: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """
    搜索任务
    
    Args:
        tasks: 任务列表
        keyword: 搜索关键字
        
    Returns:
        匹配的任务列表
    """
    if not keyword:
        return tasks
    
    keyword = keyword.lower()
    return [
        t for t in tasks
        if keyword in t.get("description", "").lower()
        or keyword in t.get("category", "").lower()
    ]


def print_table(tasks: List[Dict[str, Any]]) -> None:
    """
    以表格形式打印任务列表
    
    Args:
        tasks: 任务列表
    """
    if not tasks:
        print("暂无任务")
        return
    
    headers = ["ID", "描述", "优先级", "截止日期", "类别", "状态"]
    col_widths = [5, 30, 8, 12, 10, 10]
    
    def truncate(text: str, width: int) -> str:
        text = str(text) if text else ""
        return text[:width - 2] + ".." if len(text) > width else text
    
    def get_display_width(text: str) -> int:
        width = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                width += 2
            else:
                width += 1
        return width
    
    def pad_text(text: str, width: int) -> str:
        text = str(text) if text else ""
        current_width = get_display_width(text)
        if current_width >= width:
            return text[:width]
        return text + " " * (width - current_width)
    
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    print(separator)
    header_row = "|" + "|".join([f" {pad_text(h, w)} " for h, w in zip(headers, col_widths)]) + "|"
    print(header_row)
    print(separator)
    
    for task in tasks:
        status_display = "已完成" if task.get("status") == STATUS_COMPLETED else "待办"
        row_data = [
            str(task.get("id", "")),
            truncate(task.get("description", ""), col_widths[1]),
            str(task.get("priority", "")),
            task.get("deadline", "-"),
            task.get("category", "-"),
            status_display
        ]
        row = "|" + "|".join([f" {pad_text(d, w)} " for d, w in zip(row_data, col_widths)]) + "|"
        print(row)
    
    print(separator)
    print(f"共 {len(tasks)} 条任务")


def format_markdown(tasks: List[Dict[str, Any]], title: str = "待办事项报告") -> str:
    """
    将任务列表格式化为Markdown
    
    Args:
        tasks: 任务列表
        title: 报告标题
        
    Returns:
        Markdown格式字符串
    """
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"生成时间: {datetime.now().strftime(DATETIME_FORMAT)}")
    lines.append("")
    lines.append(f"**任务总数**: {len(tasks)}")
    lines.append("")
    
    pending_tasks = [t for t in tasks if t.get("status") == STATUS_PENDING]
    completed_tasks = [t for t in tasks if t.get("status") == STATUS_COMPLETED]
    
    lines.append(f"- 待办: {len(pending_tasks)}")
    lines.append(f"- 已完成: {len(completed_tasks)}")
    lines.append("")
    
    if pending_tasks:
        lines.append("## 待办任务")
        lines.append("")
        lines.append("| ID | 描述 | 优先级 | 截止日期 | 类别 |")
        lines.append("|----|------|--------|----------|------|")
        for task in pending_tasks:
            desc = task.get("description", "").replace("|", "\\|")
            deadline = task.get("deadline", "-")
            lines.append(
                f"| {task.get('id')} | {desc} | {task.get('priority')} | "
                f"{deadline} | {task.get('category', '-')} |"
            )
        lines.append("")
    
    if completed_tasks:
        lines.append("## 已完成任务")
        lines.append("")
        lines.append("| ID | 描述 | 类别 |")
        lines.append("|----|------|------|")
        for task in completed_tasks:
            desc = task.get("description", "").replace("|", "\\|")
            lines.append(f"| {task.get('id')} | {desc} | {task.get('category', '-')} |")
        lines.append("")
    
    lines.append("---")
    lines.append("*由 Todo List 管理工具自动生成*")
    
    return "\n".join(lines)


def save_markdown_report(content: str, filename: Optional[str] = None) -> str:
    """
    保存Markdown报告到输出目录
    
    Args:
        content: Markdown内容
        filename: 自定义文件名
        
    Returns:
        保存的文件路径
    """
    import os
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{EXPORT_FILENAME_PREFIX}{timestamp}{EXPORT_FILE_EXT}"
    elif not filename.endswith(EXPORT_FILE_EXT):
        filename += EXPORT_FILE_EXT
    
    filepath = os.path.join(OUTPUT_BUILD_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def get_status_display(status: str) -> str:
    """
    获取状态的显示文本
    
    Args:
        status: 状态值
        
    Returns:
        显示文本
    """
    status_map = {
        STATUS_PENDING: "待办",
        STATUS_COMPLETED: "已完成"
    }
    return status_map.get(status, status)


def get_priority_display(priority: int) -> str:
    """
    获取优先级的显示文本
    
    Args:
        priority: 优先级值
        
    Returns:
        显示文本
    """
    priority_map = {
        1: "最高",
        2: "高",
        3: "中",
        4: "低",
        5: "最低"
    }
    return priority_map.get(priority, str(priority))
