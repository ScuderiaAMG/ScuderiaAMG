"""
algorithms/__init__.py

此文件使 algorithms 目录成为一个 Python 包，方便从其他模块导入其子模块。
"""
# 可以在这里导入一些常用的算法类或函数，方便直接从 algorithms 导入
# 例如: from .pathfinding.a_star import AStarPlanner
# 但通常为了清晰，推荐使用 from algorithms.pathfinding.a_star import AStarPlanner

# 也可以定义包的元数据
__all__ = ['pathfinding', 'spraying']