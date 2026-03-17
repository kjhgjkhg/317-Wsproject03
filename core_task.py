"""
Task 数据类模块
定义 Task 类，包含业务规则、校验和序列化方法
"""
from datetime import datetime
from typing import Dict, Any, Optional

from utils.config import (
    DEFAULT_CATEGORY,
    STATUS_PENDING,
    STATUS_COMPLETED,
    DATETIME_FORMAT,
    DATE_FORMAT,
    PRIORITY_MIN,
    PRIORITY_MAX,
)
from utils.validators import (
    validate_priority,
    validate_date,
    validate_description,
    validate_category,
)


class Task:
    """任务数据类"""
    
    def __init__(
        self,
        task_id: int,
        description: str,
        priority: int = 3,
        due_date: str = "",
        category: str = DEFAULT_CATEGORY,
        status: str = STATUS_PENDING,
        created_at: Optional[str] = None,
    ):
        """
        初始化任务
        
        Args:
            task_id: 任务ID
            description: 任务描述
            priority: 优先级 (1-5)
            due_date: 截止日期 (YYYY-MM-DD)
            category: 类别
            status: 状态
            created_at: 创建时间
        """
        self.id = task_id
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.status = status
        self.created_at = created_at or datetime.now().strftime(DATETIME_FORMAT)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将任务转换为字典
        
        Returns:
            任务字典
        """
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        从字典创建任务实例
        
        Args:
            data: 任务字典
            
        Returns:
            Task实例
        """
        return cls(
            task_id=data.get("id", 0),
            description=data.get("description", ""),
            priority=data.get("priority", 3),
            due_date=data.get("due_date", ""),
            category=data.get("category", DEFAULT_CATEGORY),
            status=data.get("status", STATUS_PENDING),
            created_at=data.get("created_at"),
        )
    
    def update(
        self,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[str] = None,
        category: Optional[str] = None,
    ) -> None:
        """
        更新任务字段
        
        Args:
            description: 新描述
            priority: 新优先级
            due_date: 新截止日期
            category: 新类别
        """
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if due_date is not None:
            self.due_date = due_date
        if category is not None:
            self.category = category
    
    def mark_completed(self) -> None:
        """标记任务为已完成"""
        self.status = STATUS_COMPLETED
    
    def mark_pending(self) -> None:
        """标记任务为待办"""
        self.status = STATUS_PENDING
    
    def is_completed(self) -> bool:
        """检查任务是否已完成"""
        return self.status == STATUS_COMPLETED
    
    def __repr__(self) -> str:
        return f"Task(id={self.id}, description='{self.description}', priority={self.priority})"


def create_task(
    task_id: int,
    description: str,
    priority: int = 3,
    due_date: str = "",
    category: str = DEFAULT_CATEGORY,
) -> tuple[bool, Optional[Task], str]:
    """
    创建新任务（带验证）
    
    Args:
        task_id: 任务ID
        description: 任务描述
        priority: 优先级
        due_date: 截止日期
        category: 类别
        
    Returns:
        (是否成功, Task实例, 错误信息)
    """
    valid, error = validate_description(description)
    if not valid:
        return False, None, error
    
    valid, priority_val, error = validate_priority(str(priority))
    if not valid:
        return False, None, error
    
    valid, due_date_val, error = validate_date(due_date)
    if not valid:
        return False, None, error
    
    valid, error = validate_category(category)
    if not valid:
        return False, None, error
    
    task = Task(
        task_id=task_id,
        description=description.strip(),
        priority=priority_val,
        due_date=due_date_val,
        category=category.strip() if category.strip() else DEFAULT_CATEGORY,
    )
    
    return True, task, ""
