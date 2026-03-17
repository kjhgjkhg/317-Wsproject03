"""
JSON 文件读写、任务增删改查核心逻辑模块

负责数据持久化与任务管理核心操作。
"""
import json
import os
from typing import List, Optional, Dict, Any
from core_task import Task
from utils.config import DATA_DIR, OUTPUT_DIR


class DataManager:
    """数据管理器 - 负责JSON文件读写与任务管理"""
    
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.tasks: List[Task] = []
        self._next_id: int = 1
        self._ensure_data_dir()
        self._load_data()
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def _load_data(self) -> None:
        """从JSON文件加载数据"""
        if not os.path.exists(self.file_path):
            self.tasks = []
            self._next_id = 1
            self._save_data()
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                self._next_id = data.get("next_id", 1)
            elif isinstance(data, list):
                self.tasks = [Task.from_dict(t) for t in data]
                self._next_id = max([t.id for t in self.tasks], default=0) + 1
            else:
                self.tasks = []
                self._next_id = 1
                
        except json.JSONDecodeError:
            print("警告: 数据文件损坏，将创建新文件")
            self.tasks = []
            self._next_id = 1
        except Exception as e:
            print(f"警告: 加载数据失败 - {e}")
            self.tasks = []
            self._next_id = 1
    
    def _save_data(self) -> None:
        """保存数据到JSON文件"""
        data = {
            "tasks": [t.to_dict() for t in self.tasks],
            "next_id": self._next_id
        }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_task(
        self,
        description: str,
        priority: int = 3,
        due_date: Optional[str] = None,
        category: str = "未分类"
    ) -> Task:
        """添加新任务"""
        task = Task(
            task_id=self._next_id,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category
        )
        self.tasks.append(task)
        self._next_id += 1
        self._save_data()
        return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return self.tasks.copy()
    
    def get_incomplete_tasks(self) -> List[Task]:
        """获取未完成的任务"""
        return [t for t in self.tasks if not t.completed]
    
    def get_completed_tasks(self) -> List[Task]:
        """获取已完成的任务"""
        return [t for t in self.tasks if t.completed]
    
    def mark_completed(self, task_id: int) -> bool:
        """标记任务为已完成"""
        task = self.get_task_by_id(task_id)
        if task:
            task.completed = True
            self._save_data()
            return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self._save_data()
                return True
        return False
    
    def update_task(
        self,
        task_id: int,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[str] = None,
        category: Optional[str] = None
    ) -> bool:
        """更新任务字段"""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date if due_date else None
        if category is not None:
            task.category = category
        
        self._save_data()
        return True
    
    def search_tasks(self, keyword: str) -> List[Task]:
        """搜索任务（模糊匹配描述或类别）"""
        keyword_lower = keyword.lower()
        results = []
        for task in self.tasks:
            if (keyword_lower in task.description.lower() or
                keyword_lower in task.category.lower()):
                results.append(task)
        return results
    
    def filter_by_category(self, category: str) -> List[Task]:
        """按类别过滤任务"""
        return [t for t in self.tasks if t.category == category]
    
    def sort_by_priority(self, tasks: List[Task], descending: bool = False) -> List[Task]:
        """按优先级排序（优先级1最高，默认升序排列）"""
        return sorted(tasks, key=lambda t: t.priority, reverse=descending)
    
    def sort_by_due_date(self, tasks: List[Task]) -> List[Task]:
        """按截止日期排序（无截止日期的排在最后）"""
        def get_due_key(task: Task) -> str:
            return task.due_date if task.due_date else "9999-99-99"
        return sorted(tasks, key=get_due_key)
    
    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        categories = set()
        for task in self.tasks:
            categories.add(task.category)
        return sorted(list(categories))
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        total = len(self.tasks)
        completed = len(self.get_completed_tasks())
        incomplete = total - completed
        overdue = len([t for t in self.tasks if t.is_overdue()])
        
        return {
            "total": total,
            "completed": completed,
            "incomplete": incomplete,
            "overdue": overdue
        }
