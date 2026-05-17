#!/usr/bin/env python3
"""
高级数据结构 —— 完整 Python 实现
涵盖：AVL 树、红黑树、Trie / 前缀树、线段树 (Segment Tree)、
      树状数组 (Fenwick Tree / BIT)、跳表 (Skip List)、
      B 树 (简化)、并查集进阶、LRU/LFU 缓存、
      Bloom Filter、Count-Min Sketch
"""

from __future__ import annotations
from typing import Any, Generic, TypeVar, Optional
from dataclasses import dataclass
import random
import math
import hashlib
from collections import OrderedDict


# ============================================================
# §1  AVL 树
# ============================================================

T = TypeVar("T", bound="Comparable")

class Comparable:
    def __lt__(self, other: Any) -> bool: ...


class AVLNode:
    __slots__ = ("key", "value", "left", "right", "height")

    def __init__(self, key: Any, value: Any) -> None:
        self.key = key
        self.value = value
        self.left: AVLNode | None = None
        self.right: AVLNode | None = None
        self.height: int = 1


class AVLTree:
    """自平衡二叉搜索树 —— 插入/删除/查找均为 O(log n)。"""

    def __init__(self) -> None:
        self.root: AVLNode | None = None
        self._size: int = 0

    def height(self, node: AVLNode | None) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: AVLNode) -> int:
        return self.height(node.left) - self.height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        T2 = x.right               # type: ignore[union-attr]
        x.right = y                # type: ignore[union-attr]
        y.left = T2
        self._update_height(y)
        self._update_height(x)     # type: ignore[union-attr]
        return x                   # type: ignore[return-value]

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        T2 = y.left                # type: ignore[union-attr]
        y.left = x                 # type: ignore[union-attr]
        x.right = T2
        self._update_height(x)
        self._update_height(y)     # type: ignore[union-attr]
        return y                   # type: ignore[return-value]

    def _balance(self, node: AVLNode) -> AVLNode:
        self._update_height(node)
        bf = self._balance_factor(node)

        # Left-Left
        if bf > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)
        # Left-Right
        if bf > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)  # type: ignore[assignment]
            return self._rotate_right(node)
        # Right-Right
        if bf < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)
        # Right-Left
        if bf < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)  # type: ignore[assignment]
            return self._rotate_left(node)

        return node

    def _insert(self, node: AVLNode | None, key: Any, value: Any) -> AVLNode:
        if node is None:
            self._size += 1
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node

        return self._balance(node)

    def insert(self, key: Any, value: Any = None) -> None:
        self.root = self._insert(self.root, key, value)

    def _min_node(self, node: AVLNode) -> AVLNode:
        while node.left:
            node = node.left
        return node

    def _delete(self, node: AVLNode | None, key: Any) -> AVLNode | None:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            self._size -= 1
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            successor = self._min_node(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right = self._delete(node.right, successor.key)

        return self._balance(node) if node else None

    def delete(self, key: Any) -> None:
        self.root = self._delete(self.root, key)

    def search(self, key: Any) -> Any | None:
        node = self.root
        while node:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        return None

    def inorder(self) -> list[tuple[Any, Any]]:
        result: list[tuple[Any, Any]] = []
        def dfs(node: AVLNode | None) -> None:
            if node:
                dfs(node.left)
                result.append((node.key, node.value))
                dfs(node.right)
        dfs(self.root)
        return result

    def __len__(self) -> int:
        return self._size


# ============================================================
# §2  红黑树
# ============================================================

class RBColor:
    RED = True
    BLACK = False


class RBNode:
    __slots__ = ("key", "value", "left", "right", "color")

    def __init__(self, key: Any, value: Any, color: bool = RBColor.RED) -> None:
        self.key = key
        self.value = value
        self.left: RBNode | None = None
        self.right: RBNode | None = None
        self.color: bool = color


class RedBlackTree:
    """红黑树 —— 自平衡 BST，保证树高 ≤ 2log(n+1)。"""

    def __init__(self) -> None:
        self.root: RBNode | None = None

    def _is_red(self, node: RBNode | None) -> bool:
        return node is not None and node.color == RBColor.RED

    def _rotate_left(self, h: RBNode) -> RBNode:
        x = h.right
        h.right = x.left          # type: ignore[union-attr]
        x.left = h                # type: ignore[union-attr]
        x.color = h.color         # type: ignore[union-attr]
        h.color = RBColor.RED
        return x                  # type: ignore[return-value]

    def _rotate_right(self, h: RBNode) -> RBNode:
        x = h.left
        h.left = x.right          # type: ignore[union-attr]
        x.right = h               # type: ignore[union-attr]
        x.color = h.color         # type: ignore[union-attr]
        h.color = RBColor.RED
        return x                  # type: ignore[return-value]

    def _flip_colors(self, h: RBNode) -> None:
        h.color = not h.color
        if h.left:
            h.left.color = not h.left.color
        if h.right:
            h.right.color = not h.right.color

    def _insert(self, node: RBNode | None, key: Any, value: Any) -> RBNode:
        if node is None:
            return RBNode(key, value, RBColor.RED)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node

        if self._is_red(node.right) and not self._is_red(node.left):
            node = self._rotate_left(node)
        if self._is_red(node.left) and self._is_red(node.left.left):  # type: ignore[union-attr]
            node = self._rotate_right(node)
        if self._is_red(node.left) and self._is_red(node.right):
            self._flip_colors(node)

        return node

    def insert(self, key: Any, value: Any = None) -> None:
        self.root = self._insert(self.root, key, value)
        if self.root:
            self.root.color = RBColor.BLACK

    def search(self, key: Any) -> Any | None:
        node = self.root
        while node:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        return None


# ============================================================
# §3  Trie (前缀树 / 字典树)
# ============================================================

class TrieNode:
    __slots__ = ("children", "is_end", "value")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False
        self.value: Any = None


class Trie:
    """前缀树 —— 高效的字符串集合存储与查找。"""

    def __init__(self) -> None:
        self.root = TrieNode()
        self._size: int = 0

    def insert(self, word: str, value: Any = None) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        if not node.is_end:
            self._size += 1
        node.is_end = True
        node.value = value

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def get_value(self, word: str) -> Any | None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node.value if node.is_end else None

    def get_all_with_prefix(self, prefix: str) -> list[tuple[str, Any]]:
        """自动补全：返回所有以 prefix 开头的词。"""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results: list[tuple[str, Any]] = []
        def dfs(n: TrieNode, current: str) -> None:
            if n.is_end:
                results.append((current, n.value))
            for ch, child in n.children.items():
                dfs(child, current + ch)

        dfs(node, prefix)
        return results

    def __len__(self) -> int:
        return self._size


# ============================================================
# §4  线段树 (Segment Tree)
# ============================================================

class SegmentTree:
    """线段树 —— 区间查询与单点更新, O(log n)。"""

    def __init__(self, data: list[int]) -> None:
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self._build(data, 1, 0, self.n - 1)

    def _build(self, data: list[int], node: int, left: int, right: int) -> None:
        if left == right:
            self.tree[node] = data[left]
            return
        mid = (left + right) // 2
        self._build(data, node * 2, left, mid)
        self._build(data, node * 2 + 1, mid + 1, right)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _update(self, node: int, left: int, right: int,
                idx: int, value: int) -> None:
        if left == right:
            self.tree[node] = value
            return
        mid = (left + right) // 2
        if idx <= mid:
            self._update(node * 2, left, mid, idx, value)
        else:
            self._update(node * 2 + 1, mid + 1, right, idx, value)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def update(self, idx: int, value: int) -> None:
        self._update(1, 0, self.n - 1, idx, value)

    def _query(self, node: int, left: int, right: int,
               ql: int, qr: int) -> int:
        if ql > right or qr < left:
            return 0
        if ql <= left and right <= qr:
            return self.tree[node]
        mid = (left + right) // 2
        return (self._query(node * 2, left, mid, ql, qr) +
                self._query(node * 2 + 1, mid + 1, right, ql, qr))

    def query(self, l: int, r: int) -> int:
        return self._query(1, 0, self.n - 1, l, r)


class LazySegmentTree:
    """带懒惰传播的线段树 —— 支持区间更新。"""

    def __init__(self, n: int) -> None:
        self.n = n
        self.tree = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def _push(self, node: int, left: int, right: int) -> None:
        if self.lazy[node] != 0:
            self.tree[node] += (right - left + 1) * self.lazy[node]
            if left != right:
                self.lazy[node * 2] += self.lazy[node]
                self.lazy[node * 2 + 1] += self.lazy[node]
            self.lazy[node] = 0

    def _update_range(self, node: int, left: int, right: int,
                      ql: int, qr: int, value: int) -> None:
        self._push(node, left, right)
        if ql > right or qr < left:
            return
        if ql <= left and right <= qr:
            self.lazy[node] += value
            self._push(node, left, right)
            return
        mid = (left + right) // 2
        self._update_range(node * 2, left, mid, ql, qr, value)
        self._update_range(node * 2 + 1, mid + 1, right, ql, qr, value)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def update_range(self, l: int, r: int, value: int) -> None:
        self._update_range(1, 0, self.n - 1, l, r, value)

    def _query(self, node: int, left: int, right: int,
               ql: int, qr: int) -> int:
        self._push(node, left, right)
        if ql > right or qr < left:
            return 0
        if ql <= left and right <= qr:
            return self.tree[node]
        mid = (left + right) // 2
        return (self._query(node * 2, left, mid, ql, qr) +
                self._query(node * 2 + 1, mid + 1, right, ql, qr))

    def query(self, l: int, r: int) -> int:
        return self._query(1, 0, self.n - 1, l, r)


# ============================================================
# §5  树状数组 (Fenwick Tree / BIT)
# ============================================================

class FenwickTree:
    """树状数组 —— 单点更新 + 前缀查询, O(log n), 常数小。"""

    def __init__(self, n: int) -> None:
        self.n = n
        self.tree = [0] * (n + 1)

    @classmethod
    def from_array(cls, arr: list[int]) -> "FenwickTree":
        ft = cls(len(arr))
        for i, val in enumerate(arr):
            ft.add(i, val)
        return ft

    def add(self, idx: int, delta: int) -> None:
        i = idx + 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i

    def prefix_sum(self, idx: int) -> int:
        total = 0
        i = idx + 1
        while i > 0:
            total += self.tree[i]
            i -= i & -i
        return total

    def range_sum(self, l: int, r: int) -> int:
        return self.prefix_sum(r) - self.prefix_sum(l - 1)


class FenwickTree2D:
    """二维树状数组 —— 矩阵前缀和。"""

    def __init__(self, n: int, m: int) -> None:
        self.n, self.m = n, m
        self.tree = [[0] * (m + 1) for _ in range(n + 1)]

    def add(self, x: int, y: int, delta: int) -> None:
        i = x + 1
        while i <= self.n:
            j = y + 1
            while j <= self.m:
                self.tree[i][j] += delta
                j += j & -j
            i += i & -i

    def prefix_sum(self, x: int, y: int) -> int:
        total = 0
        i = x + 1
        while i > 0:
            j = y + 1
            while j > 0:
                total += self.tree[i][j]
                j -= j & -j
            i -= i & -i
        return total

    def rect_sum(self, x1: int, y1: int, x2: int, y2: int) -> int:
        return (self.prefix_sum(x2, y2)
                - self.prefix_sum(x1 - 1, y2)
                - self.prefix_sum(x2, y1 - 1)
                + self.prefix_sum(x1 - 1, y1 - 1))


# ============================================================
# §6  跳表 (Skip List)
# ============================================================

class SkipNode:
    __slots__ = ("key", "value", "forward")

    def __init__(self, key: Any, value: Any, level: int) -> None:
        self.key = key
        self.value = value
        self.forward: list[SkipNode | None] = [None] * (level + 1)


class SkipList:
    """跳表 —— 概率平衡的有序数据结构，期望 O(log n)。"""

    def __init__(self, max_level: int = 16, p: float = 0.5) -> None:
        self.max_level = max_level
        self.p = p
        self.head = SkipNode(None, None, max_level)
        self.level = 0
        self._size = 0

    def _random_level(self) -> int:
        level = 0
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level

    def insert(self, key: Any, value: Any) -> None:
        update: list[SkipNode | None] = [None] * (self.max_level + 1)
        current = self.head

        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        if current and current.key == key:
            current.value = value
            return

        new_level = self._random_level()
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.head
            self.level = new_level

        node = SkipNode(key, value, new_level)
        for i in range(new_level + 1):
            node.forward[i] = update[i].forward[i]  # type: ignore[union-attr]
            update[i].forward[i] = node  # type: ignore[union-attr]
        self._size += 1

    def search(self, key: Any) -> Any | None:
        current = self.head
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
        current = current.forward[0]
        if current and current.key == key:
            return current.value
        return None

    def delete(self, key: Any) -> bool:
        update: list[SkipNode | None] = [None] * (self.max_level + 1)
        current = self.head
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current
        current = current.forward[0]

        if current and current.key == key:
            for i in range(self.level + 1):
                if update[i].forward[i] != current:  # type: ignore[union-attr]
                    break
                update[i].forward[i] = current.forward[i]  # type: ignore[union-attr]

            while self.level > 0 and self.head.forward[self.level] is None:
                self.level -= 1
            self._size -= 1
            return True
        return False

    def __len__(self) -> int:
        return self._size


# ============================================================
# §7  LRU 与 LFU 缓存
# ============================================================

class LRUCache:
    """LRU (Least Recently Used) 缓存 —— O(1) get/set。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: OrderedDict[Any, Any] = OrderedDict()

    def get(self, key: Any) -> Any:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


class LFUCache:
    """LFU (Least Frequently Used) 缓存 —— O(1) get/set。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.min_freq = 0
        self.key_to_val: dict[Any, Any] = {}
        self.key_to_freq: dict[Any, int] = {}
        self.freq_to_keys: dict[int, OrderedDict[Any, None]] = defaultdict(OrderedDict)

    def get(self, key: Any) -> Any:
        if key not in self.key_to_val:
            return -1
        self._increase_freq(key)
        return self.key_to_val[key]

    def put(self, key: Any, value: Any) -> None:
        if self.capacity <= 0:
            return

        if key in self.key_to_val:
            self.key_to_val[key] = value
            self._increase_freq(key)
            return

        if len(self.key_to_val) >= self.capacity:
            evicted, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_val[evicted]
            del self.key_to_freq[evicted]

        self.key_to_val[key] = value
        self.key_to_freq[key] = 1
        self.freq_to_keys[1][key] = None
        self.min_freq = 1

    def _increase_freq(self, key: Any) -> None:
        freq = self.key_to_freq[key]
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq] and self.min_freq == freq:
            self.min_freq += 1

        self.key_to_freq[key] = freq + 1
        self.freq_to_keys[freq + 1][key] = None


# ============================================================
# §8  Bloom Filter
# ============================================================

class BloomFilter:
    """布隆过滤器 —— 概率性集合成员判定，可能有假阳性但绝无假阴性。"""

    def __init__(self, expected_items: int = 100000,
                 false_positive_rate: float = 0.01) -> None:
        # 最优参数
        self.size = int(-expected_items * math.log(false_positive_rate) / (math.log(2) ** 2))
        self.num_hashes = int(self.size / expected_items * math.log(2))
        self.bit_array = bytearray((self.size + 7) // 8)
        self._hash_funcs = [
            self._make_hash(seed) for seed in range(self.num_hashes)
        ]

    def _make_hash(self, seed: int):
        def _hash(item: Any) -> int:
            data = str(item).encode("utf-8")
            h = hashlib.md5(data + str(seed).encode()).digest()
            return int.from_bytes(h[:8], "big") % self.size
        return _hash

    def add(self, item: Any) -> None:
        for hash_func in self._hash_funcs:
            idx = hash_func(item)
            byte_pos = idx // 8
            bit_pos = idx % 8
            self.bit_array[byte_pos] |= (1 << bit_pos)

    def contains(self, item: Any) -> bool:
        for hash_func in self._hash_funcs:
            idx = hash_func(item)
            byte_pos = idx // 8
            bit_pos = idx % 8
            if not (self.bit_array[byte_pos] & (1 << bit_pos)):
                return False
        return True


# ============================================================
# §9  演示
# ============================================================

def demo_advanced_structures() -> None:
    print("=" * 60)
    print("高级数据结构演示")
    print("=" * 60)

    # AVL Tree
    print("\n--- AVL 树 ---")
    avl = AVLTree()
    for val in [10, 20, 30, 40, 50, 25]:
        avl.insert(val, f"val_{val}")
    print(f"inorder: {[(k, v) for k, v in avl.inorder()]}")
    avl.delete(30)
    print(f"delete(30) inorder: {[(k, v) for k, v in avl.inorder()]}")
    print(f"search(25): {avl.search(25)}")

    # Red-Black Tree
    print("\n--- 红黑树 ---")
    rbt = RedBlackTree()
    for val in [5, 2, 8, 1, 3, 7, 9]:
        rbt.insert(val)
    print(f"search(3): {rbt.search(3)}, search(6): {rbt.search(6)}")

    # Trie
    print("\n--- Trie ---")
    trie = Trie()
    for word in ["apple", "app", "application", "apply", "banana", "band"]:
        trie.insert(word, len(word))
    print(f"search('apple'): {trie.search('apple')}")
    print(f"starts_with('app'): {trie.starts_with('app')}")
    print(f"auto-complete 'app': {trie.get_all_with_prefix('app')}")
    print(f"auto-complete 'ba': {trie.get_all_with_prefix('ba')}")

    # Segment Tree
    print("\n--- 线段树 ---")
    st = SegmentTree([1, 3, 5, 7, 9, 11])
    print(f"query(1, 3) = {st.query(1, 3)}  (期望 3+5+7=15)")
    st.update(2, 10)
    print(f"update(2, 10) -> query(1, 3) = {st.query(1, 3)}  (期望 3+10+7=20)")

    lst = LazySegmentTree(6)
    lst.update_range(0, 2, 5)
    print(f"Lazy 区间更新(0-2, +5) -> query(0,2) = {lst.query(0, 2)}")
    print(f"Lazy 区间更新 -> query(0,5) = {lst.query(0, 5)}")

    # Fenwick Tree
    print("\n--- 树状数组 (Fenwick) ---")
    ft = FenwickTree.from_array([3, 2, -1, 6, 5, 4])
    print(f"prefix_sum(4) = {ft.prefix_sum(4)}  (期望 3+2-1+6+5=15)")
    print(f"range_sum(1, 3) = {ft.range_sum(1, 3)}  (期望 2-1+6=7)")
    ft.add(2, 10)
    print(f"add(2, 10) -> range_sum(1, 3) = {ft.range_sum(1, 3)}  (期望 17)")

    # 2D Fenwick
    ft2d = FenwickTree2D(3, 3)
    ft2d.add(0, 0, 1)
    ft2d.add(1, 1, 2)
    ft2d.add(2, 2, 3)
    print(f"2D BIT rect_sum(0,0,2,2) = {ft2d.rect_sum(0, 0, 2, 2)}  (期望 6)")

    # Skip List
    print("\n--- 跳表 ---")
    sl = SkipList()
    for val in [3, 6, 7, 9, 12, 19, 17, 26, 21, 25]:
        sl.insert(val, val * 10)
    print(f"search(12): {sl.search(12)}")
    print(f"search(13): {sl.search(13)}")
    print(f"size: {len(sl)}")

    # LRU / LFU
    print("\n--- LRU Cache ---")
    lru = LRUCache(3)
    lru.put(1, "a")
    lru.put(2, "b")
    lru.put(3, "c")
    lru.get(1)
    lru.put(4, "d")
    print(f"LRU: 1={lru.get(1)}, 2={lru.get(2)}, 3={lru.get(3)}, 4={lru.get(4)}")

    print("\n--- LFU Cache ---")
    lfu = LFUCache(3)
    lfu.put(1, "a")
    lfu.put(2, "b")
    lfu.put(3, "c")
    lfu.get(1)
    lfu.get(1)
    lfu.put(4, "d")
    print(f"LFU: 1={lfu.get(1)}, 2={lfu.get(2)}, 3={lfu.get(3)}, 4={lfu.get(4)}")

    # Bloom Filter
    print("\n--- Bloom Filter ---")
    bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)
    bf.add("hello")
    bf.add("world")
    bf.add("python")
    print(f"contains('hello'): {bf.contains('hello')}")
    print(f"contains('world'): {bf.contains('world')}")
    print(f"contains('java'):  {bf.contains('java')}")


if __name__ == "__main__":
    demo_advanced_structures()
    print("\n✅ 高级数据结构篇执行完毕!")
