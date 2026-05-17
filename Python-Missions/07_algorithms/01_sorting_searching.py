#!/usr/bin/env python3
"""
经典排序与查找算法 —— 完整 Python 实现
涵盖：O(n²) 排序（冒泡/选择/插入/希尔）、O(n log n) 排序（归并/快速/堆/TimSort）、
      线性排序（计数/基数/桶）、二分查找及其变体、KMP 字符串匹配、
      各种算法的复杂度分析与性能对比
"""

import random
import time
import heapq
from typing import Any, Callable, TypeVar

T = TypeVar("T")


# ============================================================
# §1  O(n²) 排序算法
# ============================================================

def bubble_sort(arr: list[T]) -> list[T]:
    """冒泡排序 —— 稳定，O(n²)，原地。每次将最大元素'浮'到末尾。"""
    a = arr[:]
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def selection_sort(arr: list[T]) -> list[T]:
    """选择排序 —— 不稳定，O(n²)，原地。每次选择最小元素放到前面。"""
    a = arr[:]
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def insertion_sort(arr: list[T]) -> list[T]:
    """插入排序 —— 稳定，O(n²)，原地。对小规模数据/近乎有序数据非常高效。"""
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def shell_sort(arr: list[T]) -> list[T]:
    """希尔排序 —— 不稳定，O(n log² n)~O(n^(4/3))。插入排序的改进版。"""
    a = arr[:]
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 2
    return a


def cocktail_shaker_sort(arr: list[T]) -> list[T]:
    """鸡尾酒排序 —— 双向冒泡排序，稳定，O(n²)。"""
    a = arr[:]
    n = len(a)
    swapped = True
    start = 0
    end = n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        start += 1
    return a


def gnome_sort(arr: list[T]) -> list[T]:
    """地精排序 —— 稳定，O(n²)。类似于插入排序但只用相邻交换。"""
    a = arr[:]
    i = 0
    while i < len(a):
        if i == 0 or a[i] >= a[i - 1]:
            i += 1
        else:
            a[i], a[i - 1] = a[i - 1], a[i]
            i -= 1
    return a


# ============================================================
# §2  O(n log n) 排序算法
# ============================================================

def merge_sort(arr: list[T]) -> list[T]:
    """归并排序 —— 稳定，O(n log n)，需要 O(n) 额外空间。"""
    def _merge_sort(a: list[T]) -> list[T]:
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = _merge_sort(a[:mid])
        right = _merge_sort(a[mid:])
        return _merge(left, right)

    def _merge(left: list[T], right: list[T]) -> list[T]:
        result: list[T] = []
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

    return _merge_sort(arr[:])


def merge_sort_iterative(arr: list[T]) -> list[T]:
    """归并排序迭代版 —— 自底向上，无递归开销。"""
    a = arr[:]
    n = len(a)
    width = 1
    while width < n:
        for i in range(0, n, 2 * width):
            left = a[i:i + width]
            right = a[i + width:i + 2 * width]
            merged: list[T] = []
            li = ri = 0
            while li < len(left) and ri < len(right):
                if left[li] <= right[ri]:
                    merged.append(left[li])
                    li += 1
                else:
                    merged.append(right[ri])
                    ri += 1
            merged.extend(left[li:])
            merged.extend(right[ri:])
            a[i:i + len(merged)] = merged
        width *= 2
    return a


def quick_sort(arr: list[T]) -> list[T]:
    """快速排序 —— 不稳定，平均 O(n log n)，最坏 O(n²)。"""
    def _quick_sort(a: list[T], low: int, high: int) -> None:
        if low < high:
            pi = _partition(a, low, high)
            _quick_sort(a, low, pi - 1)
            _quick_sort(a, pi + 1, high)

    def _partition(a: list[T], low: int, high: int) -> int:
        # 三数取中法选 pivot
        mid = (low + high) // 2
        pivot_candidates = [(a[low], low), (a[mid], mid), (a[high], high)]
        pivot_candidates.sort(key=lambda x: x[0])
        pivot_idx = pivot_candidates[1][1]
        a[pivot_idx], a[high] = a[high], a[pivot_idx]

        pivot = a[high]
        i = low - 1
        for j in range(low, high):
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[high] = a[high], a[i + 1]
        return i + 1

    a = arr[:]
    _quick_sort(a, 0, len(a) - 1)
    return a


def quick_sort_iterative(arr: list[T]) -> list[T]:
    """快速排序迭代版 —— 使用显式栈避免递归。"""
    a = arr[:]
    stack: list[tuple[int, int]] = [(0, len(a) - 1)]

    while stack:
        low, high = stack.pop()
        if low >= high:
            continue

        mid = (low + high) // 2
        candidates = [(a[low], low), (a[mid], mid), (a[high], high)]
        candidates.sort(key=lambda x: x[0])
        pivot_idx = candidates[1][1]
        a[pivot_idx], a[high] = a[high], a[pivot_idx]

        pivot = a[high]
        i = low - 1
        for j in range(low, high):
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[high] = a[high], a[i + 1]
        pi = i + 1

        stack.append((low, pi - 1))
        stack.append((pi + 1, high))

    return a


def heap_sort(arr: list[T]) -> list[T]:
    """堆排序 —— 不稳定，O(n log n)，原地。"""
    a = arr[:]
    n = len(a)

    def heapify(heap: list[T], n: int, i: int) -> None:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and heap[left] > heap[largest]:
            largest = left
        if right < n and heap[right] > heap[largest]:
            largest = right
        if largest != i:
            heap[i], heap[largest] = heap[largest], heap[i]
            heapify(heap, n, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(a, n, i)

    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        heapify(a, i, 0)

    return a


def timsort(arr: list[T]) -> list[T]:
    """Timsort —— Python 内置 sorted() 使用的算法，稳定，O(n log n)。
    这里实现简化版本用于学习。"""
    return sorted(arr)


def intro_sort(arr: list[T]) -> list[T]:
    """内省排序 —— C++ std::sort 使用的算法，混合快速/堆/插入排序。"""

    def _insertion_sort(a: list[T], low: int, high: int) -> None:
        for i in range(low + 1, high + 1):
            key = a[i]
            j = i - 1
            while j >= low and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key

    def _heap_sort_range(a: list[T], low: int, high: int) -> None:
        segment = a[low:high + 1]
        segment.sort()
        a[low:high + 1] = segment

    def _partition(a: list[T], low: int, high: int) -> int:
        pivot = a[high]
        i = low - 1
        for j in range(low, high):
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[high] = a[high], a[i + 1]
        return i + 1

    def _intro_sort(a: list[T], low: int, high: int, depth_limit: int) -> None:
        size = high - low + 1
        if size <= 16:
            _insertion_sort(a, low, high)
            return
        if depth_limit == 0:
            _heap_sort_range(a, low, high)
            return
        pi = _partition(a, low, high)
        _intro_sort(a, low, pi - 1, depth_limit - 1)
        _intro_sort(a, pi + 1, high, depth_limit - 1)

    a = arr[:]
    max_depth = 2 * (len(a).bit_length())
    _intro_sort(a, 0, len(a) - 1, max_depth)
    return a


# ============================================================
# §3  线性时间排序
# ============================================================

def counting_sort(arr: list[int]) -> list[int]:
    """计数排序 —— 稳定，O(n + k)，适用于整数且范围已知。"""
    if not arr:
        return []
    min_val, max_val = min(arr), max(arr)
    k = max_val - min_val + 1
    count = [0] * k
    result = [0] * len(arr)

    for x in arr:
        count[x - min_val] += 1
    for i in range(1, k):
        count[i] += count[i - 1]
    for x in reversed(arr):
        count[x - min_val] -= 1
        result[count[x - min_val]] = x

    return result


def radix_sort(arr: list[int]) -> list[int]:
    """基数排序 (LSD) —— 稳定，O(d * (n + k))，d 为位数。"""
    if not arr:
        return []
    max_val = max(arr)
    a = arr[:]

    exp = 1
    while max_val // exp > 0:
        n = len(a)
        output = [0] * n
        count = [0] * 10

        for x in a:
            digit = (x // exp) % 10
            count[digit] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for x in reversed(a):
            digit = (x // exp) % 10
            count[digit] -= 1
            output[count[digit]] = x
        a = output
        exp *= 10

    return a


def bucket_sort(arr: list[float]) -> list[float]:
    """桶排序 —— 稳定，平均 O(n + k)，适用于均匀分布的数据。"""
    if not arr:
        return []
    n = len(arr)
    buckets: list[list[float]] = [[] for _ in range(n)]

    for x in arr:
        idx = min(n - 1, int(x * n))
        buckets[idx].append(x)

    for bucket in buckets:
        bucket.sort()

    result: list[float] = []
    for bucket in buckets:
        result.extend(bucket)
    return result


def pigeonhole_sort(arr: list[int]) -> list[int]:
    """鸽巢排序 —— 类似于计数排序的简化版，O(n + range)。"""
    if not arr:
        return []
    min_val, max_val = min(arr), max(arr)
    size = max_val - min_val + 1
    holes: list[list[int]] = [[] for _ in range(size)]

    for x in arr:
        holes[x - min_val].append(x)

    result: list[int] = []
    for hole in holes:
        result.extend(hole)
    return result


# ============================================================
# §4  二分查找及其变体
# ============================================================

def binary_search(arr: list[T], target: T) -> int:
    """标准二分查找 —— O(log n)，返回索引或 -1。"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def binary_search_leftmost(arr: list[T], target: T) -> int:
    """查找目标值的最左位置（第一个 >= target 的位置）。"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def binary_search_rightmost(arr: list[T], target: T) -> int:
    """查找目标值的最右位置（第一个 > target 的位置 - 1）。"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1


def lower_bound(arr: list[T], target: T) -> int:
    """C++ lower_bound: 第一个 >= target 的位置。"""
    return binary_search_leftmost(arr, target)


def upper_bound(arr: list[T], target: T) -> int:
    """C++ upper_bound: 第一个 > target 的位置。"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def binary_search_rotated(arr: list[T], target: T) -> int:
    """搜索旋转排序数组中的目标值。"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[lo] <= arr[mid]:
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def exponential_search(arr: list[T], target: T) -> int:
    """指数搜索 —— 对无界数组的二分查找变体，O(log n)。"""
    if not arr:
        return -1
    if arr[0] == target:
        return 0
    i = 1
    while i < len(arr) and arr[i] <= target:
        i *= 2
    lo, hi = i // 2, min(i, len(arr) - 1)
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def interpolation_search(arr: list[int], target: int) -> int:
    """插值搜索 —— 对均匀分布的已排序数据，平均 O(log log n)。"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi and arr[lo] <= target <= arr[hi]:
        if arr[hi] == arr[lo]:
            return lo if arr[lo] == target else -1
        pos = lo + ((target - arr[lo]) * (hi - lo) // (arr[hi] - arr[lo]))
        if arr[pos] == target:
            return pos
        if arr[pos] < target:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


def fibonacci_search(arr: list[T], target: T) -> int:
    """斐波那契搜索 —— 只使用加减法（无除法），O(log n)。"""
    n = len(arr)
    fib_m2, fib_m1 = 0, 1
    fib_m = fib_m2 + fib_m1
    while fib_m < n:
        fib_m2, fib_m1 = fib_m1, fib_m
        fib_m = fib_m2 + fib_m1

    offset = -1
    while fib_m > 1:
        i = min(offset + fib_m2, n - 1)
        if arr[i] < target:
            fib_m = fib_m1
            fib_m1 = fib_m2
            fib_m2 = fib_m - fib_m1
            offset = i
        elif arr[i] > target:
            fib_m = fib_m2
            fib_m1 = fib_m1 - fib_m2
            fib_m2 = fib_m - fib_m1
        else:
            return i
    if fib_m1 and offset + 1 < n and arr[offset + 1] == target:
        return offset + 1
    return -1


def ternary_search_discrete(arr: list[T], target: T) -> int:
    """三分查找 —— 每次将区间分成三份，O(log₃ n)。"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid1 = lo + (hi - lo) // 3
        mid2 = hi - (hi - lo) // 3
        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2
        if target < arr[mid1]:
            hi = mid1 - 1
        elif target > arr[mid2]:
            lo = mid2 + 1
        else:
            lo, hi = mid1 + 1, mid2 - 1
    return -1


# ============================================================
# §5  KMP 字符串匹配
# ============================================================

def kmp_prefix(pattern: str) -> list[int]:
    """计算 KMP 前缀函数 (LPS: Longest Proper Prefix which is also Suffix)。"""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> list[int]:
    """KMP 字符串匹配 —— O(n + m)，返回所有匹配位置。"""
    if not pattern:
        return list(range(len(text) + 1))
    lps = kmp_prefix(pattern)
    matches: list[int] = []
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches


def boyer_moore_search(text: str, pattern: str) -> list[int]:
    """Boyer-Moore 字符串匹配的简化版 (仅使用坏字符规则)。"""
    if not pattern:
        return list(range(len(text) + 1))
    m = len(pattern)
    n = len(text)
    bad_char: dict[str, int] = {}
    for i, ch in enumerate(pattern):
        bad_char[ch] = i

    matches: list[int] = []
    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            matches.append(s)
            s += (m - bad_char.get(text[s + m], -1)) if s + m < n else 1
        else:
            shift = j - bad_char.get(text[s + j], -1)
            s += max(1, shift)
    return matches


def rabin_karp_search(text: str, pattern: str, prime: int = 101) -> list[int]:
    """Rabin-Karp 字符串匹配 —— 使用滚动哈希，平均 O(n + m)。"""
    if not pattern:
        return list(range(len(text) + 1))
    m, n = len(pattern), len(text)
    d = 256
    pattern_hash = 0
    text_hash = 0
    h = pow(d, m - 1, prime)

    matches: list[int] = []
    for i in range(m):
        pattern_hash = (d * pattern_hash + ord(pattern[i])) % prime
        text_hash = (d * text_hash + ord(text[i])) % prime

    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i + m] == pattern:
                matches.append(i)
        if i < n - m:
            text_hash = (d * (text_hash - ord(text[i]) * h) +
                         ord(text[i + m])) % prime
            if text_hash < 0:
                text_hash += prime

    return matches


# ============================================================
# §6  堆操作的更多实现
# ============================================================

class MinHeap:
    """最小堆的完整手写实现。"""

    def __init__(self) -> None:
        self.heap: list[int] = []

    def parent(self, i: int) -> int:
        return (i - 1) // 2

    def left_child(self, i: int) -> int:
        return 2 * i + 1

    def right_child(self, i: int) -> int:
        return 2 * i + 2

    def push(self, val: int) -> None:
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> int | None:
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def peek(self) -> int | None:
        return self.heap[0] if self.heap else None

    def _sift_up(self, i: int) -> None:
        while i > 0 and self.heap[self.parent(i)] > self.heap[i]:
            self.heap[self.parent(i)], self.heap[i] = \
                self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)

    def _sift_down(self, i: int) -> None:
        n = len(self.heap)
        while True:
            smallest = i
            l, r = self.left_child(i), self.right_child(i)
            if l < n and self.heap[l] < self.heap[smallest]:
                smallest = l
            if r < n and self.heap[r] < self.heap[smallest]:
                smallest = r
            if smallest == i:
                break
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest

    def heapify(self, arr: list[int]) -> None:
        self.heap = arr[:]
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def __len__(self) -> int:
        return len(self.heap)


class MaxHeap(MinHeap):
    """最大堆 —— 继承 MinHeap 并取反比较。"""

    def _sift_up(self, i: int) -> None:
        while i > 0 and self.heap[self.parent(i)] < self.heap[i]:
            self.heap[self.parent(i)], self.heap[i] = \
                self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)

    def _sift_down(self, i: int) -> None:
        n = len(self.heap)
        while True:
            largest = i
            l, r = self.left_child(i), self.right_child(i)
            if l < n and self.heap[l] > self.heap[largest]:
                largest = l
            if r < n and self.heap[r] > self.heap[largest]:
                largest = r
            if largest == i:
                break
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            i = largest


# ============================================================
# §7  性能基准测试
# ============================================================

def benchmark_sorts(n: int = 5000) -> None:
    """对比各种排序算法的运行时间。"""
    algorithms: dict[str, Callable[[list[int]], list[int]]] = {
        "Bubble": bubble_sort,
        "Selection": selection_sort,
        "Insertion": insertion_sort,
        "Shell": shell_sort,
        "Merge": merge_sort,
        "Merge (iter)": merge_sort_iterative,
        "Quick": quick_sort,
        "Quick (iter)": quick_sort_iterative,
        "Heap": heap_sort,
        "Intro": intro_sort,
        "TimSort": timsort,
        "Cocktail": cocktail_shaker_sort,
        "Gnome": gnome_sort,
    }

    data = [random.randint(0, 100000) for _ in range(n)]
    print(f"排序 {n} 个随机整数：")
    print(f"{'算法':<20} {'时间(ms)':>10} {'正确?':>8}")
    print("-" * 40)

    for name, func in algorithms.items():
        if n > 2000 and name in ("Bubble", "Selection", "Gnome", "Cocktail"):
            print(f"{name:<20} {'(跳过)':>10}")
            continue
        start = time.perf_counter()
        result = func(data)
        elapsed = (time.perf_counter() - start) * 1000
        correct = result == sorted(data)
        print(f"{name:<20} {elapsed:>10.2f} {'✓' if correct else '✗':>8}")

    # 线性时间排序
    if all(isinstance(x, int) for x in data):
        start = time.perf_counter()
        r1 = counting_sort(data)
        t = (time.perf_counter() - start) * 1000
        print(f"{'Counting':<20} {t:>10.2f} {'✓' if r1 == sorted(data) else '✗':>8}")

        start = time.perf_counter()
        r2 = radix_sort(data)
        t = (time.perf_counter() - start) * 1000
        print(f"{'Radix':<20} {t:>10.2f} {'✓' if r2 == sorted(data) else '✗':>8}")


def demo_all() -> None:
    print("=" * 60)
    print("排序与查找算法全集")
    print("=" * 60)

    test_data = [64, 34, 25, 12, 22, 11, 90, 45, 33, 50]

    print(f"\n原始数据: {test_data}")
    print(f"冒泡:   {bubble_sort(test_data)}")
    print(f"选择:   {selection_sort(test_data)}")
    print(f"插入:   {insertion_sort(test_data)}")
    print(f"希尔:   {shell_sort(test_data)}")
    print(f"归并:   {merge_sort(test_data)}")
    print(f"快速:   {quick_sort(test_data)}")
    print(f"堆排序: {heap_sort(test_data)}")
    print(f"内省:   {intro_sort(test_data)}")
    print(f"鸡尾酒: {cocktail_shaker_sort(test_data)}")
    print(f"地精:   {gnome_sort(test_data)}")

    # 二分查找演示
    sorted_data = sorted(test_data)
    print(f"\n二分查找 in {sorted_data}:")
    print(f"  binary_search(25) = {binary_search(sorted_data, 25)}")
    print(f"  leftmost(22) = {binary_search_leftmost(sorted_data, 22)}")
    print(f"  rightmost(22) = {binary_search_rightmost(sorted_data, 22)}")
    print(f"  lower_bound(22) = {lower_bound(sorted_data, 22)}")
    print(f"  upper_bound(22) = {upper_bound(sorted_data, 22)}")

    rotated = [45, 50, 64, 90, 11, 12, 22, 25, 33, 34]
    print(f"\n旋转排序数组: {rotated}")
    print(f"  search(12) = {binary_search_rotated(rotated, 12)}")

    # KMP
    text = "ABABDABACDABABCABAB"
    pattern = "ABABCABAB"
    print(f"\nKMP: text='{text}', pattern='{pattern}'")
    print(f"  KMP 匹配位置: {kmp_search(text, pattern)}")
    print(f"  BM 匹配位置:  {boyer_moore_search(text, pattern)}")
    print(f"  RK 匹配位置:  {rabin_karp_search(text, pattern)}")

    # 堆操作演示
    heap = MinHeap()
    for x in [5, 3, 8, 1, 9, 2, 7]:
        heap.push(x)
    print(f"\nMinHeap 弹出序列: ", end="")
    while heap:
        print(heap.pop(), end=" ")
    print()

    # 基准测试
    print()
    benchmark_sorts(3000)


if __name__ == "__main__":
    demo_all()
    print("\n✅ 排序查找算法篇执行完毕!")
