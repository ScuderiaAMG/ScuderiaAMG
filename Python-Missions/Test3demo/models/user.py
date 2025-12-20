# """
# models/user.py

# 定义 User 类，用于表示系统中的用户。
# 包含用户名、密码、关联的农田、无人机等信息。
# """
# import hashlib
# from utils.file_handler import load_user_data, save_user_data
# from utils.logger import logger

# class User:
#     """
#     表示一个用户。
#     """
#     def __init__(self, username: str, password_hash: str):
#         """
#         初始化用户对象。
#         Args:
#             username (str): 用户名。
#             password_hash (str): 密码的哈希值。
#         """
#         self.username = username
#         self.password_hash = password_hash
#         # 可以考虑将农田、无人机、农药列表的名称存储在此处，实际数据存文件
#         self.field_names = []
#         self.drone_names = []
#         self.pesticide_list = [] # 或者只存储农药名称列表

#     @classmethod
#     def create(cls, username: str, raw_password: str):
#         """
#         创建一个新用户实例（用于注册）。
#         Args:
#             username (str): 用户名。
#             raw_password (str): 原始密码。
#         Returns:
#             User: 新创建的用户对象。
#         """
#         password_hash = cls.hash_password(raw_password)
#         return cls(username, password_hash)

#     @staticmethod
#     def hash_password(password: str) -> str:
#         """
#         对密码进行哈希处理。
#         Args:
#             password (str): 原始密码。
#         Returns:
#             str: 密码的哈希值。
#         """
#         # 使用 SHA-256 哈希算法 (实际应用中建议使用更安全的算法如 bcrypt 或 argon2)
#         return hashlib.sha256(password.encode('utf-8')).hexdigest()

#     def check_password(self, raw_password: str) -> bool:
#         """
#         验证提供的密码是否正确。
#         Args:
#             raw_password (str): 提供的原始密码。
#         Returns:
#             bool: 如果密码正确返回 True，否则返回 False。
#         """
#         return self.password_hash == self.hash_password(raw_password)

#     def to_dict(self):
#         """
#         将用户对象转换为字典，用于 JSON 序列化。
#         Returns:
#             dict: 包含用户信息的字典。
#         """
#         return {
#             'username': self.username,
#             'password_hash': self.password_hash,
#             'field_names': self.field_names,
#             'drone_names': self.drone_names,
#             'pesticide_list': self.pesticide_list # 如果存储的是农药对象列表，需调用 to_dict
#         }

#     @classmethod
#     def from_dict(cls, data: dict):
#         """
#         从字典创建用户对象，用于 JSON 反序列化。
#         Args:
#             data (dict): 包含用户信息的字典。
#         Returns:
#             User: 用户对象。
#         """
#         user = cls(data['username'], data['password_hash'])
#         user.field_names = data.get('field_names', [])
#         user.drone_names = data.get('drone_names', [])
#         user.pesticide_list = data.get('pesticide_list', [])
#         return user

#     def save(self):
#         """
#         保存用户数据到文件。
#         """
#         try:
#             save_user_data(self)
#             logger.info(f"用户 {self.username} 的数据已保存。")
#         except Exception as e:
#             logger.error(f"保存用户 {self.username} 数据失败: {e}")

#     @classmethod
#     def load(cls, username: str):
#         """
#         从文件加载用户数据。
#         Args:
#             username (str): 用户名。
#         Returns:
#             User: 加载的用户对象，如果失败则返回 None。
#         """
#         try:
#             user = load_user_data(username)
#             if user:
#                 logger.info(f"用户 {user.username} 的数据已加载。")
#             return user
#         except Exception as e:
#             logger.error(f"加载用户 {username} 数据失败: {e}")
#             return None

#     def add_field_name(self, field_name: str):
#         """添加农田名称到用户列表中。"""
#         if field_name not in self.field_names:
#             self.field_names.append(field_name)

#     def remove_field_name(self, field_name: str):
#         """从用户列表中移除农田名称。"""
#         if field_name in self.field_names:
#             self.field_names.remove(field_name)

#     def add_drone_name(self, drone_name: str):
#         """添加无人机名称到用户列表中。"""
#         if drone_name not in self.drone_names:
#             self.drone_names.append(drone_name)

#     def remove_drone_name(self, drone_name: str):
#         """从用户列表中移除无人机名称。"""
#         if drone_name in self.drone_names:
#             self.drone_names.remove(drone_name)

#     # def add_pesticide(self, pesticide: 'Pesticide'): # 需要前向引用
#     #     """添加农药到用户列表中。"""
#     #     if pesticide not in self.pesticide_list:
#     #         self.pesticide_list.append(pesticide)

#     def __repr__(self):
#         return f"User(username='{self.username}')"

# # # 如果需要在农药类中引用用户类，可以使用字符串引用
# # from .pesticide import Pesticide


"""
models/user.py

定义 User 类，用于表示系统中的用户。
包含用户名、密码、关联的农田、无人机等信息。
"""
import hashlib
# 从这里移除对 utils.file_handler 的直接导入
# from utils.file_handler import load_user_data, save_user_data 
from utils.logger import logger

class User:
    """
    表示一个用户。
    """
    def __init__(self, username: str, password_hash: str):
        """
        初始化用户对象。
        Args:
            username (str): 用户名。
            password_hash (str): 密码的哈希值。
        """
        self.username = username
        self.password_hash = password_hash
        # 可以考虑将农田、无人机、农药列表的名称存储在此处，实际数据存文件
        self.field_names = []
        self.drone_names = []
        self.pesticide_list = [] # 或者只存储农药名称列表

    @classmethod
    def create(cls, username: str, raw_password: str):
        """
        创建一个新用户实例（用于注册）。
        Args:
            username (str): 用户名。
            raw_password (str): 原始密码。
        Returns:
            User: 新创建的用户对象。
        """
        password_hash = cls.hash_password(raw_password)
        return cls(username, password_hash)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希处理。
        Args:
            password (str): 原始密码。
        Returns:
            str: 密码的哈希值。
        """
        # 使用 SHA-256 哈希算法 (实际应用中建议使用更安全的算法如 bcrypt 或 argon2)
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, raw_password: str) -> bool:
        """
        验证提供的密码是否正确。
        Args:
            raw_password (str): 提供的原始密码。
        Returns:
            bool: 如果密码正确返回 True，否则返回 False。
        """
        return self.password_hash == self.hash_password(raw_password)

    def to_dict(self):
        """
        将用户对象转换为字典，用于 JSON 序列化。
        Returns:
            dict: 包含用户信息的字典。
        """
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'field_names': self.field_names,
            'drone_names': self.drone_names,
            'pesticide_list': self.pesticide_list # 如果存储的是农药对象列表，需调用 to_dict
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建用户对象，用于 JSON 反序列化。
        Args:
            data (dict): 包含用户信息的字典。
        Returns:
            User: 用户对象。
        """
        user = cls(data['username'], data['password_hash'])
        user.field_names = data.get('field_names', [])
        user.drone_names = data.get('drone_names', [])
        user.pesticide_list = data.get('pesticide_list', [])
        return user

    def save(self):
        """
        保存用户数据到文件。
        """
        # 在方法内部进行导入，避免循环导入
        from utils.file_handler import save_user_data
        try:
            save_user_data(self)
            logger.info(f"用户 {self.username} 的数据已保存。")
        except Exception as e:
            logger.error(f"保存用户 {self.username} 数据失败: {e}")

    @classmethod
    def load(cls, username: str):
        """
        从文件加载用户数据。
        Args:
            username (str): 用户名。
        Returns:
            User: 加载的用户对象，如果失败则返回 None。
        """
        # 在方法内部进行导入，避免循环导入
        from utils.file_handler import load_user_data
        try:
            user = load_user_data(username)
            if user:
                logger.info(f"用户 {user.username} 的数据已加载。")
            return user
        except Exception as e:
            logger.error(f"加载用户 {username} 数据失败: {e}")
            return None

    def add_field_name(self, field_name: str):
        """添加农田名称到用户列表中。"""
        if field_name not in self.field_names:
            self.field_names.append(field_name)

    def remove_field_name(self, field_name: str):
        """从用户列表中移除农田名称。"""
        if field_name in self.field_names:
            self.field_names.remove(field_name)

    def add_drone_name(self, drone_name: str):
        """添加无人机名称到用户列表中。"""
        if drone_name not in self.drone_names:
            self.drone_names.append(drone_name)

    def remove_drone_name(self, drone_name: str):
        """从用户列表中移除无人机名称。"""
        if drone_name in self.drone_names:
            self.drone_names.remove(drone_name)

    # def add_pesticide(self, pesticide: 'Pesticide'): # 需要前向引用
    #     """添加农药到用户列表中。"""
    #     if pesticide not in self.pesticide_list:
    #         self.pesticide_list.append(pesticide)

    def __repr__(self):
        return f"User(username='{self.username}')"

# # 如果需要在农药类中引用用户类，可以使用字符串引用
# from .pesticide import Pesticide