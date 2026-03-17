"""
core_task.py - Task 数据类与业务规则模块
定义Task数据类、校验逻辑、序列化方法等
"""
from datetime import datetime
from typing import Dict, Any, Optional, List

from utils.config import (
    PRIORITY_DEFAULT,
    CATEGORY_DEFAULT,
    DATE_FORMAT,
    STATUS_PENDING,
    STATUS_COMPLETED
)
from utils.validators import (
    validate_priority,
    validate_date,
    validate_description,
    validate_category
)


class Task:
    """
    任务数据类
    
    属性:
        id: 唯一标识符
        description: 任务描述
        priority: 优先级 (1-5)
        deadline: 截止日期 (YYYY-MM-DD)
        category: 任务类别
        status: 任务状态
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    def __init__(
        self,
        task_id: int,
        description: str,
        priority: int = PRIORITY_DEFAULT,
        deadline: str = "",
        category: str = CATEGORY_DEFAULT,
        status: str = STATUS_PENDING,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.id = task_id
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.category = category
        self.status = status
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = updated_at or self.created_at
    
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
            "deadline": self.deadline,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        从字典创建任务实例
        
        Args:
            data: 任务数据字典
            
        Returns:
            Task实例
        """
        return cls(
            task_id=data.get("id", 0),
            description=data.get("description", ""),
            priority=data.get("priority", PRIORITY_DEFAULT),
            deadline=data.get("deadline", ""),
            category=data.get("category", CATEGORY_DEFAULT),
            status=data.get("status", STATUS_PENDING),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def update(
        self,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        deadline: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> None:
        """
        更新任务属性
        
        Args:
            description: 新描述
            priority: 新优先级
            deadline: 新截止日期
            category: 新类别
            status: 新状态
        """
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if deadline is not None:
            self.deadline = deadline
        if category is not None:
            self.category = category
        if status is not None:
            self.status = status
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def mark_completed(self) -> None:
        """标记任务为已完成"""
        self.status = STATUS_COMPLETED
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self.id}, description='{self.description}', "
            f"priority={self.priority}, status='{self.status}')"
        )


class TaskValidator:
    """
    任务验证器类
    提供任务创建和更新的验证逻辑
    """
    
    @staticmethod
    def validate_create(
        description: str,
        priority: str,
        deadline: str,
        category: str
    ) -> Dict[str, Any]:
        """
        验证创建任务的输入
        
        Args:
            description: 任务描述
            priority: 优先级字符串
            deadline: 截止日期字符串
            category: 类别
            
        Returns:
            验证结果字典，包含:
            - valid: 是否有效
            - data: 验证后的数据
            - errors: 错误列表
            - warnings: 警告列表
        """
        errors: List[str] = []
        warnings: List[str] = []
        data: Dict[str, Any] = {}
        
        valid_desc, desc_error = validate_description(description)
        if not valid_desc:
            errors.append(desc_error)
        else:
            data["description"] = description.strip()
        
        valid_pri, priority_int, pri_error = validate_priority(priority)
        if not valid_pri:
            errors.append(pri_error)
        else:
            data["priority"] = priority_int
        
        valid_date, date_str, date_msg = validate_date(deadline)
        if not valid_date:
            errors.append(date_msg)
        else:
            data["deadline"] = date_str
            if date_msg:
                warnings.append(date_msg)
        
        valid_cat, category_str, cat_msg = validate_category(category)
        data["category"] = category_str
        if cat_msg:
            warnings.append(cat_msg)
        
        return {
            "valid": len(errors) == 0,
            "data": data,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_update(
        description: Optional[str] = None,
        priority: Optional[str] = None,
        deadline: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        验证更新任务的输入
        
        Args:
            description: 任务描述
            priority: 优先级字符串
            deadline: 截止日期字符串
            category: 类别
            
        Returns:
            验证结果字典
        """
        errors: List[str] = []
        warnings: List[str] = []
        data: Dict[str, Any] = {}
        
        if description is not None:
            valid_desc, desc_error = validate_description(description)
            if not valid_desc:
                errors.append(desc_error)
            else:
                data["description"] = description.strip()
        
        if priority is not None:
            valid_pri, priority_int, pri_error = validate_priority(priority)
            if not valid_pri:
                errors.append(pri_error)
            else:
                data["priority"] = priority_int
        
        if deadline is not None:
            valid_date, date_str, date_msg = validate_date(deadline)
            if not valid_date:
                errors.append(date_msg)
            else:
                data["deadline"] = date_str
                if date_msg:
                    warnings.append(date_msg)
        
        if category is not None:
            valid_cat, category_str, cat_msg = validate_category(category)
            data["category"] = category_str
            if cat_msg:
                warnings.append(cat_msg)
        
        return {
            "valid": len(errors) == 0,
            "data": data,
            "errors": errors,
            "warnings": warnings
        }
