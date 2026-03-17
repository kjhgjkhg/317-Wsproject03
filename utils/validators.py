"""
utils/validators.py - 输入验证函数模块
提供日期、优先级、ID存在性等验证功能
"""
import re
from datetime import datetime
from typing import Optional, Tuple

from utils.config import (
    PRIORITY_MIN,
    PRIORITY_MAX,
    DATE_FORMAT,
    CATEGORY_DEFAULT,
    VALID_CATEGORIES
)


def validate_priority(priority: str) -> Tuple[bool, Optional[int], str]:
    """
    验证优先级输入
    
    Args:
        priority: 优先级字符串
        
    Returns:
        (是否有效, 转换后的整数, 错误信息)
    """
    try:
        priority_int = int(priority)
        if PRIORITY_MIN <= priority_int <= PRIORITY_MAX:
            return True, priority_int, ""
        return False, None, f"优先级必须在 {PRIORITY_MIN}-{PRIORITY_MAX} 之间"
    except ValueError:
        return False, None, "优先级必须是整数"


def validate_date(date_str: str) -> Tuple[bool, Optional[str], str]:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        (是否有效, 格式化后的日期字符串, 错误信息)
    """
    if not date_str or date_str.strip() == "":
        return True, "", ""
    
    date_str = date_str.strip()
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    
    if not date_pattern.match(date_str):
        return False, None, f"日期格式必须为 {DATE_FORMAT}"
    
    try:
        parsed_date = datetime.strptime(date_str, DATE_FORMAT)
        if parsed_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            return True, date_str, "警告: 截止日期已过期"
        return True, date_str, ""
    except ValueError:
        return False, None, "无效的日期值"


def validate_description(description: str) -> Tuple[bool, str]:
    """
    验证任务描述
    
    Args:
        description: 任务描述
        
    Returns:
        (是否有效, 错误信息)
    """
    if not description or description.strip() == "":
        return False, "任务描述不能为空"
    return True, ""


def validate_category(category: str) -> Tuple[bool, str, str]:
    """
    验证任务类别
    
    Args:
        category: 任务类别
        
    Returns:
        (是否有效, 处理后的类别, 错误信息)
    """
    if not category or category.strip() == "":
        return True, CATEGORY_DEFAULT, ""
    
    category = category.strip()
    if category in VALID_CATEGORIES:
        return True, category, ""
    
    return True, category, f"注意: 类别 '{category}' 不在预设类别中，已保留"


def validate_task_id(task_id: str, existing_ids: list) -> Tuple[bool, Optional[int], str]:
    """
    验证任务ID
    
    Args:
        task_id: 任务ID字符串
        existing_ids: 已存在的ID列表
        
    Returns:
        (是否有效, 转换后的整数ID, 错误信息)
    """
    try:
        task_id_int = int(task_id)
        if task_id_int in existing_ids:
            return True, task_id_int, ""
        return False, None, f"任务ID {task_id_int} 不存在"
    except ValueError:
        return False, None, "任务ID必须是整数"


def validate_sort_field(field: str) -> Tuple[bool, str]:
    """
    验证排序字段
    
    Args:
        field: 排序字段名
        
    Returns:
        (是否有效, 错误信息)
    """
    valid_fields = ("priority", "deadline", "category", "id", "status")
    if field.lower() in valid_fields:
        return True, ""
    return False, f"排序字段必须是: {', '.join(valid_fields)}"
