"""
常量配置模块

定义文件路径、优先级范围、默认类别、日期格式等常量。
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "source_data")

OUTPUT_DIR = os.path.join(BASE_DIR, "output_build")

DATA_FILE = os.path.join(DATA_DIR, "todos.json")

PRIORITY_MIN = 1
PRIORITY_MAX = 5
PRIORITY_DEFAULT = 3

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_CATEGORY = "未分类"

VALID_CATEGORIES = ["工作", "学习", "生活", "健康", "其他", "未分类"]

TABLE_HEADERS = ["ID", "状态", "优先级", "描述", "截止日期", "类别"]
TABLE_COLUMN_WIDTHS = {
    "id": 5,
    "status": 8,
    "priority": 6,
    "description": 40,
    "due_date": 12,
    "category": 10
}
