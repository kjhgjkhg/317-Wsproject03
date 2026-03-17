"""
data_manager.py - 数据管理模块
负责JSON文件读写、任务增删改查核心逻辑
"""
import json
import os
from typing import List, Dict, Any, Optional

from utils.config import (
    DATA_FILE,
    SOURCE_DATA_DIR,
    STATUS_PENDING,
    STATUS_COMPLETED
)
from core_task import Task


class DataManager:
    """
    数据管理器类
    负责任务的持久化存储和检索
    """
    
    def __init__(self, data_file: str = DATA_FILE):
        """
        初始化数据管理器
        
        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file
        self.tasks: List[Task] = []
        self._next_id: int = 1
        self._ensure_data_dir()
        self.load()
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        if not os.path.exists(SOURCE_DATA_DIR):
            os.makedirs(SOURCE_DATA_DIR)
    
    def _ensure_data_file(self) -> None:
        """确保数据文件存在"""
        if not os.path.exists(self.data_file):
            self._save_to_file([])
    
    def load(self) -> None:
        """从文件加载任务数据"""
        self._ensure_data_file()
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict) and "tasks" in data:
                task_list = data["tasks"]
                self._next_id = data.get("next_id", 1)
            elif isinstance(data, list):
                task_list = data
                self._next_id = max([t.get("id", 0) for t in task_list], default=0) + 1
            else:
                task_list = []
                self._next_id = 1
            
            self.tasks = [Task.from_dict(t) for t in task_list]
            
        except json.JSONDecodeError:
            self.tasks = []
            self._next_id = 1
            print("警告: 数据文件损坏，已重置为空")
        except PermissionError:
            print("错误: 无权限读取数据文件")
            raise
        except Exception as e:
            self.tasks = []
            self._next_id = 1
            print(f"警告: 加载数据时发生错误: {e}")
    
    def _save_to_file(self, tasks_data: List[Dict[str, Any]]) -> None:
        """
        保存任务数据到文件
        
        Args:
            tasks_data: 任务数据列表
        """
        data = {
            "tasks": tasks_data,
            "next_id": self._next_id
        }
        
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except PermissionError:
            print("错误: 无权限写入数据文件")
            raise
        except Exception as e:
            print(f"错误: 保存数据时发生错误: {e}")
            raise
    
    def save(self) -> None:
        """保存当前任务列表到文件"""
        tasks_data = [task.to_dict() for task in self.tasks]
        self._save_to_file(tasks_data)
    
    def get_next_id(self) -> int:
        """
        获取下一个可用ID
        
        Returns:
            新的任务ID
        """
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    def add_task(self, task: Task) -> Task:
        """
        添加新任务
        
        Args:
            task: 任务对象
            
        Returns:
            添加的任务对象
        """
        self.tasks.append(task)
        self.save()
        return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        根据ID获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象或None
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
    
    def get_task_ids(self) -> List[int]:
        """
        获取所有任务ID
        
        Returns:
            ID列表
        """
        return [task.id for task in self.tasks]
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的任务对象或None
        """
        task = self.get_task_by_id(task_id)
        if task:
            task.update(**kwargs)
            self.save()
            return task
        return None
    
    def delete_task(self, task_id: int) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否删除成功
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.save()
                return True
        return False
    
    def mark_completed(self, task_id: int) -> Optional[Task]:
        """
        标记任务为已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            更新后的任务对象或None
        """
        task = self.get_task_by_id(task_id)
        if task:
            task.mark_completed()
            self.save()
            return task
        return None
    
    def search_tasks(self, keyword: str) -> List[Task]:
        """
        搜索任务
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            匹配的任务列表
        """
        if not keyword:
            return self.tasks.copy()
        
        keyword = keyword.lower()
        return [
            task for task in self.tasks
            if keyword in task.description.lower()
            or keyword in task.category.lower()
        ]
    
    def filter_by_category(self, category: str) -> List[Task]:
        """
        按类别过滤任务
        
        Args:
            category: 类别
            
        Returns:
            过滤后的任务列表
        """
        if not category:
            return self.tasks.copy()
        return [task for task in self.tasks if task.category == category]
    
    def filter_by_status(self, status: str) -> List[Task]:
        """
        按状态过滤任务
        
        Args:
            status: 状态
            
        Returns:
            过滤后的任务列表
        """
        return [task for task in self.tasks if task.status == status]
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取任务统计信息
        
        Returns:
            统计信息字典
        """
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t.status == STATUS_PENDING])
        completed = len([t for t in self.tasks if t.status == STATUS_COMPLETED])
        
        return {
            "total": total,
            "pending": pending,
            "completed": completed
        }
