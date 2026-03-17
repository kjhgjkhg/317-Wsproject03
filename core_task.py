"""
Task 数据类 + 业务规则模块

定义 Task 数据类，包含校验、序列化等业务规则。
"""
from datetime import datetime
from typing import Optional, Dict, Any


class Task:
    """任务数据类"""
    
    def __init__(
        self,
        task_id: int,
        description: str,
        priority: int = 3,
        due_date: Optional[str] = None,
        category: str = "未分类",
        completed: bool = False,
        created_at: Optional[str] = None
    ) -> None:
        self.id = task_id
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """将任务序列化为字典"""
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "category": self.category,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务实例"""
        return cls(
            task_id=data.get("id", 0),
            description=data.get("description", ""),
            priority=data.get("priority", 3),
            due_date=data.get("due_date"),
            category=data.get("category", "未分类"),
            completed=data.get("completed", False),
            created_at=data.get("created_at")
        )
    
    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        due = f" (截止: {self.due_date})" if self.due_date else ""
        return f"[{status}] #{self.id} (P{self.priority}) {self.description}{due}"
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        return "已完成" if self.completed else "未完成"
    
    def is_overdue(self) -> bool:
        """检查是否已过期"""
        if self.completed or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            return datetime.now().date() > due.date()
        except ValueError:
            return False
