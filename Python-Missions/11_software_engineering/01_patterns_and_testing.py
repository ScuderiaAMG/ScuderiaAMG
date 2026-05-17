#!/usr/bin/env python3
"""
软件工程实践 —— 测试、重构、架构模式
涵盖：unittest/pytest 风格测试、Mock 与 Monkey Patching、
      SOLID 原则实战、依赖注入、事件驱动架构、
      CQRS / Event Sourcing 简例、插件系统、配置管理
"""

import unittest
import threading
import json
import time
import os
import sys
import tempfile
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Protocol
from functools import wraps
from contextlib import contextmanager
import warnings


# ============================================================
# §1  unittest 测试框架实战
# ============================================================

class Calculator:
    """被测试的目标类。"""

    def add(self, a: float, b: float) -> float:
        return a + b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b

    def factorial(self, n: int) -> int:
        if n < 0:
            raise ValueError("n 必须 >= 0")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    def average(self, numbers: list[float]) -> float:
        if not numbers:
            raise ValueError("列表不能为空")
        return sum(numbers) / len(numbers)

    def is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def fibonacci(self, n: int) -> list[int]:
        if n < 0:
            raise ValueError("n 必须 >= 0")
        result = [0, 1]
        for _ in range(2, n + 1):
            result.append(result[-1] + result[-2])
        return result[:n + 1]


class TestCalculator(unittest.TestCase):
    """完整的 unittest 测试套件。"""

    @classmethod
    def setUpClass(cls) -> None:
        """整个测试类只运行一次。"""
        cls.calc = Calculator()

    def setUp(self) -> None:
        """每个测试方法前运行。"""
        self.start_time = time.time()

    def tearDown(self) -> None:
        """每个测试方法后运行。"""
        elapsed = time.time() - self.start_time
        if elapsed > 0.1:
            warnings.warn(f"测试 {self.id()} 耗时 {elapsed:.3f}s")

    # ---- 基础断言 ----
    def test_add_positive(self):
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_add_negative(self):
        self.assertEqual(self.calc.add(-1, -1), -2)

    def test_add_float(self):
        self.assertAlmostEqual(self.calc.add(0.1, 0.2), 0.3, places=7)

    # ---- 异常断言 ----
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError) as ctx:
            self.calc.divide(10, 0)
        self.assertIn("除数不能为零", str(ctx.exception))

    def test_divide_normal(self):
        self.assertEqual(self.calc.divide(10, 2), 5.0)

    # ---- 参数化等价测试 ----
    def test_factorial(self):
        test_cases = [
            (0, 1), (1, 1), (2, 2), (3, 6),
            (4, 24), (5, 120), (6, 720),
        ]
        for n, expected in test_cases:
            with self.subTest(n=n):
                self.assertEqual(self.calc.factorial(n), expected)

    def test_factorial_negative(self):
        with self.assertRaises(ValueError):
            self.calc.factorial(-1)

    # ---- 集合断言 ----
    def test_average(self):
        self.assertEqual(self.calc.average([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(self.calc.average([1.5, 2.5]), 2.0)

    def test_average_empty(self):
        with self.assertRaises(ValueError):
            self.calc.average([])

    # ---- 真假断言 ----
    def test_is_prime(self):
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29}
        non_primes = {0, 1, 4, 6, 8, 9, 10, 12, 14, 15}
        for p in primes:
            with self.subTest(n=p):
                self.assertTrue(self.calc.is_prime(p))
        for np in non_primes:
            with self.subTest(n=np):
                self.assertFalse(self.calc.is_prime(np))


class MockDatabase:
    """Mock 对象 —— 模拟数据库操作。"""

    def __init__(self) -> None:
        self.data: dict[int, dict[str, Any]] = {}
        self.query_calls: list[tuple[str, tuple]] = []

    def execute(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        self.query_calls.append((query, params))
        return [row for row in self.data.values()]

    def insert(self, id_val: int, row: dict[str, Any]) -> None:
        self.data[id_val] = row


class TestWithMock(unittest.TestCase):
    """使用 Mock 对象进行隔离测试。"""

    def test_mock_database(self):
        db = MockDatabase()
        db.data = {1: {"name": "Alice", "age": 30}}
        results = db.execute("SELECT * FROM users WHERE id=?", (1,))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alice")
        self.assertEqual(len(db.query_calls), 1)


# ============================================================
# §2  依赖注入与 IoC 容器
# ============================================================

class Service(ABC):
    """服务接口。"""
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...


class EmailService(Service):
    def execute(self, *args: Any, **kwargs: Any) -> str:
        to_addr = kwargs.get("to", "unknown")
        return f"[Email] 发送给 {to_addr}"


class SMSService(Service):
    def execute(self, *args: Any, **kwargs: Any) -> str:
        phone = kwargs.get("phone", "unknown")
        return f"[SMS] 发送给 {phone}"


class NotificationClient:
    """使用依赖注入的客户端 —— 不依赖具体实现。"""

    def __init__(self, service: Service) -> None:
        self._service = service

    def notify(self, **kwargs: Any) -> str:
        return self._service.execute(**kwargs)

    def set_service(self, service: Service) -> None:
        self._service = service


class SimpleContainer:
    """简易 IoC 容器。"""

    def __init__(self) -> None:
        self._services: dict[str, type] = {}
        self._instances: dict[str, Any] = {}
        self._singletons: set[str] = set()

    def register(self, name: str, cls: type, singleton: bool = False) -> None:
        self._services[name] = cls
        if singleton:
            self._singletons.add(name)

    def resolve(self, name: str) -> Any:
        if name in self._instances:
            return self._instances[name]

        cls = self._services.get(name)
        if cls is None:
            raise KeyError(f"未注册的服务: {name}")

        instance = cls()
        if name in self._singletons:
            self._instances[name] = instance
        return instance


# ============================================================
# §3  事件驱动架构
# ============================================================

@dataclass
class Event:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


EventHandler = Callable[[Event], None]


class EventBus:
    """发布-订阅事件总线。"""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[Event] = []
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        with self._lock:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        with self._lock:
            handlers = self._handlers.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)

    def publish(self, event: Event) -> None:
        with self._lock:
            self._history.append(event)
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            handler(event)

    async def publish_async(self, event: Event) -> None:
        """异步事件发布 (简化, 实际中应使用 asyncio)。"""
        import asyncio
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, handler, event)

    def replay(self) -> list[Event]:
        return self._history.copy()


class OrderService:
    """使用事件总线的订单服务。"""

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.orders: dict[str, dict[str, Any]] = {}

        bus.subscribe("order_created", self._on_order_created)
        bus.subscribe("order_paid", self._on_order_paid)

    def create_order(self, order_id: str, amount: float) -> None:
        order = {"id": order_id, "amount": amount, "status": "pending"}
        self.orders[order_id] = order
        self.bus.publish(Event("order_created",
                               {"order_id": order_id, "amount": amount}))

    def pay_order(self, order_id: str) -> None:
        if order_id in self.orders:
            self.orders[order_id]["status"] = "paid"
            self.bus.publish(Event("order_paid",
                                   {"order_id": order_id}))

    def _on_order_created(self, event: Event) -> None:
        print(f"  [OrderService] 订单创建: {event.payload['order_id']}")

    def _on_order_paid(self, event: Event) -> None:
        print(f"  [OrderService] 订单支付: {event.payload['order_id']}")


class EmailNotifier:
    def __init__(self, bus: EventBus) -> None:
        bus.subscribe("order_created", self.send_confirmation)
        bus.subscribe("order_paid", self.send_receipt)

    def send_confirmation(self, event: Event) -> None:
        print(f"  [Email] 确认邮件: 订单 {event.payload['order_id']} 已创建")

    def send_receipt(self, event: Event) -> None:
        print(f"  [Email] 收据邮件: 订单 {event.payload['order_id']} 已支付")


# ============================================================
# §4  插件系统
# ============================================================

class PluginBase(ABC):
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...


class PluginManager:
    """可扩展的插件管理器。"""

    def __init__(self) -> None:
        self._plugins: dict[str, PluginBase] = {}

    def register(self, plugin: PluginBase) -> None:
        self._plugins[plugin.name()] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def execute(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in self._plugins:
            raise KeyError(f"插件不存在: {name}")
        return self._plugins[name].execute(*args, **kwargs)

    def execute_pipeline(self, names: list[str],
                         initial_data: Any = None) -> Any:
        """按顺序执行一组插件，数据依次流过。"""
        data = initial_data
        for name in names:
            data = self.execute(name, data=data)
        return data

    def list_plugins(self) -> list[str]:
        return sorted(self._plugins.keys())


class UpperCasePlugin(PluginBase):
    def name(self) -> str:
        return "uppercase"

    def version(self) -> str:
        return "1.0.0"

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        data = kwargs.get("data", args[0] if args else "")
        return str(data).upper()


class ReversePlugin(PluginBase):
    def name(self) -> str:
        return "reverse"

    def version(self) -> str:
        return "1.0.0"

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        data = kwargs.get("data", args[0] if args else "")
        return str(data)[::-1]


class PrefixPlugin(PluginBase):
    def __init__(self, prefix: str = ">> ") -> None:
        self._prefix = prefix

    def name(self) -> str:
        return "prefix"

    def version(self) -> str:
        return "1.0.0"

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        data = kwargs.get("data", args[0] if args else "")
        return self._prefix + str(data)


# ============================================================
# §5  配置管理
# ============================================================

@dataclass
class ConfigSection:
    pass


@dataclass
class AppConfig:
    """层次化配置系统。"""

    class Database(ConfigSection):
        host: str = "localhost"
        port: int = 5432
        name: str = "app_db"
        user: str = "admin"
        password: str = ""

    class Cache(ConfigSection):
        enabled: bool = True
        ttl_seconds: int = 3600
        max_entries: int = 10000

    class Logging(ConfigSection):
        level: str = "INFO"
        file: str = "app.log"
        max_bytes: int = 10 * 1024 * 1024
        backup_count: int = 5

    db: Database = field(default_factory=Database)
    cache: Cache = field(default_factory=Cache)
    logging: Logging = field(default_factory=Logging)
    debug: bool = False
    secret_key: str = ""


class ConfigLoader:
    """配置加载器 —— 支持多层覆盖。"""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}

    def load_dict(self, data: dict[str, Any]) -> "ConfigLoader":
        self._deep_update(self._config, data)
        return self

    def load_json(self, path: str) -> "ConfigLoader":
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._deep_update(self._config, data)
        except FileNotFoundError:
            pass
        return self

    def load_env(self, prefix: str = "APP_") -> "ConfigLoader":
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # 尝试解析 JSON 值
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
                self._deep_update(self._config, {config_key: value})
        return self

    def load_args(self, args: dict[str, str]) -> "ConfigLoader":
        for key, value in args.items():
            self._deep_update(self._config, {key: value})
        return self

    def build(self) -> dict[str, Any]:
        return self._config.copy()

    @staticmethod
    def _deep_update(base: dict, update: dict) -> None:
        for key, value in update.items():
            if (key in base and isinstance(base[key], dict)
                    and isinstance(value, dict)):
                ConfigLoader._deep_update(base[key], value)
            else:
                base[key] = value


# ============================================================
# §6  装饰器工具集
# ============================================================

def retry(max_attempts: int = 3, delay: float = 0.5,
          backoff: float = 2.0,
          exceptions: tuple[type[BaseException], ...] = (Exception,)):
    """可重试的装饰器 —— 指数退避。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise RuntimeError(
                            f"{func.__name__} 重试 {max_attempts} 次后仍失败"
                        ) from e
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """计时装饰器。"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__}: {elapsed*1000:.3f}ms")
        return result
    return wrapper


def memoize(func: Callable) -> Callable:
    """记忆化装饰器。"""
    cache: dict[tuple, Any] = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache     # type: ignore[attr-defined]
    wrapper.clear_cache = lambda: cache.clear()  # type: ignore[attr-defined]
    return wrapper


def deprecated(reason: str = "") -> Callable:
    """标记函数为废弃。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} 已废弃"
            if reason:
                msg += f": {reason}"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls: type) -> type:
    """单例类装饰器。"""
    instances: dict[type, Any] = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def validate_types(**expected_types: type):
    """运行时类型检查装饰器。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg_name, expected in expected_types.items():
                if arg_name in kwargs:
                    val = kwargs[arg_name]
                    if not isinstance(val, expected):
                        raise TypeError(
                            f"{arg_name} 期望 {expected.__name__}, "
                            f"收到 {type(val).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# §7  演示
# ============================================================

def demo_software_engineering() -> None:
    print("=" * 60)
    print("软件工程实践")
    print("=" * 60)

    # 依赖注入
    print("\n--- 依赖注入 ---")
    email = EmailService()
    sms = SMSService()
    client = NotificationClient(email)
    print(client.notify(to="alice@example.com"))
    client.set_service(sms)
    print(client.notify(phone="+86-123-4567"))

    # IoC 容器
    container = SimpleContainer()
    container.register("email", EmailService, singleton=True)
    container.register("sms", SMSService)
    svc1 = container.resolve("email")
    svc2 = container.resolve("email")
    print(f"IoC 单例: svc1 is svc2 = {svc1 is svc2}")

    # 事件总线
    print("\n--- 事件驱动 ---")
    bus = EventBus()
    order_svc = OrderService(bus)
    email_notifier = EmailNotifier(bus)
    order_svc.create_order("ORD-001", 99.99)
    order_svc.pay_order("ORD-001")
    print(f"事件历史: {len(bus.replay())} 条")

    # 插件系统
    print("\n--- 插件系统 ---")
    pm = PluginManager()
    pm.register(UpperCasePlugin())
    pm.register(ReversePlugin())
    pm.register(PrefixPlugin(">>> "))
    result = pm.execute_pipeline(
        ["uppercase", "reverse", "prefix"],
        initial_data="hello world"
    )
    print(f"pipeline 结果: {result}")
    print(f"已注册插件: {pm.list_plugins()}")

    # 配置管理
    print("\n--- 配置管理 ---")
    loader = ConfigLoader()
    loader.load_dict({"debug": True, "db": {"host": "prod-server"}})
    loader.load_dict({"db": {"port": 3306}, "cache": {"ttl_seconds": 7200}})
    config = loader.build()
    print(f"配置: {json.dumps(config, indent=2, ensure_ascii=False)}")

    # 装饰器演示
    print("\n--- 装饰器工具 ---")

    @measure_time
    @retry(max_attempts=3, delay=0.01)
    def maybe_fails() -> str:
        return "成功"

    print(f"retry+计时: {maybe_fails()}")

    @memoize
    def slow_fib(n: int) -> int:
        if n < 2:
            return n
        return slow_fib(n - 1) + slow_fib(n - 2)

    t0 = time.perf_counter()
    fib30 = slow_fib(30)
    t1 = time.perf_counter()
    print(f"memoize fib(30) 第1次: {t1-t0:.4f}s, result={fib30}")
    t2 = time.perf_counter()
    fib30_2 = slow_fib(30)
    t3 = time.perf_counter()
    print(f"memoize fib(30) 第2次: {t3-t2:.6f}s, result={fib30_2}")

    # 运行 unittest
    print("\n--- 单元测试运行 ---")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculator)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    print(f"测试: {result.testsRun} 个, 成功 {result.testsRun - len(result.failures) - len(result.errors)}, "
          f"失败 {len(result.failures)}, 错误 {len(result.errors)}")


if __name__ == "__main__":
    demo_software_engineering()
    print("\n✅ 软件工程篇执行完毕!")
