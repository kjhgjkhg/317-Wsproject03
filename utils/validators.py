"""
输入验证模块
提供日期、优先级、ID存在性等验证函数
"""
import re
from datetime import datetime
from typing import Optional, Tuple

from utils.config import PRIORITY_MIN, PRIORITY_MAX, DATE_FORMAT


def validate_priority(priority_str: str) -> Tuple[bool, Optional[int], str]:
    """
    验证优先级是否有效
    
    Args:
        priority_str: 优先级字符串
        
    Returns:
        (是否有效, 转换后的整数优先级, 错误信息)
    """
    try:
        priority = int(priority_str)
        if PRIORITY_MIN <= priority <= PRIORITY_MAX:
            return True, priority, ""
        return False, None, f"优先级必须在 {PRIORITY_MIN}-{PRIORITY_MAX} 之间"
    except ValueError:
        return False, None, "优先级必须是整数"


def validate_date(date_str: str) -> Tuple[bool, Optional[str], str]:
    """
    验证日期格式是否有效
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        (是否有效, 格式化后的日期字符串, 错误信息)
    """
    if not date_str or date_str.strip() == "":
        return True, "", ""
    
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, date_str):
        return False, None, f"日期格式必须为 {DATE_FORMAT}"
    
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True, date_str, ""
    except ValueError:
        return False, None, "无效的日期，请检查日期是否正确"


def validate_description(description: str) -> Tuple[bool, str]:
    """
    验证任务描述是否有效
    
    Args:
        description: 任务描述
        
    Returns:
        (是否有效, 错误信息)
    """
    if not description or description.strip() == "":
        return False, "任务描述不能为空"
    return True, ""


def validate_category(category: str) -> Tuple[bool, str]:
    """
    验证类别是否有效
    
    Args:
        category: 类别字符串
        
    Returns:
        (是否有效, 错误信息)
    """
    if not category or category.strip() == "":
        return True, ""
    return True, ""


def validate_id(id_str: str) -> Tuple[bool, Optional[int], str]:
    """
    验证任务ID是否为有效整数
    
    Args:
        id_str: ID字符串
        
    Returns:
        (是否有效, 转换后的整数ID, 错误信息)
    """
    try:
        task_id = int(id_str)
        if task_id > 0:
            return True, task_id, ""
        return False, None, "任务ID必须是正整数"
    except ValueError:
        return False, None, "任务ID必须是整数"
