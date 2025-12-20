"""
models/__init__.py

此文件使 models 目录成为一个 Python 包，方便从其他模块导入其子模块。
"""
# 可以在这里导入一些常用的类，方便直接从 models 导入
# 例如: from .user import User
# 但通常为了清晰，推荐使用 from models.user import User

# 也可以定义包的元数据
__all__ = ['user', 'field', 'drone', 'pesticide', 'simulation']