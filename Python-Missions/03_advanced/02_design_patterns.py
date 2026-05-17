#!/usr/bin/env python3
"""
Python 高级 —— 设计模式
涵盖：创建型（单例、工厂、建造者、原型）、
      结构型（适配器、装饰器、代理、外观）、
      行为型（观察者、策略、责任链、命令、状态）
每种模式均提供可运行的完整 Python 实现
"""

from __future__ import annotations
import copy
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, ClassVar, Protocol, runtime_checkable


# ============================================================
# 创建型模式
# ============================================================

# --- 单例 (Singleton) ---
class SingletonMeta(type):
    """元类实现单例 — 保证全局只有一个实例。"""
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    """全局配置（单例）。"""

    def __init__(self) -> None:
        self._settings: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)


class BorgPattern:
    """Borg 模式 — 共享状态但不同实例。"""
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


# --- 工厂方法 (Factory Method) ---
class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        ...


class PDFDocument(Document):
    def render(self) -> str:
        return "PDF 文档内容"


class WordDocument(Document):
    def render(self) -> str:
        return "Word 文档内容"


class MarkdownDocument(Document):
    def render(self) -> str:
        return "# Markdown 文档内容"


class DocumentFactory:
    """工厂 — 根据类型创建文档。"""

    _registry: ClassVar[dict[str, type[Document]]] = {
        "pdf": PDFDocument,
        "word": WordDocument,
        "md": MarkdownDocument,
    }

    @classmethod
    def create(cls, doc_type: str) -> Document:
        doc_class = cls._registry.get(doc_type)
        if doc_class is None:
            raise ValueError(f"未知文档类型: {doc_type}")
        return doc_class()

    @classmethod
    def register(cls, doc_type: str, doc_class: type[Document]) -> None:
        cls._registry[doc_type] = doc_class


# --- 抽象工厂 (Abstract Factory) ---
class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...


class WindowsButton(Button):
    def render(self) -> str:
        return "[Windows 风格按钮]"


class WindowsCheckbox(Checkbox):
    def render(self) -> str:
        return "[Windows 风格复选框]"


class MacButton(Button):
    def render(self) -> str:
        return "[Mac 风格按钮]"


class MacCheckbox(Checkbox):
    def render(self) -> str:
        return "[Mac 风格复选框]"


class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...


class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()


class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()


# --- 建造者 (Builder) ---
class Query:
    """SQL 查询构建器。"""

    def __init__(self) -> None:
        self._select: list[str] = []
        self._from: str = ""
        self._where: list[str] = []
        self._order_by: list[str] = []
        self._limit: int | None = None

    def select(self, *columns: str) -> "Query":
        self._select.extend(columns)
        return self

    def from_table(self, table: str) -> "Query":
        self._from = table
        return self

    def where(self, condition: str) -> "Query":
        self._where.append(condition)
        return self

    def order_by(self, *columns: str) -> "Query":
        self._order_by.extend(columns)
        return self

    def limit(self, n: int) -> "Query":
        self._limit = n
        return self

    def build(self) -> str:
        if not self._select or not self._from:
            raise ValueError("select 和 from 为必填项")
        sql = f"SELECT {', '.join(self._select)} FROM {self._from}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        return sql + ";"


# ============================================================
# 结构型模式
# ============================================================

# --- 适配器 (Adapter) ---
class OldPaymentSystem:
    """旧系统接口 — 不兼容。"""

    def pay_in_cents(self, amount_cents: int, card_number: str) -> bool:
        print(f"  [OldSystem] 支付 {amount_cents} 分, 卡号={card_number[-4:]:*>16}")
        return True


class PaymentGateway(Protocol):
    """新系统期望的接口。"""

    def process_payment(self, amount_dollars: float, token: str) -> bool:
        ...


class PaymentAdapter:
    """适配器 — 让 OldPaymentSystem 满足 PaymentGateway 协议。"""

    def __init__(self, old_system: OldPaymentSystem) -> None:
        self._old = old_system

    def process_payment(self, amount_dollars: float, token: str) -> bool:
        cents = int(amount_dollars * 100)
        return self._old.pay_in_cents(cents, token)


# --- 代理 (Proxy) ---
class Image(ABC):
    @abstractmethod
    def display(self) -> str: ...


class RealImage(Image):
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        print(f"  [RealImage] 从磁盘加载: {self._filename}")

    def display(self) -> str:
        return f"显示图片: {self._filename}"


class LazyImageProxy(Image):
    """延迟加载代理 — 只在首次 display() 时加载。"""

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._real_image: RealImage | None = None

    def display(self) -> str:
        if self._real_image is None:
            self._real_image = RealImage(self._filename)
        return self._real_image.display()


class AccessControlProxy(Image):
    """访问控制代理 — 检查权限。"""

    def __init__(self, image: Image, allowed_roles: list[str]) -> None:
        self._image = image
        self._allowed = set(allowed_roles)

    def display(self, user_role: str = "guest") -> str:
        if user_role not in self._allowed:
            return f"拒绝访问: 角色 '{user_role}' 无权查看"
        return self._image.display()


# --- 外观 (Facade) ---
class VideoDecoder:
    def decode(self, path: str) -> bytes:
        return b"decoded_frames"


class AudioDecoder:
    def decode(self, path: str) -> bytes:
        return b"decoded_audio"


class FrameRenderer:
    def render(self, frames: bytes) -> None:
        pass


class MediaPlayer:
    """外观 — 统一接口封装子系统。"""

    def __init__(self) -> None:
        self._video = VideoDecoder()
        self._audio = AudioDecoder()
        self._renderer = FrameRenderer()

    def play(self, filepath: str) -> None:
        print(f"  [MediaPlayer] 播放 {filepath}")
        video_data = self._video.decode(filepath)
        audio_data = self._audio.decode(filepath)
        self._renderer.render(video_data)
        print(f"  视频: {len(video_data)} bytes, 音频: {len(audio_data)} bytes")


# ============================================================
# 行为型模式
# ============================================================

# --- 观察者 (Observer) ---
class Observer(ABC):
    @abstractmethod
    def update(self, subject: "Subject", event: str, data: Any) -> None:
        ...


class Subject:
    def __init__(self) -> None:
        self._observers: weakref.WeakSet[Observer] = weakref.WeakSet()

    def attach(self, observer: Observer) -> None:
        self._observers.add(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.discard(observer)

    def notify(self, event: str, data: Any = None) -> None:
        for observer in list(self._observers):
            observer.update(self, event, data)


class StockPrice(Subject):
    """股票价格 — 被观察者。"""

    def __init__(self, symbol: str, price: float) -> None:
        super().__init__()
        self.symbol = symbol
        self._price = price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, new_price: float) -> None:
        old = self._price
        self._price = new_price
        self.notify("price_changed", {"old": old, "new": new_price})


class StockLogger(Observer):
    def update(self, subject: Subject, event: str, data: Any) -> None:
        if event == "price_changed":
            s = subject  # type: ignore[assignment]
            print(f"  [Logger] {s.symbol}: {data['old']:.2f} -> {data['new']:.2f}")


class StockAlert(Observer):
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def update(self, subject: Subject, event: str, data: Any) -> None:
        if event == "price_changed" and data["new"] > self.threshold:
            s = subject  # type: ignore[assignment]
            print(f"  [Alert] {s.symbol} 突破 {self.threshold}: 当前 {data['new']:.2f}")


# --- 策略 (Strategy) ---
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list[int]) -> list[int]: ...


class QuickSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        return sorted(data)                      # 内置 Timsort 作为快速排序的代表


class BubbleSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        arr = data[:]
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class MergeSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)

    def _merge(self, left: list[int], right: list[int]) -> list[int]:
        result: list[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


class Sorter:
    def __init__(self, strategy: SortStrategy | None = None) -> None:
        self._strategy = strategy or QuickSort()

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def execute(self, data: list[int]) -> list[int]:
        return self._strategy.sort(data)


# --- 命令 (Command) ---
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class TextEditor:
    def __init__(self) -> None:
        self.text: str = ""
        self.cursor: int = 0

    def insert(self, text: str) -> None:
        self.text = self.text[:self.cursor] + text + self.text[self.cursor:]
        self.cursor += len(text)

    def delete(self, length: int) -> str:
        deleted = self.text[self.cursor:self.cursor + length]
        self.text = self.text[:self.cursor] + self.text[self.cursor + length:]
        return deleted


class InsertCommand(Command):
    def __init__(self, editor: TextEditor, text: str) -> None:
        self.editor = editor
        self.text = text

    def execute(self) -> None:
        self.editor.insert(self.text)

    def undo(self) -> None:
        self.editor.cursor -= len(self.text)
        self.editor.delete(len(self.text))


class CommandHistory:
    def __init__(self) -> None:
        self._history: list[Command] = []
        self._index: int = -1

    def execute(self, cmd: Command) -> None:
        self._history = self._history[:self._index + 1]
        self._history.append(cmd)
        cmd.execute()
        self._index += 1

    def undo(self) -> bool:
        if self._index >= 0:
            self._history[self._index].undo()
            self._index -= 1
            return True
        return False

    def redo(self) -> bool:
        if self._index + 1 < len(self._history):
            self._index += 1
            self._history[self._index].execute()
            return True
        return False


# --- 状态 (State) ---
class OrderState(ABC):
    @abstractmethod
    def pay(self, order: "Order") -> str: ...

    @abstractmethod
    def ship(self, order: "Order") -> str: ...

    @abstractmethod
    def cancel(self, order: "Order") -> str: ...


class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        self.state: OrderState = PendingState()

    def pay(self) -> str:
        return self.state.pay(self)

    def ship(self) -> str:
        return self.state.ship(self)

    def cancel(self) -> str:
        return self.state.cancel(self)


class PendingState(OrderState):
    def pay(self, order: Order) -> str:
        order.state = PaidState()
        return f"订单 {order.order_id}: 待支付 -> 已支付"

    def ship(self, order: Order) -> str:
        return f"订单 {order.order_id}: 未支付，无法发货"

    def cancel(self, order: Order) -> str:
        order.state = CancelledState()
        return f"订单 {order.order_id}: 待支付 -> 已取消"


class PaidState(OrderState):
    def pay(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已支付，无需重复支付"

    def ship(self, order: Order) -> str:
        order.state = ShippedState()
        return f"订单 {order.order_id}: 已支付 -> 已发货"

    def cancel(self, order: Order) -> str:
        order.state = CancelledState()
        return f"订单 {order.order_id}: 已支付 -> 已取消 (将退款)"


class ShippedState(OrderState):
    def pay(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已发货，无法再支付"

    def ship(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已发货，无需重复发货"

    def cancel(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已发货，无法取消"


class CancelledState(OrderState):
    def pay(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已取消，无法支付"

    def ship(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已取消，无法发货"

    def cancel(self, order: Order) -> str:
        return f"订单 {order.order_id}: 已取消"


# --- 责任链 (Chain of Responsibility) ---
class Handler(ABC):
    def __init__(self) -> None:
        self._next: Handler | None = None

    def set_next(self, handler: Handler) -> Handler:
        self._next = handler
        return handler

    @abstractmethod
    def handle(self, request: dict[str, Any]) -> str | None:
        if self._next:
            return self._next.handle(request)
        return None


class AuthHandler(Handler):
    def handle(self, request: dict[str, Any]) -> str | None:
        if not request.get("authenticated"):
            return "AuthHandler: 认证失败"
        print("  AuthHandler: 认证通过")
        return super().handle(request)


class RateLimitHandler(Handler):
    def __init__(self, max_requests: int = 5) -> None:
        super().__init__()
        self._counts: dict[str, int] = defaultdict(int)
        self._max = max_requests

    def handle(self, request: dict[str, Any]) -> str | None:
        user = request.get("user", "unknown")
        self._counts[user] += 1
        if self._counts[user] > self._max:
            return f"RateLimitHandler: {user} 超出频率限制"
        print(f"  RateLimitHandler: {user} 请求 {self._counts[user]}/{self._max}")
        return super().handle(request)


class BusinessLogicHandler(Handler):
    def handle(self, request: dict[str, Any]) -> str | None:
        action = request.get("action", "unknown")
        result = f"BusinessLogicHandler: 执行 {action} — 成功"
        print(f"  {result}")
        return result


# ============================================================
# 演示入口
# ============================================================

def demo_creational() -> None:
    print("=" * 60)
    print("创建型模式")
    print("=" * 60)

    # 单例
    cfg1 = AppConfig()
    cfg2 = AppConfig()
    cfg1.set("theme", "dark")
    print(f"单例: cfg1 is cfg2 = {cfg1 is cfg2}, theme={cfg2.get('theme')}")

    # Borg
    b1 = BorgPattern()
    b2 = BorgPattern()
    b1.shared_value = 42
    print(f"Borg: b2.shared_value = {b2.shared_value}")

    # 工厂
    factory = DocumentFactory()
    for t in ["pdf", "word", "md"]:
        doc = factory.create(t)
        print(f"Factory({t}): {doc.render()}")

    # 抽象工厂
    for gui_factory in [WindowsFactory(), MacFactory()]:
        btn = gui_factory.create_button()
        chk = gui_factory.create_checkbox()
        print(f"GUI: {btn.render()} + {chk.render()}")

    # 建造者
    sql = (Query()
           .select("id", "name", "email")
           .from_table("users")
           .where("age > 18")
           .where("active = true")
           .order_by("name", "id DESC")
           .limit(10)
           .build())
    print(f"Builder SQL:\n  {sql}")


def demo_structural() -> None:
    print("\n" + "=" * 60)
    print("结构型模式")
    print("=" * 60)

    # 适配器
    old = OldPaymentSystem()
    adapter = PaymentAdapter(old)
    result = adapter.process_payment(49.99, "4111-1111-1111-1111")
    print(f"Adapter: 支付结果={result}")

    # 代理
    print("延迟代理:")
    lazy_img = LazyImageProxy("photo.jpg")
    print("  未加载...")
    print(f"  {lazy_img.display()}")
    print(f"  {lazy_img.display()}  (第2次—直接从缓存)")

    print("访问控制代理:")
    real = RealImage("secret.png")
    acl = AccessControlProxy(real, ["admin", "superuser"])
    print(f"  {acl.display('guest')}")
    print(f"  {acl.display('admin')}")

    # 外观
    player = MediaPlayer()
    player.play("movie.mp4")


def demo_behavioral() -> None:
    print("\n" + "=" * 60)
    print("行为型模式")
    print("=" * 60)

    # 观察者
    print("--- 观察者 ---")
    stock = StockPrice("AAPL", 150.0)
    logger = StockLogger()
    alert = StockAlert(160.0)
    stock.attach(logger)
    stock.attach(alert)
    stock.price = 155.0
    stock.price = 162.0

    # 策略
    print("\n--- 策略 ---")
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    sorter = Sorter()
    print(f"QuickSort:  {sorter.execute(data)}")
    sorter.set_strategy(BubbleSort())
    print(f"BubbleSort: {sorter.execute(data)}")
    sorter.set_strategy(MergeSort())
    print(f"MergeSort:  {sorter.execute(data)}")

    # 命令
    print("\n--- 命令 ---")
    editor = TextEditor()
    history = CommandHistory()
    history.execute(InsertCommand(editor, "Hello"))
    history.execute(InsertCommand(editor, " World"))
    print(f"编辑器内容: '{editor.text}'")
    history.undo()
    print(f"撤销后:     '{editor.text}'")
    history.redo()
    print(f"重做后:     '{editor.text}'")

    # 状态
    print("\n--- 状态 ---")
    order = Order("ORD-001")
    print(order.pay())
    print(order.pay())                           # 重复支付
    print(order.ship())
    print(order.cancel())                        # 已发货无法取消

    # 责任链
    print("\n--- 责任链 ---")
    auth = AuthHandler()
    rate = RateLimitHandler(max_requests=3)
    biz = BusinessLogicHandler()
    auth.set_next(rate).set_next(biz)

    req1 = {"authenticated": True, "user": "alice", "action": "get_report"}
    req2 = {"authenticated": False, "user": "bob", "action": "delete_all"}
    req3 = {"authenticated": True, "user": "alice", "action": "check_status"}

    for i, req in enumerate([req1, req2, req3], 1):
        print(f"\n请求 {i}: {req}")
        result = auth.handle(req)
        if result:
            print(f"  最终结果: {result}")

    # alice 超过限频
    for i in range(3):
        auth.handle({"authenticated": True, "user": "alice",
                     "action": f"action_{i}"})
    result = auth.handle({"authenticated": True, "user": "alice",
                          "action": "exceeded"})
    print(f"\n限频测试: {result}")


if __name__ == "__main__":
    demo_creational()
    demo_structural()
    demo_behavioral()
    print("\n✅ 设计模式篇全部执行完毕!")
