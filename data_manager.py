"""
数据管理模块
负责 JSON 文件读写、任务增删改查核心逻辑
"""
import json
import os
from typing import List, Dict, Any, Optional, Tuple

from utils.config import DATA_FILE, SOURCE_DATA_DIR, OUTPUT_BUILD_DIR
from core_task import Task, create_task


class DataManager:
    """数据管理器，负责任务的持久化存储"""
    
    def __init__(self):
        """初始化数据管理器"""
        self.tasks: List[Task] = []
        self._next_id: int = 1
        self._ensure_directories()
        self._load_data()
    
    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        os.makedirs(SOURCE_DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUT_BUILD_DIR, exist_ok=True)
    
    def _load_data(self) -> None:
        """从JSON文件加载数据"""
        if not os.path.exists(DATA_FILE):
            self.tasks = []
            self._next_id = 1
            self._save_data()
            return
        
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.tasks = [Task.from_dict(item) for item in data.get("tasks", [])]
            self._next_id = data.get("next_id", 1)
            
            if not self._next_id or self._next_id < 1:
                self._next_id = max([t.id for t in self.tasks], default=0) + 1
                
        except json.JSONDecodeError:
            print(f"警告: 数据文件损坏，将创建新文件")
            self.tasks = []
            self._next_id = 1
            self._save_data()
        except PermissionError:
            print(f"错误: 无权限读取数据文件")
            self.tasks = []
            self._next_id = 1
        except Exception as e:
            print(f"警告: 加载数据时发生错误: {e}")
            self.tasks = []
            self._next_id = 1
    
    def _save_data(self) -> bool:
        """
        保存数据到JSON文件
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                "tasks": [task.to_dict() for task in self.tasks],
                "next_id": self._next_id,
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except PermissionError:
            print(f"错误: 无权限写入数据文件")
            return False
        except Exception as e:
            print(f"错误: 保存数据失败: {e}")
            return False
    
    def add_task(
        self,
        description: str,
        priority: int = 3,
        due_date: str = "",
        category: str = "",
    ) -> Tuple[bool, Optional[int], str]:
        """
        添加新任务
        
        Args:
            description: 任务描述
            priority: 优先级
            due_date: 截止日期
            category: 类别
            
        Returns:
            (是否成功, 任务ID, 错误信息)
        """
        success, task, error = create_task(
            task_id=self._next_id,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
        )
        
        if not success:
            return False, None, error
        
        self.tasks.append(task)
        self._next_id += 1
        self._save_data()
        
        return True, task.id, ""
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        根据ID获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task实例或None
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """
        获取所有任务
        
        Returns:
            任务列表
        """
        return self.tasks.copy()
    
    def get_tasks_as_dicts(self) -> List[Dict[str, Any]]:
        """
        获取所有任务的字典形式
        
        Returns:
            任务字典列表
        """
        return [task.to_dict() for task in self.tasks]
    
    def delete_task(self, task_id: int) -> Tuple[bool, str]:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (是否成功, 错误信息)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"任务ID {task_id} 不存在"
        
        self.tasks.remove(task)
        self._save_data()
        
        return True, ""
    
    def update_task(
        self,
        task_id: int,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            description: 新描述
            priority: 新优先级
            due_date: 新截止日期
            category: 新类别
            
        Returns:
            (是否成功, 错误信息)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"任务ID {task_id} 不存在"
        
        if description is not None:
            if not description.strip():
                return False, "任务描述不能为空"
            task.description = description.strip()
        
        if priority is not None:
            task.priority = priority
        
        if due_date is not None:
            task.due_date = due_date
        
        if category is not None:
            task.category = category if category.strip() else "未分类"
        
        self._save_data()
        
        return True, ""
    
    def mark_completed(self, task_id: int) -> Tuple[bool, str]:
        """
        标记任务为已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            (是否成功, 错误信息)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"任务ID {task_id} 不存在"
        
        task.mark_completed()
        self._save_data()
        
        return True, ""
    
    def mark_pending(self, task_id: int) -> Tuple[bool, str]:
        """
        标记任务为待办
        
        Args:
            task_id: 任务ID
            
        Returns:
            (是否成功, 错误信息)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False, f"任务ID {task_id} 不存在"
        
        task.mark_pending()
        self._save_data()
        
        return True, ""
    
    def task_exists(self, task_id: int) -> bool:
        """
        检查任务是否存在
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否存在
        """
        return self.get_task_by_id(task_id) is not None
