"""
config.py

此文件用于存储整个项目中的全局配置变量，例如文件路径、默认设置等。
使用常量可以方便地在一处修改配置，并在整个项目中保持一致性。
"""
import os

# --- 路径配置 ---
# 项目根目录 (相对于 config.py 的位置)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 如果 main.py 在根目录下

# 数据存储根目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
# 用户数据存储目录
USERS_DIR = os.path.join(DATA_DIR, 'users')
# 共享数据存储目录
SHARED_DIR = os.path.join(DATA_DIR, 'shared')
# 资源文件目录
RESOURCES_DIR = os.path.join(PROJECT_ROOT, 'resources')

# --- 登录/注册配置 ---
# 密码最小长度
MIN_PASSWORD_LENGTH = 8
# 密码必须包含大写字母
PASSWORD_REQUIRE_UPPERCASE = True
# 密码必须包含小写字母
PASSWORD_REQUIRE_LOWERCASE = True
# 密码必须包含数字
PASSWORD_REQUIRE_DIGIT = True
# 密码必须包含特殊字符
PASSWORD_REQUIRE_SPECIAL = True

# --- 农田配置 ---
# 默认农田网格大小 (行数, 列数)
DEFAULT_FIELD_SIZE = (10, 10)
# 默认网格单元格像素大小
GRID_CELL_SIZE_PX = 40

# --- 无人机配置 ---
# 默认飞行速度 (单位/秒)
DEFAULT_DRONE_SPEED = 5
# 默认喷洒宽度 (覆盖的网格单元格数量)
DEFAULT_SPRAY_WIDTH = 1

# --- 模拟配置 ---
# 模拟时间步长 (秒)
SIMULATION_TIMESTEP = 0.1
# 动画帧率 (FPS)
ANIMATION_FPS = 30

# --- UI/图形配置 ---
# 主窗口标题
WINDOW_TITLE = "农田无人机喷洒模拟系统"
# 主窗口默认宽度
WINDOW_WIDTH = 1200
# 主窗口默认高度
WINDOW_HEIGHT = 800
# 默认背景颜色 (RGB)
DEFAULT_BG_COLOR = (240, 240, 240)
# 默认网格线颜色 (RGB)
DEFAULT_GRID_COLOR = (200, 200, 200)

# --- 日志配置 ---
# 日志文件路径
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, 'app.log')
# 日志级别 (例如: 'DEBUG', 'INFO', 'WARNING', 'ERROR')
LOG_LEVEL = 'INFO'

# --- 文件扩展名 ---
JSON_EXT = '.json'