#!/usr/bin/env python3
"""
Python 中级 —— 函数进阶
涵盖：闭包深入、装饰器（含参数化装饰器）、LRU 缓存、singledispatch、偏函数
"""

import functools
import time
import math
import random
from functools import (
    wraps,
    lru_cache,
    cached_property,
    partial,
    reduce,
    singledispatch,
    total_ordering,
)
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


# ============================================================
# §1  闭包与自由变量深入
# ============================================================

def make_multiplier(factor: float) -> Callable[[float], float]:
    """典型的闭包：内部函数捕获 factor。"""

    def multiply(x: float) -> float:
        # factor 是自由变量 (free variable)
        return x * factor

    return multiply


def make_averager() -> Callable[[float], float]:
    """闭包的另一个经典例子：移动平均器（可变外部变量）。"""
    history: list[float] = []

    def averager(new_value: float) -> float:
        history.append(new_value)
        return sum(history) / len(history)

    return averager


def make_averager_nonlocal() -> Callable[[float], float]:
    """使用 nonlocal 避免 list 的间接引用。"""
    total: float = 0.0
    count: int = 0

    def averager(new_value: float) -> float:
        nonlocal total, count
        total += new_value
        count += 1
        return total / count

    return averager


def demo_closures() -> None:
    print("=" * 60)
    print("§1  闭包深入")
    print("=" * 60)

    double = make_multiplier(2)
    triple = make_multiplier(3)
    print(f"double(10) = {double(10)}, triple(10) = {triple(10)}")

    # 查看自由变量
    print(f"double.__closure__[0].cell_contents = {double.__closure__[0].cell_contents}")  # type: ignore[union-attr]

    avg = make_averager()
    for v in [10, 20, 30]:
        print(f"  average after {v} = {avg(v)}")

    avg2 = make_averager_nonlocal()
    for v in [100, 200, 300]:
        print(f"  average (nonlocal) after {v} = {avg2(v)}")


# ============================================================
# §2  装饰器基础
# ============================================================

def timer(func: Callable[P, R]) -> Callable[P, R]:
    """记录函数执行时间的装饰器。"""

    @wraps(func)                               # 保留原函数的 __name__ / __doc__ 等元数据
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [timer] {func.__name__} 耗时 {elapsed*1000:.3f} ms")
        return result

    return wrapper


def retry(max_attempts: int = 3, delay: float = 0.5,
          exceptions: tuple[type[BaseException], ...] = (Exception,)):
    """参数化装饰器：自动重试。"""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: BaseException | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"  [retry] {func.__name__} 第 {attempt} 次失败: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise RuntimeError(f"{func.__name__} 重试 {max_attempts} 次后仍失败") from last_exc
        return wrapper
    return decorator


def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    """记录每次调用的参数和返回值。"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        arg_repr = ", ".join(
            [repr(a) for a in args] +
            [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        result = func(*args, **kwargs)
        print(f"  [log] {func.__name__}({arg_repr}) -> {result!r}")
        return result

    return wrapper


# 组合装饰器（从下往上执行）
@timer
@log_calls
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """带缓存的斐波那契，外加 log + timer 装饰器。"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# 使用参数化装饰器
@retry(max_attempts=3, delay=0.1, exceptions=(ValueError, ConnectionError))
def flaky_remote_call() -> str:
    """模拟不稳定的远程调用。"""
    if random.random() < 0.6:
        raise ConnectionError("网络超时")
    return "OK"


def demo_decorators() -> None:
    print("\n" + "=" * 60)
    print("§2  装饰器基础")
    print("=" * 60)

    print(f"fibonacci(30) = {fibonacci(30)}")
    print(f"缓存信息: {fibonacci.cache_info()}")  # type: ignore[attr-defined]

    # 测试重试
    print("\n重试装饰器测试 (随机失败):")
    for _ in range(3):
        try:
            result = flaky_remote_call()
            print(f"  -> {result}")
        except RuntimeError as e:
            print(f"  -> {e}")


# ============================================================
# §3  装饰器进阶
# ============================================================

# 类装饰器
class CountCalls:
    """类作为装饰器：统计函数被调用的次数。"""

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.num_calls: int = 0
        wraps(func)(self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        self.num_calls += 1
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<CountCalls:{self.func.__name__}, called={self.num_calls}>"


@CountCalls
def greet(name: str) -> str:
    return f"Hello, {name}!"


# singledispatch — 函数重载（基于第一个参数的类型）
@singledispatch
def to_json(obj: Any) -> str:
    """默认回退：repr。"""
    return repr(obj)


@to_json.register(int)
def _(obj: int) -> str:
    return str(obj)


@to_json.register(float)
def _(obj: float) -> str:
    return f"{obj:.2f}"


@to_json.register(list)
def _(obj: list[Any]) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


@to_json.register(dict)
def _(obj: dict[str, Any]) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False, indent=2)


def demo_advanced_decorators() -> None:
    print("\n" + "=" * 60)
    print("§3  装饰器进阶")
    print("=" * 60)

    # 类装饰器
    for name in ["Alice", "Bob", "Charlie"]:
        greet(name)
    print(f"greet called {greet.num_calls} times")  # type: ignore[attr-defined]

    # singledispatch
    print(f"to_json(42)          -> {to_json(42)}")
    print(f"to_json(3.14159)     -> {to_json(3.14159)}")
    print(f"to_json([1,2,3])     -> {to_json([1, 2, 3])}")
    print(f"to_json({{'a':1}})   -> {to_json({'a': 1})}")
    print(f"to_json({{1,2,3}})   -> {to_json({1, 2, 3})}")


# ============================================================
# §4  LRU Cache 与缓存策略
# ============================================================

@lru_cache(maxsize=256)
def slow_factorial(n: int) -> int:
    """模拟耗时计算的阶乘（用 LRU 加速）。"""
    time.sleep(0.001)
    return math.factorial(n)


class CachedDataService:
    """使用 cached_property 延迟计算并缓存属性。"""

    def __init__(self, dataset: list[int]) -> None:
        self.dataset = dataset

    @cached_property
    def mean(self) -> float:
        print("  计算 mean...")
        return sum(self.dataset) / len(self.dataset)

    @cached_property
    def stddev(self) -> float:
        print("  计算 stddev...")
        m = self.mean
        variance = sum((x - m) ** 2 for x in self.dataset) / len(self.dataset)
        return math.sqrt(variance)

    @cached_property
    def sorted_unique(self) -> list[int]:
        print("  计算 sorted_unique...")
        return sorted(set(self.dataset))


def demo_caching() -> None:
    print("\n" + "=" * 60)
    print("§4  缓存策略")
    print("=" * 60)

    # lru_cache
    t0 = time.perf_counter()
    for _ in range(5):
        slow_factorial(500)                      # 只有第 1 次真正计算
    elapsed = time.perf_counter() - t0
    info = slow_factorial.cache_info()
    print(f"LRU factorial(500) x5: {elapsed*1e3:.1f}ms, hits={info.hits}, misses={info.misses}")
    slow_factorial.cache_clear()

    # cached_property
    svc = CachedDataService([1, 2, 3, 4, 5, 5, 4, 3, 2, 1])
    print(f"mean (第1次访问): {svc.mean}")
    print(f"mean (第2次访问): {svc.mean}  (已缓存)")
    print(f"stddev: {svc.stddev}")
    print(f"sorted_unique: {svc.sorted_unique}")


# ============================================================
# §5  partial — 偏函数
# ============================================================

def power(base: float, exp: float) -> float:
    return base ** exp


def build_url(protocol: str, host: str, port: int, path: str) -> str:
    return f"{protocol}://{host}:{port}{path}"


def demo_partial() -> None:
    print("\n" + "=" * 60)
    print("§5  partial — 偏函数")
    print("=" * 60)

    # 冻结部分参数
    square = partial(power, exp=2)
    cube = partial(power, exp=3)
    http_localhost = partial(build_url, "http", "localhost", port=8080)

    print(f"square(5) = {square(5)}")
    print(f"cube(5)   = {cube(5)}")
    print(f"http_localhost('/api') = {http_localhost('/api')}")

    # 与 functools.reduce 配合
    product = partial(reduce, lambda a, b: a * b)
    print(f"product([1..5]) = {product([1, 2, 3, 4, 5])}")


# ============================================================
# §6  lambda / map / filter / reduce / sorted 实战
# ============================================================

def demo_lambda_and_friends() -> None:
    print("\n" + "=" * 60)
    print("§6  lambda / map / filter / reduce / sorted 实战")
    print("=" * 60)

    # 排序综合：按多个键
    students = [
        {"name": "Alice", "score": 90, "age": 20},
        {"name": "Bob", "score": 85, "age": 21},
        {"name": "Charlie", "score": 90, "age": 19},
        {"name": "Diana", "score": 78, "age": 22},
    ]
    # 按 score 降序，同分按 age 升序
    ranked = sorted(students, key=lambda s: (-s["score"], s["age"]))
    print("排序结果:")
    for s in ranked:
        print(f"  {s['name']}: score={s['score']}, age={s['age']}")

    # map + filter + reduce 链
    nums = list(range(1, 21))
    chain_result = reduce(
        lambda a, b: a + b,
        map(lambda x: x**2, filter(lambda x: x % 2 == 0, nums)),
    )
    # 等价于: sum(x**2 for x in nums if x % 2 == 0)
    print(f"sum of squares of evens 1-20: {chain_result}")


# ============================================================
# §7  单分派泛函数——Method Overloading
# ============================================================

# 已在 §3 的 singledispatch 中演示，这里补充更复杂的用例

class HTMLNode:
    pass


class TextNode(HTMLNode):
    def __init__(self, text: str) -> None:
        self.text = text


class ElementNode(HTMLNode):
    def __init__(self, tag: str, children: list[HTMLNode]) -> None:
        self.tag = tag
        self.children = children


@singledispatch
def render_html(node: HTMLNode) -> str:
    raise TypeError(f"Unknown node type: {type(node)}")


@render_html.register
def _(node: TextNode) -> str:
    from html import escape
    return escape(node.text)


@render_html.register
def _(node: ElementNode) -> str:
    children_html = "".join(render_html(child) for child in node.children)
    return f"<{node.tag}>{children_html}</{node.tag}>"


def demo_single_dispatch_html() -> None:
    print("\n" + "=" * 60)
    print("§7  singledispatch — HTML 渲染器")
    print("=" * 60)

    page = ElementNode("div", [
        ElementNode("h1", [TextNode("Hello World")]),
        ElementNode("p", [TextNode("This is a <b>paragraph</b>.")]),
    ])
    print(f"HTML: {render_html(page)}")


# ============================================================
# §8  函数式编程综合练习
# ============================================================

def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """函数组合：compose(f, g, h)(x) = f(g(h(x)))。"""
    if not functions:
        return lambda x: x
    def composed(x: Any) -> Any:
        result = x
        for f in reversed(functions):
            result = f(result)
        return result
    return composed


def pipe(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """管道：pipe(f, g, h)(x) = h(g(f(x)))。"""
    if not functions:
        return lambda x: x
    def piped(x: Any) -> Any:
        result = x
        for f in functions:
            result = f(result)
        return result
    return piped


def demo_functional_composition() -> None:
    print("\n" + "=" * 60)
    print("§8  函数组合 & 管道")
    print("=" * 60)

    # compose(f, g) -> f(g(x))
    process = compose(
        lambda s: s + "!",
        lambda s: s.upper(),
        lambda s: s.strip(),
    )
    print(f"compose: {process('  hello world  ')}")

    # pipe(f, g) -> g(f(x))
    transform = pipe(
        lambda n: n * 2,
        lambda n: n + 10,
        lambda n: f"result={n}",
    )
    print(f"pipe: {transform(5)}")

    # 偏函数 + 组合
    add = lambda a: lambda b: a + b
    mul = lambda a: lambda b: a * b
    add_10 = add(10)
    mul_3 = mul(3)
    composed_math = compose(mul_3, add_10)
    print(f"compose(mul(3), add(10))(5) = {composed_math(5)}  (=(5+10)*3)")


if __name__ == "__main__":
    demo_closures()
    demo_decorators()
    demo_advanced_decorators()
    demo_caching()
    demo_partial()
    demo_lambda_and_friends()
    demo_single_dispatch_html()
    demo_functional_composition()
    print("\n✅ 函数进阶篇全部执行完毕!")
