"""
辅助函数模块
提供排序、过滤、Markdown格式化、表格打印等辅助函数
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from utils.config import DATE_FORMAT, DATETIME_FORMAT, EXPORT_FILENAME_PREFIX, EXPORT_FILENAME_SUFFIX


def sort_tasks_by_priority(tasks: List[Dict[str, Any]], descending: bool = False) -> List[Dict[str, Any]]:
    """
    按优先级排序任务
    
    Args:
        tasks: 任务列表
        descending: 是否降序排列（优先级低的在前，默认False表示优先级高的在前）
        
    Returns:
        排序后的任务列表
    """
    return sorted(tasks, key=lambda x: x.get("priority", 3), reverse=descending)


def sort_tasks_by_due_date(tasks: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
    """
    按截止日期排序任务
    
    Args:
        tasks: 任务列表
        ascending: 是否升序排列（日期近的在前）
        
    Returns:
        排序后的任务列表
    """
    def get_due_date(task: Dict[str, Any]) -> datetime:
        due_date = task.get("due_date", "")
        if due_date:
            try:
                return datetime.strptime(due_date, DATE_FORMAT)
            except ValueError:
                pass
        return datetime.max if ascending else datetime.min
    
    return sorted(tasks, key=get_due_date, reverse=not ascending)


def filter_tasks_by_category(tasks: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """
    按类别过滤任务
    
    Args:
        tasks: 任务列表
        category: 类别名称
        
    Returns:
        过滤后的任务列表
    """
    if not category:
        return tasks
    return [task for task in tasks if task.get("category", "") == category]


def filter_tasks_by_status(tasks: List[Dict[str, Any]], status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    按状态过滤任务
    
    Args:
        tasks: 任务列表
        status: 状态 (pending/completed)，None表示不过滤
        
    Returns:
        过滤后的任务列表
    """
    if status is None:
        return tasks
    return [task for task in tasks if task.get("status", "pending") == status]


def search_tasks(tasks: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """
    搜索任务（关键字模糊匹配描述或类别）
    
    Args:
        tasks: 任务列表
        keyword: 搜索关键字
        
    Returns:
        匹配的任务列表
    """
    if not keyword:
        return tasks
    
    keyword_lower = keyword.lower()
    results = []
    for task in tasks:
        description = task.get("description", "").lower()
        category = task.get("category", "").lower()
        if keyword_lower in description or keyword_lower in category:
            results.append(task)
    return results


def print_tasks_table(tasks: List[Dict[str, Any]]) -> None:
    """
    以表格形式打印任务列表
    
    Args:
        tasks: 任务列表
    """
    if not tasks:
        print("暂无任务")
        return
    
    headers = ["ID", "描述", "优先级", "截止日期", "类别", "状态", "创建时间"]
    col_widths = [5, 30, 8, 12, 10, 10, 20]
    
    header_line = "+" + "+".join("-" * w for w in col_widths) + "+"
    print(header_line)
    
    header_row = "|" + "|".join(h.center(w) for h, w in zip(headers, col_widths)) + "|"
    print(header_row)
    
    print(header_line)
    
    for task in tasks:
        row_data = [
            str(task.get("id", "")),
            truncate_text(task.get("description", ""), col_widths[1] - 2),
            str(task.get("priority", "")),
            task.get("due_date", "-") or "-",
            task.get("category", "-") or "-",
            "已完成" if task.get("status") == "completed" else "待办",
            task.get("created_at", "-")[:10] if task.get("created_at") else "-"
        ]
        row = "|" + "|".join(d.center(w) for d, w in zip(row_data, col_widths)) + "|"
        print(row)
    
    print(header_line)
    print(f"共 {len(tasks)} 条任务")


def truncate_text(text: str, max_length: int) -> str:
    """
    截断文本，超出部分显示省略号
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_markdown_report(tasks: List[Dict[str, Any]], title: str = "待办事项报告") -> str:
    """
    将任务列表格式化为Markdown报告
    
    Args:
        tasks: 任务列表
        title: 报告标题
        
    Returns:
        Markdown格式的报告字符串
    """
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime(DATETIME_FORMAT)}")
    lines.append(f"**任务总数**: {len(tasks)}")
    lines.append("")
    
    pending_tasks = [t for t in tasks if t.get("status") != "completed"]
    completed_tasks = [t for t in tasks if t.get("status") == "completed"]
    
    lines.append("## 待办任务")
    lines.append("")
    if pending_tasks:
        lines.append("| ID | 描述 | 优先级 | 截止日期 | 类别 |")
        lines.append("|----|------|--------|----------|------|")
        for task in pending_tasks:
            lines.append(f"| {task.get('id')} | {task.get('description')} | {task.get('priority')} | {task.get('due_date') or '-'} | {task.get('category') or '-'} |")
    else:
        lines.append("暂无待办任务")
    lines.append("")
    
    lines.append("## 已完成任务")
    lines.append("")
    if completed_tasks:
        lines.append("| ID | 描述 | 优先级 | 截止日期 | 类别 |")
        lines.append("|----|------|--------|----------|------|")
        for task in completed_tasks:
            lines.append(f"| {task.get('id')} | {task.get('description')} | {task.get('priority')} | {task.get('due_date') or '-'} | {task.get('category') or '-'} |")
    else:
        lines.append("暂无已完成任务")
    lines.append("")
    
    return "\n".join(lines)


def generate_export_filename() -> str:
    """
    生成导出文件名
    
    Returns:
        带时间戳的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{EXPORT_FILENAME_PREFIX}{timestamp}{EXPORT_FILENAME_SUFFIX}"
