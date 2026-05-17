#!/usr/bin/env python3
"""
Python 面向对象编程 (OOP)
涵盖：类与实例、继承与多态、封装与属性、魔术方法、抽象类、数据类、枚举
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict, astuple
from enum import Enum, IntEnum, StrEnum, auto, unique
from functools import total_ordering
from typing import Any, ClassVar, Final, Self


# ============================================================
# §1  类与实例
# ============================================================

class Vehicle:
    """交通工具基类 — 展示 __init__ / __repr__ / __str__ / 实例属性与类属性。"""

    # 类属性（所有实例共享）
    count: ClassVar[int] = 0
    _registry: ClassVar[list["Vehicle"]] = []

    def __init__(self, brand: str, model: str, year: int) -> None:
        self.brand = brand                     # 实例属性（公有）
        self.model = model
        self.year = year
        self._mileage: float = 0.0             # 实例属性（受保护，单下划线约定）
        self.__vin: str = self._generate_vin() # 实例属性（私有，双下划线 → name mangling）

        Vehicle.count += 1
        Vehicle._registry.append(self)

    @staticmethod
    def _generate_vin() -> str:
        import random
        return "VIN-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))

    # --- 魔术方法 ---
    def __repr__(self) -> str:
        """开发者友好的字符串表示（repr() 或直接回车）。"""
        return f"Vehicle(brand={self.brand!r}, model={self.model!r}, year={self.year})"

    def __str__(self) -> str:
        """用户友好的字符串表示（print() / str()）。"""
        return f"{self.year} {self.brand} {self.model}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vehicle):
            return NotImplemented
        return (self.brand, self.model, self.year) == (other.brand, other.model, other.year)

    def __hash__(self) -> int:
        return hash((self.brand, self.model, self.year))

    def __lt__(self, other: "Vehicle") -> bool:
        return self.year < other.year

    # --- 属性访问器 @property ---
    @property
    def mileage(self) -> float:
        """只读属性：行驶里程。"""
        return self._mileage

    @property
    def vin(self) -> str:
        """只读属性暴露私有 VIN。"""
        return self.__vin

    # --- 常规方法 ---
    def drive(self, distance: float) -> None:
        if distance < 0:
            raise ValueError("距离必须为非负数")
        self._mileage += distance

    @classmethod
    def get_count(cls) -> int:
        return cls.count

    @classmethod
    def get_registry(cls) -> list["Vehicle"]:
        return cls._registry

    @staticmethod
    def is_vintage(year: int) -> bool:
        return year < 1980


def demo_basic_class() -> None:
    print("=" * 60)
    print("§1  类与实例")
    print("=" * 60)

    v1 = Vehicle("Toyota", "Corolla", 2020)
    v2 = Vehicle("Honda", "Civic", 2022)

    print(f"repr: {v1!r}")
    print(f"str:  {v1}")
    print(f"eq:   {v1 == v2}")
    print(f"lt:   {v1 < v2}")
    print(f"hash: {hash(v1)}")

    v1.drive(150.5)
    v1.drive(80)
    print(f"mileage: {v1.mileage}")
    print(f"VIN: {v1.vin}")
    # 私有属性 name mangling: _Vehicle__vin
    print(f"间接访问 __vin: {v1._Vehicle__vin}")  # type: ignore[attr-defined]

    print(f"车辆计数: {Vehicle.get_count()}")
    print(f"vintage 判定 (1975): {Vehicle.is_vintage(1975)}")
    print(f"vintage 判定 (2000): {Vehicle.is_vintage(2000)}")


# ============================================================
# §2  继承与多态
# ============================================================

class ElectricVehicle(Vehicle):
    """电动车 — 继承 Vehicle。"""

    def __init__(self, brand: str, model: str, year: int,
                 battery_kwh: float = 60.0) -> None:
        super().__init__(brand, model, year)     # 必须显式调用 super().__init__
        self.battery_kwh = battery_kwh
        self._charge_pct: float = 100.0

    def __repr__(self) -> str:
        return (f"ElectricVehicle(brand={self.brand!r}, model={self.model!r}, "
                f"year={self.year}, battery_kwh={self.battery_kwh})")

    @property
    def charge(self) -> float:
        return self._charge_pct

    def drive(self, distance: float) -> None:
        """重写父类方法：消耗电量。"""
        consumption = distance * 0.18            # 假设 0.18 kWh / km
        self._charge_pct = max(0, self._charge_pct - consumption / self.battery_kwh * 100)
        super().drive(distance)                  # 仍记录里程

    def recharge(self) -> None:
        self._charge_pct = 100.0


class HybridVehicle(Vehicle):
    """混动车 — 展示多重继承的思路（通过合作式 super()）。"""

    def __init__(self, brand: str, model: str, year: int,
                 fuel_efficiency: float = 20.0) -> None:
        super().__init__(brand, model, year)
        self.fuel_efficiency = fuel_efficiency   # km/L
        self._fuel_level: float = 50.0           # L

    @property
    def fuel_level(self) -> float:
        return self._fuel_level

    def drive(self, distance: float) -> None:
        fuel_used = distance / self.fuel_efficiency
        self._fuel_level = max(0, self._fuel_level - fuel_used)
        super().drive(distance)

    def refuel(self, litres: float) -> None:
        self._fuel_level = min(80.0, self._fuel_level + litres)


def demo_inheritance() -> None:
    print("\n" + "=" * 60)
    print("§2  继承与多态")
    print("=" * 60)

    ev = ElectricVehicle("Tesla", "Model 3", 2024, battery_kwh=75)
    hy = HybridVehicle("Toyota", "Prius", 2023, fuel_efficiency=25)

    # 多态：同一个接口，不同行为
    fleet: list[Vehicle] = [ev, hy]
    for v in fleet:
        v.drive(100)
        print(f"{v.model}: mileage={v.mileage:.0f}, "
              + (f"charge={ev.charge:.0f}%"
                 if isinstance(v, ElectricVehicle)
                 else f"fuel={hy.fuel_level:.1f}L"))

    print(f"isinstance(ev, Vehicle) = {isinstance(ev, Vehicle)}")
    print(f"issubclass(ElectricVehicle, Vehicle) = {issubclass(ElectricVehicle, Vehicle)}")
    print(f"MRO of HybridVehicle: {[c.__name__ for c in HybridVehicle.__mro__]}")


# ============================================================
# §3  属性描述符与 property 进阶
# ============================================================

class ValidatedAttribute:
    """描述符 — 对属性进行验证。"""

    def __init__(self, name: str, expected_type: type,
                 min_value: Any = None, max_value: Any = None) -> None:
        self.name = name
        self.expected_type = expected_type
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self.name, None)

    def __set__(self, instance: Any, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} 期望 {self.expected_type.__name__}, "
                            f"收到 {type(value).__name__}")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} 不得小于 {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} 不得大于 {self.max_value}")
        instance.__dict__[self.name] = value


class Person:
    name = ValidatedAttribute("name", str)
    age = ValidatedAttribute("age", int, min_value=0, max_value=150)

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    # property 进阶：setter / deleter
    _salary: float = 0.0

    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, value: float) -> None:
        if value < 0:
            raise ValueError("工资不得为负")
        self._salary = value

    @salary.deleter
    def salary(self) -> None:
        self._salary = 0.0


def demo_descriptors() -> None:
    print("\n" + "=" * 60)
    print("§3  属性描述符与 property")
    print("=" * 60)

    p = Person("Alice", 30)
    p.salary = 50000
    print(f"Person: name={p.name}, age={p.age}, salary={p.salary}")
    del p.salary
    print(f"After del salary: {p.salary}")

    # 验证捕获
    try:
        p.age = -5
    except ValueError as e:
        print(f"验证错误: {e}")
    try:
        p.age = "thirty"
    except TypeError as e:
        print(f"类型错误: {e}")


# ============================================================
# §4  魔术方法大全
# ============================================================

@total_ordering                               # 只需定义 __eq__ 和 __lt__，自动推导其余比较
class Money:
    """演示 __add__ / __radd__ / __iadd__ / __neg__ / __bool__ / __call__ 等。"""

    def __init__(self, amount: float, currency: str = "CNY") -> None:
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("不同货币不能直接比较大小")
        return self.amount < other.amount

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"不同货币不能相加: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"不同货币不能相减: {self.currency} vs {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor: float) -> "Money":
        return self.__mul__(factor)

    def __truediv__(self, divisor: float) -> "Money":
        return Money(self.amount / divisor, self.currency)

    def __bool__(self) -> bool:
        return self.amount != 0

    def __call__(self, tax_rate: float) -> "Money":
        """将 Money 实例变成可调用对象，计算含税金额。"""
        return Money(self.amount * (1 + tax_rate), self.currency)

    def __format__(self, fmt: str) -> str:
        return f"{self.currency} {self.amount:{fmt}}"

    def __len__(self) -> int:
        """金额的整数位数（非标准语义，仅作演示）。"""
        return len(str(int(abs(self.amount))))


class Resource:
    """演示上下文管理器 __enter__ / __exit__。"""

    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> "Resource":
        print(f"  [Resource] 获取 {self.name}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        print(f"  [Resource] 释放 {self.name}")
        if exc_type is not None:
            print(f"    异常: {exc_type.__name__}: {exc_val}")
            # return True 会抑制异常；return False 则继续传播
        return False


class SliceableList:
    """演示 __getitem__ / __setitem__ / __delitem__ / __contains__ / __iter__。"""

    def __init__(self, data: list[int]) -> None:
        self._data = data

    def __getitem__(self, index: int | slice) -> int | list[int]:
        print(f"  __getitem__({index!r})")
        return self._data[index]

    def __setitem__(self, index: int | slice, value: int | list[int]) -> None:
        print(f"  __setitem__({index!r}, {value!r})")
        self._data[index] = value

    def __delitem__(self, index: int) -> None:
        print(f"  __delitem__({index!r})")
        del self._data[index]

    def __contains__(self, item: int) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[int]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __reversed__(self) -> Iterator[int]:
        return reversed(self._data)


def demo_magic_methods() -> None:
    print("\n" + "=" * 60)
    print("§4  魔术方法大全")
    print("=" * 60)

    # Money
    m1 = Money(100, "CNY")
    m2 = Money(50, "CNY")
    print(f"Money: m1={m1}, m2={m2}")
    print(f"  m1 + m2 = {m1 + m2}")
    print(f"  m1 - m2 = {m1 - m2}")
    print(f"  -m1 = {-m1}")
    print(f"  m1 * 3 = {m1 * 3}")
    print(f"  3 * m1 = {3 * m1}")
    print(f"  m1 / 2 = {m1 / 2}")
    print(f"  bool(m1) = {bool(m1)}, bool(Money(0)) = {bool(Money(0, 'CNY'))}")
    print(f"  m1(0.13) = {m1(0.13)}  (13% tax)")
    print(f"  len(m1) = {len(m1)}")
    print(f"  m1 == m2: {m1 == m2}")
    print(f"  m1 > m2: {m1 > m2}")

    # Resource (context manager)
    print("\ncontext manager:")
    with Resource("file_handle") as res:
        print(f"    使用 {res.name} 中...")

    with Resource("failing") as res:
        print(f"    使用 {res.name} 中...")
        # raise ValueError("模拟失败")

    # SliceableList
    print("\n容器协议:")
    sl = SliceableList([10, 20, 30, 40, 50])
    print(f"  len(sl) = {len(sl)}")
    print(f"  sl[2] = {sl[2]}")
    sl[1] = 99
    print(f"  10 in sl: {10 in sl}")
    print(f"  list(reversed(sl)): {list(reversed(sl))}")


# ============================================================
# §5  抽象基类 (ABC) 与接口
# ============================================================

class Shape(ABC):
    """抽象形状基类。"""

    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...

    def describe(self) -> str:
        """具体方法：可被子类继承或重写。"""
        return f"{self.__class__.__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"

    @classmethod
    @abstractmethod
    def from_string(cls, spec: str) -> "Shape":
        ...


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius

    @classmethod
    def from_string(cls, spec: str) -> "Circle":
        # 格式: "Circle 5.0"
        _, r = spec.split()
        return cls(float(r))


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    @classmethod
    def from_string(cls, spec: str) -> "Rectangle":
        _, w, h = spec.split()
        return cls(float(w), float(h))


def demo_abstract() -> None:
    print("\n" + "=" * 60)
    print("§5  抽象基类 (ABC)")
    print("=" * 60)

    shapes: list[Shape] = [
        Circle(5),
        Rectangle(4, 6),
        Circle.from_string("Circle 3.0"),
        Rectangle.from_string("Rectangle 7 2"),
    ]
    for s in shapes:
        print(f"  {s.describe()}")

    # 不可实例化抽象类
    try:
        _ = Shape()                              # type: ignore[abstract]
    except TypeError as e:
        print(f"  TypeError: {e}")


# ============================================================
# §6  dataclass — 数据类
# ============================================================

@dataclass(order=True, frozen=False)
class Employee:
    """dataclass 自动生成 __init__ / __repr__ / __eq__ / __hash__ 等。"""
    name: str
    role: str
    salary: float = 0.0
    skills: list[str] = field(default_factory=list, repr=False, compare=False)

    def promote(self, increase: float) -> None:
        self.salary += increase


@dataclass(frozen=True)                          # 不可变（只读）
class GeoPoint:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """初始化后验证（对 frozen=True 需要用 object.__setattr__）。"""
        if not (-90 <= self.latitude <= 90):
            raise ValueError("纬度范围 [-90, 90]")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("经度范围 [-180, 180]")


def demo_dataclass() -> None:
    print("\n" + "=" * 60)
    print("§6  dataclass")
    print("=" * 60)

    e1 = Employee("Alice", "Engineer", 80000, ["Python", "C++"])
    e2 = Employee("Bob", "Manager", 90000, ["Leadership"])
    e3 = Employee("Alice", "Engineer", 80000)    # skills 不同但不参与比较

    print(f"e1: {e1}")
    print(f"e1 == e2: {e1 == e2}")
    print(f"e1 == e3: {e1 == e3}  (skills 被排除在比较外)")
    print(f"asdict(e1): {asdict(e1)}")
    print(f"astuple(e1): {astuple(e1)}")

    e1.promote(5000)
    print(f"after promote: {e1.salary}")

    # frozen
    pt = GeoPoint(39.9, 116.4)
    print(f"GeoPoint: {pt}")
    try:
        pt.latitude = 40                        # type: ignore[misc]
    except Exception as e:
        print(f"FrozenDataclassError: {type(e).__name__}")


# ============================================================
# §7  Enum — 枚举
# ============================================================

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def describe(self) -> str:
        return f"Color.{self.name} = {self.value}"


class HttpStatus(IntEnum):                       # 与 int 兼容
    OK = 200
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


@unique                                         # 确保值不重复
class Direction(StrEnum):                        # Python 3.11+
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Priority(Enum):
    LOW = auto()                                 # 自增值 1, 2, 3...
    MEDIUM = auto()
    HIGH = auto()


def demo_enum() -> None:
    print("\n" + "=" * 60)
    print("§7  Enum 枚举")
    print("=" * 60)

    print(f"Color.RED: {Color.RED}, value={Color.RED.value}")
    print(f"Color(2):  {Color(2)}")
    print(f"Color['BLUE']: {Color['BLUE']}")

    print(f"HttpStatus.OK == 200: {HttpStatus.OK == 200}")  # IntEnum 可与 int 比较
    print(f"Direction.NORTH == 'north': {Direction.NORTH == 'north'}")

    for p in Priority:
        print(f"  Priority.{p.name} = {p.value}")


# ============================================================
# §8  设计原则：SOLID 示例
# ============================================================

class ReportExporter(ABC):
    """OCP (开闭原则): 对扩展开放，对修改封闭。"""
    @abstractmethod
    def export(self, data: list[dict[str, Any]]) -> str:
        ...


class JsonExporter(ReportExporter):
    def export(self, data: list[dict[str, Any]]) -> str:
        import json
        return json.dumps(data, ensure_ascii=False, indent=2)


class CsvExporter(ReportExporter):
    def export(self, data: list[dict[str, Any]]) -> str:
        import csv
        import io
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()


class ReportService:
    """DIP (依赖倒转): 依赖抽象而非具体实现。"""
    def __init__(self, exporter: ReportExporter) -> None:
        self.exporter = exporter

    def generate(self, data: list[dict[str, Any]]) -> str:
        return self.exporter.export(data)


def demo_solid() -> None:
    print("\n" + "=" * 60)
    print("§8  SOLID 设计示例")
    print("=" * 60)

    data = [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]

    json_svc = ReportService(JsonExporter())
    csv_svc = ReportService(CsvExporter())

    print(f"JSON:\n{json_svc.generate(data)}")
    print(f"CSV:\n{csv_svc.generate(data)}")


if __name__ == "__main__":
    demo_basic_class()
    demo_inheritance()
    demo_descriptors()
    demo_magic_methods()
    demo_abstract()
    demo_dataclass()
    demo_enum()
    demo_solid()
    print("\n✅ OOP 篇全部执行完毕!")
