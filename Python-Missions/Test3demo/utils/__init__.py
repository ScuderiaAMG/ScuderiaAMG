"""
utils/__init__.py

此文件使 utils 目录成为一个 Python 包，方便从其他模块导入其子模块。
"""
# 可以在这里导入一些常用的函数或类，方便直接从 utils 导入
# 例如: from .logger import logger
# 但通常为了清晰，推荐使用 from utils.logger import logger

# 也可以定义包的元数据
__all__ = ['file_handler', 'input_handler', 'logger']