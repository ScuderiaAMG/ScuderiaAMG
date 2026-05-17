#!/usr/bin/env python3
"""
Python 数据结构深入
涵盖：list / tuple / set / dict / deque / namedtuple / heapq / bisect
所有方法均附带可运行的示例代码
"""

import heapq
import bisect
from collections import (
    deque,
    defaultdict,
    OrderedDict,
    Counter,
    ChainMap,
    namedtuple,
)
from typing import Any, Iterable, Iterator, Sequence


# ============================================================
# §1  list — 有序可变序列
# ============================================================

def demo_list() -> None:
    print("=" * 60)
    print("§1  list 操作")
    print("=" * 60)

    # 构造
    a: list[int] = [1, 2, 3]
    b: list[int] = list(range(4, 7))            # [4, 5, 6]
    c: list[int] = [0] * 5                       # [0, 0, 0, 0, 0]
    d: list[int] = [x * 10 for x in range(3)]    # 推导式 [0, 10, 20]
    print(f"构造: a={a}, b={b}, c={c}, d={d}")

    # 索引与切片
    nums = [10, 20, 30, 40, 50, 60]
    print(f"\n原列表: {nums}")
    print(f"  nums[0]   = {nums[0]}")           # 首元素
    print(f"  nums[-1]  = {nums[-1]}")           # 末元素
    print(f"  nums[1:4] = {nums[1:4]}")          # [20, 30, 40]
    print(f"  nums[:3]  = {nums[:3]}")           # 前 3 个
    print(f"  nums[3:]  = {nums[3:]}")           # 索引 3 以后
    print(f"  nums[::2] = {nums[::2]}")          # 步长 2
    print(f"  nums[::-1]= {nums[::-1]}")          # 反转

    # 赋值切片
    nums_copy = nums[:]
    nums_copy[1:4] = [99, 88]
    print(f"\n切片赋值 nums[1:4]=[99,88] -> {nums_copy}")

    # --- 增删改查 ---
    fruits: list[str] = ["apple", "banana"]
    fruits.append("cherry")                      # 尾部追加
    fruits.insert(1, "kiwi")                     # 指定位置插入
    fruits.extend(["date", "elderberry"])        # 扩展
    print(f"\n增: {fruits}")

    last = fruits.pop()                          # 移除并返回尾部
    second = fruits.pop(1)                       # 移除索引 1
    fruits.remove("banana")                      # 按值移除（第一个匹配）
    print(f"删: pop()->{last}, pop(1)->{second}, fruits={fruits}")

    idx = fruits.index("cherry")                 # 查找索引
    count = fruits.count("apple")                # 计数
    fruits.sort()                                # 原地排序
    fruits.reverse()                             # 原地反转
    print(f"查: idx_of_cherry={idx}, apple_count={count}")
    print(f"排序+反转: {fruits}")

    # sorted / reversed 不改变原列表
    original = [3, 1, 4, 1, 5]
    print(f"\nsorted(original)  = {sorted(original)}")
    print(f"list(reversed(original)) = {list(reversed(original))}")
    print(f"original 依旧: {original}")

    # list 作为栈 (stack): append + pop
    stack: list[int] = []
    for v in [1, 2, 3]:
        stack.append(v)
    while stack:
        print(f"  pop stack -> {stack.pop()}", end=" ")
    print()

    # list 作为队列 (不推荐；应使用 collections.deque)
    # list.pop(0) 是 O(n)
    q = [1, 2, 3]
    q.append(4)
    front = q.pop(0)                             # O(n) — 不推荐
    print(f"list-queue pop(0) -> {front}, remaining: {q} (这很慢!)")


# ============================================================
# §2  tuple — 不可变序列
# ============================================================

def demo_tuple() -> None:
    print("\n" + "=" * 60)
    print("§2  tuple 操作")
    print("=" * 60)

    # 构造
    t1: tuple[int, ...] = (1, 2, 3)
    t2: tuple[int, ...] = tuple([4, 5, 6])
    single: tuple[int] = (42,)                  # 单元素必须加逗号
    empty: tuple = ()
    packed = 1, 2, "three"                      # 括号可省略（打包）
    print(f"构造: t1={t1}, single={single}, packed={packed}")

    # 拆包
    x, y, z = t1
    first, *rest = range(10)
    a_val, *middle, z_val = [1, 2, 3, 4, 5]
    print(f"拆包: x={x}, y={y}, z={z}")
    print(f"first={first}, rest={rest}")
    print(f"a={a_val}, middle={middle}, z={z_val}")

    # 交换变量（一行）
    p, q = "left", "right"
    p, q = q, p
    print(f"一行交换: p={p}, q={q}")

    # 不可变 ≠ 内容不能变（元素是可变对象时）
    nested = ([1, 2], [3, 4])
    nested[0].append(999)
    print(f"tuple 内 list 可变: {nested}")

    # 性能：tuple 比 list 创建快，占用内存少
    # sys.getsizeof 可验证
    import sys
    lst_small = [1, 2, 3, 4, 5]
    tup_small = (1, 2, 3, 4, 5)
    print(f"sizeof list  {len(lst_small)} elem: {sys.getsizeof(lst_small)} bytes")
    print(f"sizeof tuple {len(tup_small)} elem: {sys.getsizeof(tup_small)} bytes")


# ============================================================
# §3  set — 无序、可变、不重复
# ============================================================

def demo_set() -> None:
    print("\n" + "=" * 60)
    print("§3  set 操作")
    print("=" * 60)

    # 构造
    s1: set[int] = {1, 2, 3, 3, 3}             # {1, 2, 3}
    s2: set[int] = set([3, 4, 5])
    empty_set: set = set()                       # {} 创建的是 dict
    print(f"构造: s1={s1}, s2={s2}  ({} is dict: {type({}) == dict})")

    # 集合运算
    print(f"s1 | s2  (并集)  = {s1 | s2}")
    print(f"s1 & s2  (交集)  = {s1 & s2}")
    print(f"s1 - s2  (差集)  = {s1 - s2}")
    print(f"s1 ^ s2  (对称差)= {s1 ^ s2}")
    print(f"s1 <= s2 (子集)  = {s1 <= s2}")
    print(f"s1 >= s2 (超集)  = {s1 >= s2}")

    # 方法
    uniq = {10, 20, 30}
    uniq.add(40)                                 # 添加一个
    uniq.update({50, 60})                        # 添加多个
    uniq.remove(10)                              # 删除（不存在抛 KeyError）
    uniq.discard(999)                            # 安全删除（不抛异常）
    popped = uniq.pop()                          # 随机弹出一个
    print(f"方法演示: add/update/remove/discard/pop={popped} -> {uniq}")

    # 性能：O(1) 成员检查（基于哈希）
    big_set = set(range(100000))
    import time
    t0 = time.perf_counter()
    found = 99999 in big_set
    elapsed = time.perf_counter() - t0
    print(f"100k set 成员检查 99999 in set: {found}, 耗时 {elapsed*1e6:.1f} ns")

    # 去重 / 数学题
    duplicates = [1, 2, 2, 3, 3, 3, 4]
    uniq_list = list(set(duplicates))
    print(f"用 set 去重: {duplicates} -> {uniq_list}")

    # frozenset (不可变集合，可作 dict key)
    fs1 = frozenset([1, 2, 3])
    fs2 = frozenset([2, 3, 4])
    d = {fs1: "set A", fs2: "set B"}
    print(f"frozenset as dict key: {d}")


# ============================================================
# §4  dict — 映射类型
# ============================================================

def demo_dict() -> None:
    print("\n" + "=" * 60)
    print("§4  dict 操作")
    print("=" * 60)

    # 构造
    d1: dict[str, int] = {"a": 1, "b": 2}
    d2: dict[str, int] = dict(c=3, d=4)
    d3: dict[str, int] = dict([("e", 5), ("f", 6)])
    d4: dict[str, int] = {k: v for k, v in zip("xyz", range(3))}  # 字典推导
    print(f"构造: d1={d1}, d2={d2}, d3={d3}, d4={d4}")

    # 合并 (Python 3.9+)
    merged = d1 | d2                             # 键冲突时右侧覆盖
    print(f"合并 (|): {merged}")

    # 取值
    a_val = d1["a"]                              # 键不存在时 KeyError
    b_safe = d1.get("b", "default")              # 键不存在返回默认值
    print(f"d1['a']={a_val}, d1.get('missing','default')={d1.get('missing', 'default')}")

    # setdefault
    cache: dict[str, list[int]] = {}
    cache.setdefault("evens", []).append(2)      # 键不存在时先设默认值，再返回
    cache.setdefault("evens", []).append(4)
    print(f"setdefault: {cache}")

    # 视图对象：keys / values / items
    for k, v in d1.items():
        print(f"  items 遍历: {k} -> {v}")

    keys_view = d1.keys()
    print(f"keys view: {keys_view}, 'a' in keys_view: {'a' in keys_view}")

    # pop / popitem
    val = d1.pop("a")                            # 弹出指定键
    last_item = d1.popitem()                     # (Python 3.7+ LIFO) 弹出最后插入项
    print(f"pop('a')={val}, popitem={last_item}, remaining={d1}")


# ============================================================
# §5  collections 高级容器
# ============================================================

def demo_collections() -> None:
    print("\n" + "=" * 60)
    print("§5  collections 模块")
    print("=" * 60)

    # ------ deque：双端队列 ------
    print("\n--- deque ---")
    dq: deque[int] = deque([1, 2, 3], maxlen=5)  # 固定最大长度
    dq.append(4)
    dq.appendleft(0)                             # 左端入队
    dq.append(5)
    dq.append(6)                                 # 溢出：左侧自动弹出
    print(f"deque (maxlen=5): {dq}")
    print(f"  dq.pop()={dq.pop()}, dq.popleft()={dq.popleft()}, remaining={dq}")
    dq.rotate(1)                                 # 右旋
    print(f"  rotate(1) -> {dq}")
    dq.rotate(-2)                                # 左旋
    print(f"  rotate(-2) -> {dq}")

    # ------ defaultdict ------
    print("\n--- defaultdict ---")
    dd_list: defaultdict[str, list[int]] = defaultdict(list)
    dd_int: defaultdict[str, int] = defaultdict(int)
    for word in ["a", "b", "a", "c", "b", "a"]:
        dd_list[word].append(1)
        dd_int[word] += 1
    print(f"defaultdict(list): {dict(dd_list)}")
    print(f"defaultdict(int):  {dict(dd_int)}")

    # ------ OrderedDict ------
    print("\n--- OrderedDict ---")
    od = OrderedDict()
    od["first"] = 1
    od["second"] = 2
    od["third"] = 3
    od.move_to_end("first")                      # 移到末尾
    print(f"OrderedDict after move_to_end: {list(od.items())}")
    od.popitem(last=False)                       # 弹出首项 (FIFO)
    print(f"  popitem(last=False) -> {list(od.items())}")

    # ------ Counter ------
    print("\n--- Counter ---")
    cnt = Counter("abracadabra")
    print(f"Counter('abracadabra'): {cnt}")
    print(f"  most_common(2): {cnt.most_common(2)}")
    cnt2 = Counter("algebra")
    print(f"  cnt + cnt2: {cnt + cnt2}")
    print(f"  cnt - cnt2: {cnt - cnt2}")          # 只保留正计数

    # ------ ChainMap ------
    print("\n--- ChainMap ---")
    defaults = {"color": "red", "user": "guest"}
    cmd_line = {"user": "admin"}
    config = ChainMap(cmd_line, defaults)
    print(f"ChainMap: config['user']={config['user']}, config['color']={config['color']}")


# ============================================================
# §6  namedtuple — 轻量级数据类
# ============================================================

def demo_namedtuple() -> None:
    print("\n" + "=" * 60)
    print("§6  namedtuple")
    print("=" * 60)

    # 定义
    Point = namedtuple("Point", ["x", "y"])
    Point3D = namedtuple("Point3D", "x y z", defaults=(0,))
    #                            x  y   z (default 0)

    p1 = Point(10, 20)
    p2 = Point3D(5, 3)                          # z 使用默认值 0
    p3 = Point3D(5, 3, 7)
    print(f"Point: {p1}, 字段 x={p1.x}, y={p1[1]}")
    print(f"Point3D: p2={p2}, p3={p3}")

    # 内置方法
    print(f"p1._asdict(): {p1._asdict()}")
    print(f"p1._fields:  {p1._fields}")

    new_p1 = p1._replace(x=999)                  # 返回新实例（原实例不变）
    print(f"_replace(x=999): {new_p1}")

    # 从 iterable 构造
    from_iter = Point._make([7, 8])
    print(f"_make([7,8]): {from_iter}")

    # 内存效率与普通类对比
    class PointClass:
        __slots__ = ("x", "y")                   # 用 __slots__ 优化
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    import sys
    nt = Point(1, 2)
    cls_inst = PointClass(1, 2)
    reg_dict = {"x": 1, "y": 2}
    print(f"namedtuple size:   {sys.getsizeof(nt)} bytes")
    print(f"class(__slots__):  {sys.getsizeof(cls_inst)} bytes")
    print(f"regular dict:      {sys.getsizeof(reg_dict)} bytes")


# ============================================================
# §7  heapq — 堆队列算法
# ============================================================

def demo_heapq() -> None:
    print("\n" + "=" * 60)
    print("§7  heapq — 优先队列")
    print("=" * 60)

    # 最小堆
    heap: list[int] = [5, 1, 8, 3, 7]
    heapq.heapify(heap)                          # 原地转换为堆
    print(f"heapify([5,1,8,3,7]) -> {heap}")

    heapq.heappush(heap, 0)
    print(f"heappush(0) -> {heap}")
    smallest = heapq.heappop(heap)
    print(f"heappop() -> {smallest}, heap={heap}")
    print(f"heap[0] (最小但不弹出) = {heap[0]}")

    # nlargest / nsmallest
    data = [3, 7, 2, 9, 1, 5, 8, 4]
    print(f"\nnlargest(3, data)  = {heapq.nlargest(3, data)}")
    print(f"nsmallest(3, data) = {heapq.nsmallest(3, data)}")

    # 优先级队列示例 — 使用元组 (priority, counter, item) 避免比较 item
    import itertools
    pq: list[tuple[int, int, str]] = []
    counter_gen = itertools.count()
    for task, prio in [("fix bug", 1), ("write docs", 3), ("add feature", 2)]:
        heapq.heappush(pq, (prio, next(counter_gen), task))

    while pq:
        prio, _, task = heapq.heappop(pq)
        print(f"  处理优先级 {prio}: {task}")


# ============================================================
# §8  bisect — 有序列表二分查找
# ============================================================

def demo_bisect() -> None:
    print("\n" + "=" * 60)
    print("§8  bisect — 二分查找与插入")
    print("=" * 60)

    sorted_data = [1, 3, 5, 7, 9, 11]

    # bisect_left: 找到插入位置（左侧优先）
    pos_left = bisect.bisect_left(sorted_data, 5)
    pos_right = bisect.bisect_right(sorted_data, 5)
    print(f"bisect_left([1,3,5,7,9,11], 5)  = {pos_left}   (在第一个 5 前)")
    print(f"bisect_right([1,3,5,7,9,11], 5) = {pos_right}   (在最后一个 5 后)")

    # 插入（保持有序）
    working = sorted_data[:]
    bisect.insort(working, 6)                    # O(n) 插入 + O(log n) 查找
    print(f"insort(6) -> {working}")

    # 成绩评级（自定义 key — Python 3.10+ 支持 key 参数）
    breakpoints = [60, 70, 80, 90]
    grades = "FDCBA"
    for score in [55, 73, 85, 91, 100]:
        idx = bisect.bisect_right(breakpoints, score)
        print(f"  分数 {score} -> {grades[idx]}")


# ============================================================
# §9  综合练习
# ============================================================

def demo_exercise() -> None:
    print("\n" + "=" * 60)
    print("§9  综合练习")
    print("=" * 60)

    # LRU 缓存 (使用 OrderedDict)
    class LRUCache:
        def __init__(self, capacity: int) -> None:
            self.capacity = capacity
            self.cache: OrderedDict[str, Any] = OrderedDict()

        def get(self, key: str) -> Any:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            return self.cache[key]

        def put(self, key: str, value: Any) -> None:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    lru = LRUCache(3)
    lru.put("a", 1)
    lru.put("b", 2)
    lru.put("c", 3)
    lru.get("a")                                 # a 移到末尾
    lru.put("d", 4)                              # 驱逐 b
    print(f"LRU (capacity=3): {list(lru.cache.items())}  (b 被驱逐)")

    # Top-K 高频词
    words = ["the", "day", "is", "sunny", "the", "the", "sunny", "is", "is"]
    top2 = Counter(words).most_common(2)
    print(f"Top-K 高频词: {top2}")

    # 合并 K 个有序列表 (heapq)
    lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    merged = list(heapq.merge(*lists))
    print(f"heapq.merge 合并 K 个有序列表: {merged}")


if __name__ == "__main__":
    demo_list()
    demo_tuple()
    demo_set()
    demo_dict()
    demo_collections()
    demo_namedtuple()
    demo_heapq()
    demo_bisect()
    demo_exercise()
    print("\n✅ 数据结构篇全部执行完毕!")
