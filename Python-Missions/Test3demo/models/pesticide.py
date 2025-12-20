"""
models/pesticide.py

定义 Pesticide 类，用于表示农药。
包含农药名称、类型、混合注意事项等信息。
"""
from typing import Dict, Any, List
from utils.logger import logger

class Pesticide:
    """
    表示一种农药。
    """
    def __init__(self, name: str, pesticide_type: str, mixing_notes: str = "", incompatible_with: List[str] = None):
        """
        初始化农药对象。
        Args:
            name (str): 农药名称。
            pesticide_type (str): 农药类型 (例如: 杀虫剂, 杀菌剂, 除草剂)。
            mixing_notes (str): 混合比例和注意事项。
            incompatible_with (list): 不能与之混合的农药名称列表。
        """
        self.name = name
        self.type = pesticide_type
        self.mixing_notes = mixing_notes
        self.incompatible_with = incompatible_with or [] # 防止可变默认参数

    def is_compatible_with(self, other_pesticide_name: str) -> bool:
        """
        检查此农药是否与另一种农药兼容。
        Args:
            other_pesticide_name (str): 另一种农药的名称。
        Returns:
            bool: 如果兼容返回 True，否则返回 False。
        """
        return other_pesticide_name not in self.incompatible_with

    def to_dict(self) -> Dict[str, Any]:
        """
        将农药对象转换为字典，用于 JSON 序列化。
        Returns:
            dict: 包含农药信息的字典。
        """
        return {
            'name': self.name,
            'type': self.type,
            'mixing_notes': self.mixing_notes,
            'incompatible_with': self.incompatible_with
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        从字典创建农药对象，用于 JSON 反序列化。
        Args:
            data (dict): 包含农药信息的字典。
        Returns:
            Pesticide: 农药对象。
        """
        return cls(
            name=data['name'],
            pesticide_type=data['type'],
            mixing_notes=data.get('mixing_notes', ''),
            incompatible_with=data.get('incompatible_with', [])
        )

    def __repr__(self):
        return f"Pesticide(name='{self.name}', type='{self.type}')"
