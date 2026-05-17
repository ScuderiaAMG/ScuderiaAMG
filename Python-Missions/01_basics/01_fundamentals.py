#!/usr/bin/env python3
"""
Python 基础 —— 从零开始的完整学习脚本
涵盖：变量、数据类型、运算符、控制流、函数、作用域
每个小节都有可执行的代码和输出演示
"""

import math
import random
import sys
from typing import Any, Callable


# ============================================================
# §1  变量与基本数据类型
# ============================================================

def demo_variables_and_types() -> None:
    """演示变量的定义、赋值以及 Python 的基本数据类型。"""

    # --- 整数 int ---
    a: int = 42
    b: int = -7
    big: int = 2**63 - 1                     # Python 的整数没有上限（仅受内存限制）
    binary: int = 0b1010                      # 二进制字面量 = 10
    hexadecimal: int = 0xFF                   # 十六进制字面量 = 255
    octal: int = 0o777                        # 八进制字面量 = 511
    print(f"[int] a={a}, b={b}, big={big}, bin={binary}, hex={hexadecimal}, oct={octal}")

    # --- 浮点数 float ---
    pi: float = 3.141592653589793
    sci: float = 1.6e-19                      # 科学记数法
    inf: float = float("inf")                 # 正无穷
    nan: float = float("nan")                 # Not a Number
    print(f"[float] pi={pi}, sci={sci}, inf={inf}, nan={nan}, is_inf={math.isinf(inf)}, is_nan={math.isnan(nan)}")

    # --- 复数 complex ---
    c1: complex = 3 + 4j
    c2: complex = complex(1, -2)
    print(f"[complex] c1={c1}, real={c1.real}, imag={c1.imag}, abs={abs(c1)}, conj={c1.conjugate()}, add={c1 + c2}")

    # --- 字符串 str ---
    s1: str = 'hello'
    s2: str = "world"
    s3: str = """多行
    字符串"""
    raw: str = r"C:\Users\new\tab"            # raw string 忽略转义
    fstring: str = f"{s1} {s2.upper()}, 2+3={2+3}"
    print(f"[str] s1={s1!r}, s2={s2!r}, s3={s3!r}, raw={raw!r}, fstring={fstring!r}")

    # --- 布尔值 bool ---
    yes: bool = True
    no: bool = False
    # Falsy 值：None, 0, 0.0, '', [], {}, set(), ()
    print(f"[bool] yes={yes}, no={no}, 1==1 -> {1 == 1}, isinstance(True,int) -> {isinstance(True, int)}")

    # --- NoneType ---
    nothing: None = None
    print(f"[None] nothing={nothing}, is None -> {nothing is None}")


# ============================================================
# §2  运算符
# ============================================================

def demo_operators() -> None:
    """演示 Python 支持的各类运算符。"""

    # 算术运算符
    print("\n--- 算术 ---")
    print(f"7 + 3 = {7 + 3},  7 - 3 = {7 - 3},  7 * 3 = {7 * 3}")
    print(f"7 / 3 = {7 / 3}    (浮点除)")
    print(f"7 // 3 = {7 // 3}  (整数除/地板除)")
    print(f"7 % 3 = {7 % 3}   (取余)")
    print(f"7 ** 3 = {7 ** 3}  (幂)")

    # 比较运算符
    print("\n--- 比较 ---")
    print(f"5 == 5: {5 == 5},  5 != 3: {5 != 3}")
    print(f"5 > 3: {5 > 3},  5 >= 5: {5 >= 5}")
    # 链式比较
    x = 7
    print(f"3 < x < 10: {3 < x < 10}")

    # 逻辑运算符 (and, or, not) & 短路求值
    print("\n--- 逻辑 ---")
    print(f"True and False -> {True and False}")
    print(f"True or False  -> {True or False}")
    print(f"'truthy' or 'default' -> {'truthy' or 'default'}")   # 短路：返回第一个 truthy 值
    print(f"'' or 'default'      -> {'' or 'default'}")

    # 位运算符
    print("\n--- 位运算 ---")
    print(f"12 & 10 = {12 & 10}    (1100 & 1010 -> 1000)")
    print(f"12 | 10 = {12 | 10}    (1100 | 1010 -> 1110)")
    print(f"12 ^ 10 = {12 ^ 10}    (1100 ^ 1010 -> 0110)")
    print(f"~12     = {~12}         (按位取反)")
    print(f"1 << 4  = {1 << 4}     (左移，等价于 *16)")
    print(f"32 >> 2 = {32 >> 2}    (右移，等价于 //4)")

    # 成员运算符
    print(f"\n'a' in 'abc': {'a' in 'abc'},  'z' not in 'abc': {'z' not in 'abc'}")
    # 身份运算符
    a, b = [1, 2], [1, 2]
    print(f"a is b: {a is b},  a == b: {a == b}")   # is 比较引用，== 比较值


# ============================================================
# §3  容器类型（简要引入）
# ============================================================

def demo_containers_brief() -> None:
    """快速浏览 4 种核心容器；详细操作见 02_data_structures.py。"""
    lst: list[int] = [1, 2, 3, 2, 1]          # 有序、可变、可重复
    tup: tuple[int, ...] = (10, 20, 30)       # 有序、不可变
    st: set[int] = {1, 2, 3}                  # 无序、可变、不重复
    dct: dict[str, int] = {"a": 1, "b": 2}    # 键值对；键不可变，值可变

    print(f"list  -> {lst}, type={type(lst)}")
    print(f"tuple -> {tup}, type={type(tup)}")
    print(f"set   -> {st}, type={type(st)}")
    print(f"dict  -> {dct}, type={type(dct)}")

    # frozenset — 不可变集合
    frozen: frozenset[int] = frozenset([1, 2, 3])
    print(f"frozenset -> {frozen}, type={type(frozen)}")


# ============================================================
# §4  控制流
# ============================================================

def demo_control_flow() -> None:
    """if / match / while / for 的全面示例。"""

    # ---------- if / elif / else ----------
    score = 87
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    else:
        grade = "F"
    print(f"\nif-elif: score={score} -> grade={grade}")

    # 三元表达式 (conditional expression)
    parity = "even" if score % 2 == 0 else "odd"
    print(f"三元: {score} is {parity}")

    # ---------- match (Python 3.10+) ----------
    def http_status(code: int) -> str:
        match code:
            case 200 | 201 | 204:
                return "成功"
            case 301 | 302:
                return "重定向"
            case 400:
                return "请求错误"
            case 401 | 403:
                return "认证/授权失败"
            case 404:
                return "未找到"
            case 500:
                return "服务器错误"
            case _:
                return "其他状态码"
    print(f"match: 404 -> {http_status(404)}, 200 -> {http_status(200)}")

    # ---------- while ----------
    print("\nwhile 循环: ", end="")
    n, total = 1, 0
    while n <= 10:
        total += n
        n += 1
    print(f"1+...+10 = {total}")

    # while + break / continue
    print("while-break: ", end="")
    i = 0
    while True:
        i += 1
        if i > 5:
            break
        if i % 2 == 0:
            continue
        print(i, end=" ")
    print()

    # ---------- for ----------
    print("\nfor 循环基础:")
    for i in range(5):                         # range(stop)
        print(f"  range(5)[{i}]", end=" ")
    print()

    for i in range(2, 8, 3):                   # range(start, stop, step)
        print(f"  range(2,8,3)[{i}]", end=" ")
    print()

    # enumerate
    print("\nenumerate:")
    for idx, ch in enumerate("ABCD"):
        print(f"  {idx}:{ch}", end=" ")
    print()

    # zip 并行迭代
    print("zip:")
    for a_val, b_val in zip("ABC", [1, 2, 3]):
        print(f"  {a_val}-{b_val}", end=" ")
    print()

    # for-else 子句：只有未触发 break 时才执行 else
    def find_prime_above(n: int) -> int | None:
        for candidate in range(n + 1, n + 50):
            for d in range(2, int(candidate**0.5) + 1):
                if candidate % d == 0:
                    break
            else:                               # 内层 for 的 else
                return candidate
        return None
    print(f"for-else: next prime after 50 -> {find_prime_above(50)}")


# ============================================================
# §5  列表推导式 / 生成器表达式 / 字典推导式
# ============================================================

def demo_comprehensions() -> None:
    """演示各种推导式。"""

    # 列表推导式
    squares: list[int] = [x**2 for x in range(10)]
    evens: list[int] = [x for x in range(20) if x % 2 == 0]
    # 嵌套推导
    matrix: list[list[int]] = [[i * j for j in range(1, 4)] for i in range(1, 4)]
    print(f"列表推导 squares: {squares}")
    print(f"列表推导 evens:   {evens}")
    print(f"列表推导 matrix:  {matrix}")

    # 集合推导式
    divisors: set[int] = {d for n in [12, 18, 24] for d in range(1, n + 1) if n % d == 0}
    print(f"集合推导 divisors: {sorted(divisors)}")

    # 字典推导式
    word_lengths: dict[str, int] = {w: len(w) for w in ["apple", "banana", "cherry"]}
    print(f"字典推导 word_lengths: {word_lengths}")

    # 生成器表达式（惰性求值）
    gen = (x**3 for x in range(5))
    print(f"生成器表达式 type: {type(gen)}, list(gen)={list(gen)}")


# ============================================================
# §6  函数
# ============================================================

def demo_functions() -> None:
    """位置参数、默认参数、可变参数、关键字参数、类型注解。"""

    # 基本定义
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    print(f"greet: {greet('World')}, {greet('Alice', 'Hi')}")

    # *args (可变位置参数)
    def product(*nums: float) -> float:
        result = 1.0
        for n in nums:
            result *= n
        return result
    print(f"product(2,3,4) = {product(2, 3, 4)}")

    # **kwargs (可变关键字参数)
    def build_url(base: str, **params: str) -> str:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{query}" if query else base
    print(f"build_url: {build_url('/api', page='2', size='10')}")

    # 仅位置 / 仅关键字参数 (Python 3.8+)
    def describe(obj: str, /, *, verbose: bool = False) -> str:
        """obj 只能按位置传入；verbose 只能按关键字传入。"""
        return f"{obj!r} (verbose={verbose})"
    print(f"describe: {describe('car', verbose=True)}")

    # 解包实参
    args = (3, 4, 5)
    print(f"product(*args) = {product(*args)}")
    info = {"name": "Bob", "greeting": "Hey"}
    print(f"greet(**info) = {greet(**info)}")

    # 函数注解（可通过 __annotations__ 访问）
    print(f"describe.__annotations__ = {describe.__annotations__}")

    # 函数是一等公民：赋值、传参、返回
    funcs: list[Callable[..., Any]] = [greet, str.upper, len]
    results = [f("test") if callable(f) else None for f in funcs]
    print(f"higher-order: {results}")


# ============================================================
# §7  变量作用域与闭包
# ============================================================

def demo_scope_and_closure() -> None:
    """LEGB 规则 (Local, Enclosing, Global, Built-in) 及闭包示例。"""

    x_global: str = "global"

    def outer(outer_param: str) -> Callable[[], str]:
        outer_var: str = "enclosing"

        def inner() -> str:
            local_var: str = "local"
            # locals() 显示当前所有局部变量
            return f"L:{local_var} | E:{outer_var} | G:{x_global} | outer_param:{outer_param}"
        return inner

    closure = outer("param_val")
    print(f"LEGB 闭包: {closure()}")
    print(f"闭包捕获的自由变量: {closure.__closure__}")
    if closure.__closure__:
        for cell in closure.__closure__:
            print(f"  cell contents = {cell.cell_contents}")

    # global 声明
    counter: int = 0

    def increment() -> None:
        global counter
        counter += 1

    increment()
    print(f"global counter after increment: {counter}")

    # nonlocal 声明
    def make_counter(start: int = 0) -> Callable[[], int]:
        count = start

        def tick() -> int:
            nonlocal count
            count += 1
            return count
        return tick

    c1 = make_counter(100)
    print(f"nonlocal counter: {c1()}, {c1()}, {c1()}")


# ============================================================
# §8  常用内置函数速览
# ============================================================

def demo_builtins() -> None:
    """展示常用内置函数。"""

    data = [3, 1, 4, 1, 5, 9, 2, 6]

    print(f"原始数据: {data}")
    print(f"  len          = {len(data)}")
    print(f"  sum          = {sum(data)}")
    print(f"  min / max    = {min(data)} / {max(data)}")
    print(f"  sorted       = {sorted(data, reverse=True)}")
    print(f"  any(>5)      = {any(x > 5 for x in data)}")
    print(f"  all(>0)      = {all(x > 0 for x in data)}")
    print(f"  abs(-5)      = {abs(-5)}")
    print(f"  round(pi,2)  = {round(math.pi, 2)}")
    print(f"  divmod(17,3) = {divmod(17, 3)}")
    print(f"  pow(2,10)    = {pow(2, 10)}")
    print(f"  ord('A')     = {ord('A')}, chr(65) = {chr(65)}")
    print(f"  bin(42)      = {bin(42)}, hex(42) = {hex(42)}")
    print(f"  repr('abc')  = {repr('abc')}")

    # map / filter / reduce
    doubled = list(map(lambda x: x * 2, data))
    filtered = list(filter(lambda x: x > 4, data))
    print(f"  map(*2)      = {doubled}")
    print(f"  filter(>4)   = {filtered}")

    from functools import reduce
    product_all = reduce(lambda a, b: a * b, data)
    print(f"  reduce(*)    = {product_all}")

    # zip 的高级用法：矩阵转置
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    transposed = list(zip(*matrix))
    print(f"  zip(*matrix) (转置) = {transposed}")


# ============================================================
# §9  类型检查与转换
# ============================================================

def demo_type_utilities() -> None:
    """isinstance, type, cast, 鸭子类型示例。"""

    def process(value: Any) -> str:
        if isinstance(value, int):
            return f"int: {value ** 2}"
        if isinstance(value, float):
            return f"float: {value:.2f}"
        if isinstance(value, str):
            return f"str: {value.upper()}"
        if isinstance(value, (list, tuple)):
            return f"seq: 长度={len(value)}"
        return f"unknown type: {type(value).__name__}"

    for v in [42, 3.14, "hello", [1, 2, 3], None]:
        print(f"  process({v!r}) -> {process(v)}")

    # EAFP vs LBYL
    # LBYL: Look Before You Leap
    d = {"a": 1}
    if "b" in d:
        print(f"LBYL: d['b']={d['b']}")
    else:
        print("LBYL: key 'b' not found")

    # EAFP: Easier to Ask for Forgiveness than Permission
    try:
        print(f"EAFP: d['b']={d['b']}")
    except KeyError:
        print("EAFP: key 'b' not found")


# ============================================================
# §10  main 守卫
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Python 基础 (01_fundamentals) 运行中...")
    print("=" * 60)

    demo_variables_and_types()
    demo_operators()
    demo_containers_brief()
    demo_control_flow()
    demo_comprehensions()
    demo_functions()
    demo_scope_and_closure()
    demo_builtins()
    demo_type_utilities()

    print("\n✅ 基础篇全部执行完毕!")
