#!/usr/bin/env python3
"""
Python 中级 —— 迭代器、生成器、上下文管理器、异常处理、日志
涵盖：迭代器协议、生成器函数/表达式、yield from、async 生成器基本概念、
      __enter__/__exit__、contextlib、异常链、日志模块配置
"""

import contextlib
import logging
import sys
import time
import traceback
from collections.abc import Iterable, Iterator, Generator
from typing import Any


# ============================================================
# §1  迭代器协议
# ============================================================

class CountDown:
    """可迭代对象 + 迭代器（合二为一）。"""

    def __init__(self, start: int, step: int = 1) -> None:
        self.current = start
        self.step = step

    def __iter__(self) -> "CountDown":
        """返回自身作为迭代器。"""
        return self

    def __next__(self) -> int:
        if self.current < 0:
            raise StopIteration
        result = self.current
        self.current -= self.step
        return result


class FibIterator:
    """斐波那契迭代器：无限迭代。"""

    def __init__(self, max_count: int | None = None) -> None:
        self.a, self.b = 0, 1
        self.count = 0
        self.max_count = max_count

    def __iter__(self) -> "FibIterator":
        return self

    def __next__(self) -> int:
        if self.max_count is not None and self.count >= self.max_count:
            raise StopIteration
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return result


class Sentence:
    """将迭代逻辑分离到独立迭代器类的可迭代对象。"""

    def __init__(self, text: str) -> None:
        self.words = text.split()

    def __iter__(self) -> Iterator[str]:
        return SentenceIterator(self.words)

    def __repr__(self) -> str:
        return f"Sentence({self.words!r})"


class SentenceIterator:
    def __init__(self, words: list[str]) -> None:
        self._words = words
        self._index = 0

    def __iter__(self) -> "SentenceIterator":
        return self

    def __next__(self) -> str:
        if self._index >= len(self._words):
            raise StopIteration
        word = self._words[self._index]
        self._index += 1
        return word


def demo_iterators() -> None:
    print("=" * 60)
    print("§1  迭代器协议")
    print("=" * 60)

    cd = CountDown(5)
    print("CountDown(5):", list(cd))

    fib = FibIterator(10)
    print("Fibonacci 前 10:", list(fib))

    sent = Sentence("The quick brown fox jumps")
    print("Sentence 迭代: ", end="")
    for word in sent:
        print(word, end=" | ")
    print()

    # iter() 内置函数 + 哨兵
    import random
    random_ints = iter(lambda: random.randint(1, 6), 6)  # 遇到 6 停止
    print("iter(sentinel=6):", list(random_ints))


# ============================================================
# §2  生成器函数
# ============================================================

def fibonacci_gen(limit: int) -> Generator[int, None, None]:
    """生成器函数版本，惰性生成斐波那契数。"""
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b


def read_lines(filename: str) -> Generator[str, None, None]:
    """逐行读取大文件的生成器（内存友好）。"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                yield line.rstrip("\n")
    except FileNotFoundError:
        yield f"[ERROR] 文件不存在: {filename}"


def tree_walk(root: dict[str, Any] | list[Any] | Any) -> Generator[Any, None, None]:
    """递归遍历嵌套字典/列表，产出所有叶子节点。"""
    if isinstance(root, dict):
        for v in root.values():
            yield from tree_walk(v)
    elif isinstance(root, list):
        for item in root:
            yield from tree_walk(item)
    else:
        yield root


# 生成器表达式（惰性列表推导）
def demo_generators() -> None:
    print("\n" + "=" * 60)
    print("§2  生成器函数")
    print("=" * 60)

    gen = fibonacci_gen(10)
    print(f"fibonacci_gen(10): {gen}, list(gen) = {list(gen)}")
    # 生成器只能消费一次
    print(f"再次消费已空的生成器: {list(gen)}")

    # yield from 示例
    nested = {
        "a": [1, 2],
        "b": {"c": 3, "d": [4, 5]},
        "e": 6,
    }
    leaves = list(tree_walk(nested))
    print(f"tree_walk 叶子: {leaves}")

    # 生成器表达式
    squares_gen = (x**2 for x in range(10) if x % 2 == 0)
    print(f"生成器表达式: {squares_gen}, sum = {sum(squares_gen)}")

    # 生成器表达式作为函数实参（省略括号）
    total = sum(x**2 for x in range(10))
    print(f"sum(x**2 for x in range(10)) = {total}")


# ============================================================
# §3  send / throw / close — 双向通信
# ============================================================

def accumulator(initial: float = 0.0) -> Generator[float, float, float]:
    """
    协程风格的生成器：
    - 通过 send() 发送值累加
    - 通过 throw() 抛入异常
    - 最终返回累加总和
    """
    total = initial
    count = 0
    try:
        while True:
            value = yield total
            if value is None:
                continue
            total += value
            count += 1
    finally:
        print(f"  [accumulator] 清理: count={count}")

    return total


def demo_generator_advanced() -> None:
    print("\n" + "=" * 60)
    print("§3  send / throw / close")
    print("=" * 60)

    acc = accumulator()
    # 1) 启动生成器（预激）
    current = next(acc)
    print(f"初始值: {current}")

    # 2) send — 向生成器发送值
    current = acc.send(10)
    print(f"send(10) -> total = {current}")
    current = acc.send(25)
    print(f"send(25) -> total = {current}")

    # 3) throw — 向生成器抛入异常
    try:
        acc.throw(ValueError, "模拟异常")
    except ValueError as e:
        print(f"生成器内部捕获异常: {e}")

    # 4) close — 关闭生成器
    acc.close()
    print("生成器已关闭")

    # yield from + 返回值捕获
    def inner() -> Generator[int, None, str]:
        yield 1
        yield 2
        return "done"

    def outer() -> Generator[int, None, str]:
        result = yield from inner()
        print(f"  inner 返回: {result}")
        return "outer " + result

    print("yield from 返回值: ", end="")
    g = outer()
    yielded = list(g)
    print(f"产出的值: {yielded}")


# ============================================================
# §4  上下文管理器
# ============================================================

class FileManager:
    """__enter__ / __exit__ 手写上下文管理器。"""

    def __init__(self, filename: str, mode: str = "r") -> None:
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode, encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.file:
            self.file.close()
        if exc_type is OSError:
            print(f"  [FileManager] 抑制 OSError: {exc_val}")
            return True                          # 抑制异常
        return False


class Timer:
    """性能计时的上下文管理器（可复用）。"""

    def __init__(self, label: str = "Elapsed") -> None:
        self.label = label

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> bool:
        self.end = time.perf_counter()
        print(f"  [Timer] {self.label}: {(self.end - self.start)*1000:.2f} ms")
        return False


class Transaction:
    """模拟数据库事务：失败时自动回滚。"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.committed = False

    def __enter__(self) -> "Transaction":
        print(f"  [Tx] BEGIN {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self.committed = True
            print(f"  [Tx] COMMIT {self.name}")
        else:
            print(f"  [Tx] ROLLBACK {self.name} due to {exc_type.__name__}")
        return False                             # 异常继续传播


def demo_context_managers() -> None:
    print("\n" + "=" * 60)
    print("§4  上下文管理器")
    print("=" * 60)

    # Timer
    with Timer("sleep 0.1s"):
        time.sleep(0.1)

    # Transaction (成功)
    with Transaction("transfer"):
        print("    执行转账...")

    # Transaction (失败)
    with contextlib.suppress(ValueError):
        with Transaction("failing"):
            print("    执行失败操作...")
            raise ValueError("余额不足")

    # 嵌套上下文管理器
    with Timer("嵌套") as t, contextlib.redirect_stdout(None):
        # 被重定向到 None 的输出
        print("这条不会被看到")
    print("redirect_stdout 之后")


# ============================================================
# §5  contextlib 模块
# ============================================================

@contextlib.contextmanager
def temporary_attribute(obj: Any, attr: str, temp_value: Any) -> Generator[None, None, None]:
    """临时修改对象属性，退出时恢复。"""
    original = getattr(obj, attr, contextlib._UNDEFINED_SENTINEL)
    setattr(obj, attr, temp_value)
    try:
        yield
    finally:
        if original is contextlib._UNDEFINED_SENTINEL:
            delattr(obj, attr)
        else:
            setattr(obj, attr, original)


@contextlib.contextmanager
def open_and_print(filename: str) -> Generator[Any, None, None]:
    """contextlib 装饰器版上下文管理器。"""
    f = open(filename, "r", encoding="utf-8")
    try:
        print(f"  [open_and_print] 打开 {filename}")
        yield f
    finally:
        f.close()
        print(f"  [open_and_print] 关闭 {filename}")


@contextlib.contextmanager
def suppress_log(level: int = logging.WARNING) -> Generator[None, None, None]:
    """临时提高日志级别来抑制低级别日志。"""
    logging.disable(level - 10)
    try:
        yield
    finally:
        logging.disable(logging.NOTSET)


def demo_contextlib() -> None:
    print("\n" + "=" * 60)
    print("§5  contextlib 模块")
    print("=" * 60)

    # temporary_attribute
    class Config:
        debug = False

    cfg = Config()
    print(f"before: cfg.debug = {cfg.debug}")
    with temporary_attribute(cfg, "debug", True):
        print(f"  inside: cfg.debug = {cfg.debug}")
    print(f"after:  cfg.debug = {cfg.debug}")

    # ExitStack — 动态管理多个上下文
    with contextlib.ExitStack() as stack:
        files = []
        for i in range(3):
            # 模拟打开多个资源
            timer = stack.enter_context(Timer(f"resource_{i}"))
            time.sleep(0.02)
        print("  ExitStack 管理 3 个资源完成")

    # nullcontext — 条件性上下文
    use_cm = False
    cm = Timer("conditional") if use_cm else contextlib.nullcontext()
    with cm:
        pass
    print("nullcontext 完成（无操作）")


# ============================================================
# §6  异常处理深入
# ============================================================

class AppError(Exception):
    """应用自定义异常基类。"""
    def __init__(self, message: str, code: int = 500) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ValidationError(AppError):
    """数据验证失败。"""
    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"字段 '{field}' 验证失败: {reason}", code=400)
        self.field = field


class ResourceNotFound(AppError):
    """资源未找到。"""
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(f"{resource} '{identifier}' 不存在", code=404)
        self.resource = resource
        self.identifier = identifier


def validate_age(age: int) -> int:
    if not isinstance(age, int):
        raise ValidationError("age", f"期望 int，收到 {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValidationError("age", f"值 {age} 不在 [0, 150] 范围内")
    return age


def fetch_user(user_id: int) -> dict[str, Any]:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    if user_id not in users:
        raise ResourceNotFound("User", str(user_id))
    return users[user_id]


def demo_exceptions() -> None:
    print("\n" + "=" * 60)
    print("§6  异常处理深入")
    print("=" * 60)

    # 常规 try/except/else/finally
    for age_input in [25, -5, "thirty", 40]:
        try:
            validated = validate_age(age_input)  # type: ignore[arg-type]
        except ValidationError as e:
            print(f"  [{e.code}] {e.message}")
        else:
            print(f"  验证通过: age={validated}")
        finally:
            pass  # 清理资源

    # 异常链 (raise ... from ...)
    try:
        try:
            fetch_user(999)
        except ResourceNotFound as e:
            raise RuntimeError("获取用户失败") from e
    except RuntimeError as e:
        print(f"\n异常链:")
        print(f"  {type(e).__name__}: {e}")
        if e.__cause__:
            print(f"  原始异常: {type(e.__cause__).__name__}: {e.__cause__}")

    # 异常组 (Python 3.11+ ExceptionGroup)
    try:
        errors: list[AppError] = []
        for uid in [3, 4, 5]:
            try:
                fetch_user(uid)
            except ResourceNotFound as e:
                errors.append(e)
        if errors:
            raise ExceptionGroup("批量获取用户失败", errors)
    except* ResourceNotFound as eg:
        print(f"\nExceptionGroup 捕获到 {len(eg.exceptions)} 个 ResourceNotFound")
    except* AppError as eg:
        print(f"ExceptionGroup 捕获到 {len(eg.exceptions)} 个 AppError")


# ============================================================
# §7  日志配置
# ============================================================

def setup_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """配置一个带文件和控制台双 handler 的 logger。"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # 格式
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 控制台 Handler（INFO 以上）
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        # 文件 Handler（DEBUG 以上）
        file_handler = logging.FileHandler("app.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(file_handler)

    return logger


def demo_logging() -> None:
    print("\n" + "=" * 60)
    print("§7  日志配置")
    print("=" * 60)

    log = setup_logger("demo")

    log.debug("调试信息 — 仅出现在文件中")
    log.info("普通信息")
    log.warning("警告信息")
    log.error("错误信息")
    log.critical("严重错误")

    # 带异常栈的日志
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("捕获到一个除零异常")

    print("(日志已同时写入 app.log)")


# ============================================================
# §8  itertools 精选
# ============================================================

def demo_itertools() -> None:
    print("\n" + "=" * 60)
    print("§8  itertools 精选")
    print("=" * 60)

    import itertools

    # count / cycle / repeat (无限迭代器)
    print("islice(count(10,2), 5):", list(itertools.islice(itertools.count(10, 2), 5)))
    print("islice(cycle('AB'), 6):", list(itertools.islice(itertools.cycle("AB"), 6)))
    print("repeat('X', 3):", list(itertools.repeat("X", 3)))

    # accumulate
    data = [1, 2, 3, 4, 5]
    print(f"accumulate({data}):", list(itertools.accumulate(data)))
    print(f"accumulate(*, operator.mul):", list(itertools.accumulate(data, lambda a, b: a * b)))

    # chain
    print(f"chain([1,2],[3,4],[5]):", list(itertools.chain([1, 2], [3, 4], [5])))

    # pairwise (Python 3.10+)
    print(f"pairwise({data}):", list(itertools.pairwise(data)))

    # combinations / permutations / product
    items = "ABC"
    print(f"combinations({items!r}, 2):", list(itertools.combinations(items, 2)))
    print(f"permutations({items!r}, 2):", list(itertools.permutations(items, 2)))
    print(f"product('AB', '12'):", list(itertools.product("AB", "12")))

    # groupby (需先按 key 排序)
    logs = sorted(["ERROR:fail", "INFO:start", "ERROR:retry", "INFO:done"],
                  key=lambda s: s.split(":")[0])
    for level, entries in itertools.groupby(logs, key=lambda s: s.split(":")[0]):
        print(f"  {level}: {list(entries)}")


if __name__ == "__main__":
    demo_iterators()
    demo_generators()
    demo_generator_advanced()
    demo_context_managers()
    demo_contextlib()
    demo_exceptions()
    demo_logging()
    demo_itertools()
    print("\n✅ 中级进阶篇全部执行完毕!")
