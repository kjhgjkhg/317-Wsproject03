"""
配置常量模块
定义文件路径、优先级范围、默认类别、日期格式等常量
"""
import os
from typing import Final

BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DATA_DIR: Final[str] = os.path.join(BASE_DIR, "source_data")
OUTPUT_BUILD_DIR: Final[str] = os.path.join(BASE_DIR, "output_build")

DATA_FILE: Final[str] = os.path.join(SOURCE_DATA_DIR, "todos.json")
CONFIG_FILE: Final[str] = os.path.join(SOURCE_DATA_DIR, ".do_not_touch.cfg")

PRIORITY_MIN: Final[int] = 1
PRIORITY_MAX: Final[int] = 5
PRIORITY_RANGE: Final[range] = range(PRIORITY_MIN, PRIORITY_MAX + 1)

DEFAULT_CATEGORY: Final[str] = "未分类"
VALID_CATEGORIES: Final[list] = ["工作", "学习", "生活", "其他", "未分类"]

DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

STATUS_PENDING: Final[str] = "pending"
STATUS_COMPLETED: Final[str] = "completed"

EXPORT_FILENAME_PREFIX: Final[str] = "todo_report_"
EXPORT_FILENAME_SUFFIX: Final[str] = ".md"
