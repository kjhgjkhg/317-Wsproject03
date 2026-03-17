"""
输入验证函数模块

提供日期、优先级、ID存在性等验证函数。
"""
import re
from datetime import datetime
from typing import Optional
from utils.config import PRIORITY_MIN, PRIORITY_MAX, DATE_FORMAT


def validate_priority(priority: int) -> int:
    """
    验证优先级是否在有效范围内
    
    Args:
        priority: 待验证的优先级值
        
    Returns:
        验证通过的优先级值
        
    Raises:
        ValueError: 优先级不在有效范围内
    """
    if not isinstance(priority, int):
        raise ValueError(f"优先级必须是整数")
    
    if priority < PRIORITY_MIN or priority > PRIORITY_MAX:
        raise ValueError(f"优先级必须在 {PRIORITY_MIN}-{PRIORITY_MAX} 之间")
    
    return priority


def validate_date(date_str: Optional[str]) -> str:
    """
    验证日期格式是否正确
    
    Args:
        date_str: 待验证的日期字符串 (YYYY-MM-DD)
        
    Returns:
        验证通过的日期字符串
        
    Raises:
        ValueError: 日期格式不正确或无效
    """
    if not date_str:
        raise ValueError("日期不能为空")
    
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, date_str):
        raise ValueError(f"日期格式必须为 {DATE_FORMAT}")
    
    try:
        datetime.strptime(date_str, DATE_FORMAT)
    except ValueError:
        raise ValueError(f"无效的日期: {date_str}")
    
    return date_str


def validate_description(description: str) -> str:
    """
    验证任务描述是否有效
    
    Args:
        description: 待验证的任务描述
        
    Returns:
        验证通过的任务描述（去除首尾空格）
        
    Raises:
        ValueError: 描述为空或仅包含空白字符
    """
    if not description:
        raise ValueError("任务描述不能为空")
    
    cleaned = description.strip()
    if not cleaned:
        raise ValueError("任务描述不能为空或仅包含空白字符")
    
    return cleaned


def validate_task_id(task_id: int, manager) -> int:
    """
    验证任务ID是否存在
    
    Args:
        task_id: 待验证的任务ID
        manager: 数据管理器实例
        
    Returns:
        验证通过的任务ID
        
    Raises:
        ValueError: 任务ID不存在
    """
    if not isinstance(task_id, int):
        raise ValueError("任务ID必须是整数")
    
    if task_id <= 0:
        raise ValueError("任务ID必须为正整数")
    
    task = manager.get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"任务ID #{task_id} 不存在")
    
    return task_id


def validate_category(category: Optional[str]) -> str:
    """
    验证并返回类别名称
    
    Args:
        category: 类别名称
        
    Returns:
        验证通过的类别名称
    """
    if not category or not category.strip():
        return "未分类"
    
    return category.strip()
