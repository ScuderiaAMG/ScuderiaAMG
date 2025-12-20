"""
utils/file_handler.py

负责处理与文件读写相关的操作，如用户信息、农田数据、无人机数据等的持久化存储。
"""
import json
import os
from config import USERS_DIR, SHARED_DIR
from models.user import User
from models.field import Field
from models.drone import Drone
from models.pesticide import Pesticide
from utils.logger import logger

def ensure_directory_exists(path):
    """确保指定的目录存在，如果不存在则创建。"""
    os.makedirs(path, exist_ok=True)

def save_user_data(user: User):
    """
    保存用户数据到其专属文件夹。
    Args:
        user (User): 用户对象。
    """
    user_dir = os.path.join(USERS_DIR, user.username)
    ensure_directory_exists(user_dir)
    
    profile_path = os.path.join(user_dir, "profile.json")
    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            # User 对象需要能被序列化，例如实现 to_dict 方法
            json.dump(user.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info(f"用户 {user.username} 的 profile 数据已保存到 {profile_path}")
    except Exception as e:
        logger.error(f"保存用户 {user.username} profile 数据失败: {e}")

def load_user_data(username: str) -> User:
    """
    从文件加载用户数据。
    Args:
        username (str): 用户名。
    Returns:
        User: 加载的用户对象，如果失败则返回 None。
    """
    profile_path = os.path.join(USERS_DIR, username, "profile.json")
    if not os.path.exists(profile_path):
        logger.warning(f"用户 {username} 的 profile 文件不存在: {profile_path}")
        return None

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        # User 类需要能从字典重建，例如实现 from_dict 类方法
        user = User.from_dict(user_data)
        logger.info(f"用户 {username} 的 profile 数据已加载")
        return user
    except Exception as e:
        logger.error(f"加载用户 {username} profile 数据失败: {e}")
        return None

def save_field_data(username: str, field_name: str, field: Field):
    """
    保存特定用户的农田数据。
    Args:
        username (str): 用户名。
        field_name (str): 农田名称。
        field (Field): 农田对象。
    """
    user_dir = os.path.join(USERS_DIR, username)
    field_dir = os.path.join(user_dir, "fields")
    ensure_directory_exists(field_dir)
    
    field_path = os.path.join(field_dir, f"{field_name}.json")
    try:
        with open(field_path, 'w', encoding='utf-8') as f:
            json.dump(field.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info(f"农田 {field_name} 的数据已保存到 {user_dir} 的 fields 文件夹")
    except Exception as e:
        logger.error(f"保存农田 {field_name} 数据失败: {e}")

def load_field_data(username: str, field_name: str) -> Field:
    """
    加载特定用户的农田数据。
    Args:
        username (str): 用户名。
        field_name (str): 农田名称。
    Returns:
        Field: 加载的农田对象，如果失败则返回 None。
    """
    field_path = os.path.join(USERS_DIR, username, "fields", f"{field_name}.json")
    if not os.path.exists(field_path):
        logger.warning(f"农田 {field_name} 的文件不存在: {field_path}")
        return None

    try:
        with open(field_path, 'r', encoding='utf-8') as f:
            field_data = json.load(f)
        field = Field.from_dict(field_data)
        logger.info(f"农田 {field_name} 的数据已加载")
        return field
    except Exception as e:
        logger.error(f"加载农田 {field_name} 数据失败: {e}")
        return None

def list_user_fields(username: str) -> list:
    """
    列出特定用户的所有农田文件名。
    Args:
        username (str): 用户名。
    Returns:
        list: 农田名称列表。
    """
    field_dir = os.path.join(USERS_DIR, username, "fields")
    ensure_directory_exists(field_dir) # 确保目录存在
    try:
        files = os.listdir(field_dir)
        # 过滤出 .json 文件并移除扩展名
        field_names = [f[:-5] for f in files if f.endswith('.json')]
        logger.info(f"列出用户 {username} 的农田: {field_names}")
        return field_names
    except Exception as e:
        logger.error(f"列出用户 {username} 农田失败: {e}")
        return []

def save_drone_data(username: str, drone_name: str, drone: Drone):
    """
    保存特定用户的无人机数据。
    Args:
        username (str): 用户名。
        drone_name (str): 无人机名称。
        drone (Drone): 无人机对象。
    """
    user_dir = os.path.join(USERS_DIR, username)
    drone_dir = os.path.join(user_dir, "drones")
    ensure_directory_exists(drone_dir)
    
    drone_path = os.path.join(drone_dir, f"{drone_name}.json")
    try:
        with open(drone_path, 'w', encoding='utf-8') as f:
            json.dump(drone.to_dict(), f, ensure_ascii=False, indent=4)
        logger.info(f"无人机 {drone_name} 的数据已保存到 {user_dir} 的 drones 文件夹")
    except Exception as e:
        logger.error(f"保存无人机 {drone_name} 数据失败: {e}")

def load_drone_data(username: str, drone_name: str) -> Drone:
    """
    加载特定用户的无人机数据。
    Args:
        username (str): 用户名。
        drone_name (str): 无人机名称。
    Returns:
        Drone: 加载的无人机对象，如果失败则返回 None。
    """
    drone_path = os.path.join(USERS_DIR, username, "drones", f"{drone_name}.json")
    if not os.path.exists(drone_path):
        logger.warning(f"无人机 {drone_name} 的文件不存在: {drone_path}")
        return None

    try:
        with open(drone_path, 'r', encoding='utf-8') as f:
            drone_data = json.load(f)
        drone = Drone.from_dict(drone_data)
        logger.info(f"无人机 {drone_name} 的数据已加载")
        return drone
    except Exception as e:
        logger.error(f"加载无人机 {drone_name} 数据失败: {e}")
        return None

def list_user_drones(username: str) -> list:
    """
    列出特定用户的所有无人机文件名。
    Args:
        username (str): 用户名。
    Returns:
        list: 无人机名称列表。
    """
    drone_dir = os.path.join(USERS_DIR, username, "drones")
    ensure_directory_exists(drone_dir)
    try:
        files = os.listdir(drone_dir)
        drone_names = [f[:-5] for f in files if f.endswith('.json')]
        logger.info(f"列出用户 {username} 的无人机: {drone_names}")
        return drone_names
    except Exception as e:
        logger.error(f"列出用户 {username} 无人机失败: {e}")
        return []

def save_pesticide_data(username: str, pesticide_list: list):
    """
    保存特定用户的农药列表数据。
    Args:
        username (str): 用户名。
        pesticide_list (list): 农药对象列表。
    """
    user_dir = os.path.join(USERS_DIR, username)
    pesticide_dir = os.path.join(user_dir, "pesticides")
    ensure_directory_exists(pesticide_dir)
    
    pesticide_path = os.path.join(pesticide_dir, "pesticides.json")
    try:
        # 假设农药对象有 to_dict 方法
        pesticide_dicts = [p.to_dict() for p in pesticide_list]
        with open(pesticide_path, 'w', encoding='utf-8') as f:
            json.dump(pesticide_dicts, f, ensure_ascii=False, indent=4)
        logger.info(f"用户 {username} 的农药数据已保存到 {user_dir} 的 pesticides 文件夹")
    except Exception as e:
        logger.error(f"保存用户 {username} 农药数据失败: {e}")

def load_pesticide_data(username: str) -> list:
    """
    加载特定用户的农药列表数据。
    Args:
        username (str): 用户名。
    Returns:
        list: 农药对象列表，如果失败则返回空列表。
    """
    pesticide_path = os.path.join(USERS_DIR, username, "pesticides", "pesticides.json")
    if not os.path.exists(pesticide_path):
        logger.warning(f"用户 {username} 的农药文件不存在: {pesticide_path}")
        # 如果文件不存在，返回一个空列表，表示用户尚未配置农药
        return []

    try:
        with open(pesticide_path, 'r', encoding='utf-8') as f:
            pesticide_data_list = json.load(f)
        # 假设农药类有 from_dict 类方法
        pesticide_list = [Pesticide.from_dict(data) for data in pesticide_data_list]
        logger.info(f"用户 {username} 的农药数据已加载")
        return pesticide_list
    except Exception as e:
        logger.error(f"加载用户 {username} 农药数据失败: {e}")
        return []

# --- 示例：加载共享默认无人机数据 ---
def load_default_drones():
    """加载系统提供的默认无人机配置（如果存在）。"""
    default_drone_path = os.path.join(SHARED_DIR, "default_drones.json")
    if not os.path.exists(default_drone_path):
        logger.info("未找到共享默认无人机配置文件。")
        return []
    try:
        with open(default_drone_path, 'r', encoding='utf-8') as f:
            default_data_list = json.load(f)
        default_drones = [Drone.from_dict(data) for data in default_data_list]
        logger.info(f"加载了 {len(default_drones)} 个默认无人机配置。")
        return default_drones
    except Exception as e:
        logger.error(f"加载默认无人机配置失败: {e}")
        return []
