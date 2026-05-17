#!/usr/bin/env python3
"""
动态规划全集 —— 从入门到进阶
涵盖：斐波那契(记忆化/递推)、0-1背包/完全背包/多重背包、
      最长公共子序列(LCS)/最长递增子序列(LIS)、编辑距离、
      矩阵链乘法、硬币找零、切钢条、区间DP、树形DP、
      状态压缩DP、概率DP、数位DP
"""

from functools import lru_cache
from typing import Any
import math


# ============================================================
# §1  基础：记忆化与递推
# ============================================================

def fib_memo(n: int) -> int:
    """斐波那契 —— 记忆化递归 (Top-Down)。"""
    memo: dict[int, int] = {}

    def dp(k: int) -> int:
        if k <= 1:
            return k
        if k not in memo:
            memo[k] = dp(k - 1) + dp(k - 2)
        return memo[k]

    return dp(n)


def fib_tabulation(n: int) -> int:
    """斐波那契 —— 递推 (Bottom-Up), O(n) / O(1) 空间优化。"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fib_matrix(n: int) -> int:
    """斐波那契 —— 矩阵快速幂, O(log n)。"""
    def mat_mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        return (
            a[0]*b[0] + a[1]*b[2], a[0]*b[1] + a[1]*b[3],
            a[2]*b[0] + a[3]*b[2], a[2]*b[1] + a[3]*b[3],
        )

    def mat_pow(mat: tuple[int, ...], exp: int) -> tuple[int, ...]:
        result = (1, 0, 0, 1)
        base = mat
        while exp:
            if exp & 1:
                result = mat_mul(result, base)
            base = mat_mul(base, base)
            exp >>= 1
        return result

    if n <= 1:
        return n
    result = mat_pow((1, 1, 1, 0), n - 1)
    return result[0]


# ============================================================
# §2  背包问题
# ============================================================

def knapsack_01(weights: list[int], values: list[int],
                capacity: int) -> int:
    """0-1 背包 —— 每件物品选或不选, O(n*C)。"""
    n = len(weights)
    dp = [0] * (capacity + 1)
    for i in range(n):
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]


def knapsack_01_with_items(weights: list[int], values: list[int],
                           capacity: int) -> tuple[int, list[int]]:
    """0-1 背包 —— 同时返回选择了哪些物品。"""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if w >= weights[i - 1]:
                dp[i][w] = max(dp[i][w],
                               dp[i - 1][w - weights[i - 1]] + values[i - 1])

    # 回溯物品
    selected: list[int] = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)
            w -= weights[i - 1]

    return dp[n][capacity], selected[::-1]


def knapsack_complete(weights: list[int], values: list[int],
                      capacity: int) -> int:
    """完全背包 —— 每件物品可以选无限次, O(n*C)。"""
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for w in range(weights[i], capacity + 1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]


def knapsack_multiple(weights: list[int], values: list[int],
                      counts: list[int], capacity: int) -> int:
    """多重背包 —— 使用二进制拆分优化, O(n*C*log count)。"""
    items: list[tuple[int, int]] = []
    for w, v, c in zip(weights, values, counts):
        k = 1
        while k <= c:
            items.append((w * k, v * k))
            c -= k
            k <<= 1
        if c > 0:
            items.append((w * c, v * c))

    dp = [0] * (capacity + 1)
    for w, v in items:
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]


def knapsack_unbounded_exact(weights: list[int], capacity: int) -> int:
    """完全背包求恰好装满的方案数。"""
    dp = [0] * (capacity + 1)
    dp[0] = 1
    for w in weights:
        for cap in range(w, capacity + 1):
            dp[cap] += dp[cap - w]
    return dp[capacity]


# ============================================================
# §3  最长公共子序列 & 最长递增子序列
# ============================================================

def lcs(s1: str, s2: str) -> int:
    """最长公共子序列长度 —— O(n*m)。"""
    n, m = len(s1), len(s2)
    dp = [0] * (m + 1)
    for i in range(1, n + 1):
        prev = 0
        for j in range(1, m + 1):
            temp = dp[j]
            if s1[i - 1] == s2[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = temp
    return dp[m]


def lcs_string(s1: str, s2: str) -> str:
    """最长公共子序列的具体内容。"""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 回溯
    result: list[str] = []
    i, j = n, m
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            result.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return "".join(reversed(result))


def lis(arr: list[int]) -> int:
    """最长递增子序列长度 —— O(n log n)（使用 patience sorting）。"""
    import bisect
    tails: list[int] = []
    for x in arr:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x
    return len(tails)


def lis_sequence(arr: list[int]) -> list[int]:
    """最长递增子序列的具体内容 —— O(n log n)。"""
    import bisect
    n = len(arr)
    tails: list[int] = []
    prev = [-1] * n
    indices: list[int] = []

    for i, x in enumerate(arr):
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
            indices.append(i)
        else:
            tails[idx] = x
            indices[idx] = i
        if idx > 0:
            prev[i] = indices[idx - 1]

    # 回溯
    result: list[int] = []
    idx = indices[-1]
    while idx != -1:
        result.append(arr[idx])
        idx = prev[idx]
    return result[::-1]


def lcs_of_three(s1: str, s2: str, s3: str) -> int:
    """三个字符串的 LCS —— O(n*m*k)。"""
    n, m, k = len(s1), len(s2), len(s3)
    dp = [[[0] * (k + 1) for _ in range(m + 1)] for __ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            for l in range(1, k + 1):
                if s1[i - 1] == s2[j - 1] == s3[l - 1]:
                    dp[i][j][l] = dp[i - 1][j - 1][l - 1] + 1
                else:
                    dp[i][j][l] = max(dp[i - 1][j][l], dp[i][j - 1][l],
                                      dp[i][j][l - 1])
    return dp[n][m][k]


# ============================================================
# §4  编辑距离
# ============================================================

def edit_distance(s1: str, s2: str) -> int:
    """Levenshtein 编辑距离 —— O(n*m)。"""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],       # 删除
                                   dp[i][j - 1],       # 插入
                                   dp[i - 1][j - 1])   # 替换
    return dp[n][m]


def edit_distance_operations(s1: str, s2: str) -> tuple[int, list[str]]:
    """编辑距离 + 具体操作序列。"""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    ops: list[list[str]] = [[""] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = i
        ops[i][0] = ops[i - 1][0] + f"DEL {s1[i-1]}; "
    for j in range(1, m + 1):
        dp[0][j] = j
        ops[0][j] = ops[0][j - 1] + f"INS {s2[j-1]}; "

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                ops[i][j] = ops[i - 1][j - 1]
            else:
                candidates = [
                    (dp[i - 1][j] + 1, ops[i - 1][j] + f"DEL {s1[i-1]}; "),
                    (dp[i][j - 1] + 1, ops[i][j - 1] + f"INS {s2[j-1]}; "),
                    (dp[i - 1][j - 1] + 1, ops[i - 1][j - 1] + f"SUB {s1[i-1]}->{s2[j-1]}; "),
                ]
                dp[i][j], ops[i][j] = min(candidates, key=lambda x: x[0])

    return dp[n][m], ops[n][m].rstrip("; ").split("; ")


# ============================================================
# §5  硬币找零与切钢条
# ============================================================

def coin_change(coins: list[int], amount: int) -> int:
    """最少硬币数 (每种硬币无限) —— O(n * amount)。"""
    INF = amount + 1
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1


def coin_change_count_ways(coins: list[int], amount: int) -> int:
    """凑出金额的方案数 (每种硬币无限)。"""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


def coin_change_limited(coins: list[int], counts: list[int],
                        amount: int) -> int:
    """有限硬币 —— 最少硬币数 (多重背包)。"""
    INF = amount + 1
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for c, cnt in zip(coins, counts):
        # 二进制拆分
        k = 1
        while k <= cnt:
            w = c * k
            for a in range(amount, w - 1, -1):
                dp[a] = min(dp[a], dp[a - w] + k)
            cnt -= k
            k <<= 1
        if cnt > 0:
            w = c * cnt
            for a in range(amount, w - 1, -1):
                dp[a] = min(dp[a], dp[a - w] + cnt)
    return dp[amount] if dp[amount] != INF else -1


def rod_cutting(prices: list[int]) -> int:
    """切钢条问题 —— O(n²)。prices[i] 是长度 i 的价格。"""
    n = len(prices)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        max_val = 0
        for j in range(1, i + 1):
            max_val = max(max_val, prices[j - 1] + dp[i - j])
        dp[i] = max_val
    return dp[n]


# ============================================================
# §6  矩阵链乘法
# ============================================================

def matrix_chain_order(dims: list[int]) -> tuple[int, str]:
    """矩阵链乘法 —— O(n³), 返回最小乘法次数和括号化方式。"""
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    splits = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float("inf")  # type: ignore[assignment]
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    splits[i][j] = k

    def build_parens(i: int, j: int) -> str:
        if i == j:
            return f"A{i}"
        k = splits[i][j]
        return f"({build_parens(i, k)} × {build_parens(k + 1, j)})"

    return int(dp[0][n - 1]), build_parens(0, n - 1)


# ============================================================
# §7  区间 DP
# ============================================================

def stone_merge(stones: list[int]) -> int:
    """石子合并 —— 线性区间 DP, O(n³)。"""
    n = len(stones)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + stones[i]

    INF = 10 ** 18
    dp = [[INF] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 0

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + prefix[j + 1] - prefix[i]
                dp[i][j] = min(dp[i][j], cost)

    return dp[0][n - 1]


def palindrome_partition(s: str) -> int:
    """回文串最少分割次数 —— O(n²)。"""
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]

    for i in range(n):
        is_pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length <= 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True

    dp = list(range(n))
    for i in range(n):
        if is_pal[0][i]:
            dp[i] = 0
        else:
            for j in range(i):
                if is_pal[j + 1][i]:
                    dp[i] = min(dp[i], dp[j] + 1)

    return dp[n - 1]


def burst_balloons(nums: list[int]) -> int:
    """戳气球 —— LeetCode 312, O(n³)。"""
    nums = [1] + [x for x in nums if x > 0] + [1]
    n = len(nums)
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n):
        for left in range(n - length):
            right = left + length
            for k in range(left + 1, right):
                dp[left][right] = max(
                    dp[left][right],
                    dp[left][k] + dp[k][right] + nums[left] * nums[k] * nums[right]
                )

    return dp[0][n - 1]


# ============================================================
# §8  状态压缩 DP
# ============================================================

def tsp_dp(dist: list[list[int]]) -> int:
    """旅行商问题 (TSP) —— Held-Karp 算法, O(n²·2ⁿ)。"""
    n = len(dist)
    INF = 10 ** 18
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0

    for mask in range(1 << n):
        for u in range(n):
            if not (mask >> u) & 1:
                continue
            if dp[mask][u] == INF:
                continue
            for v in range(n):
                if (mask >> v) & 1:
                    continue
                new_mask = mask | (1 << v)
                dp[new_mask][v] = min(dp[new_mask][v],
                                      dp[mask][u] + dist[u][v])

    full_mask = (1 << n) - 1
    return int(min(dp[full_mask][v] + dist[v][0] for v in range(n)))


def assignment_problem(cost: list[list[int]]) -> int:
    """指派问题 —— 状态压缩 DP, O(n·2ⁿ)。"""
    n = len(cost)
    INF = 10 ** 18
    dp = [INF] * (1 << n)
    dp[0] = 0

    for mask in range(1 << n):
        i = mask.bit_count()
        if i >= n:
            continue
        for j in range(n):
            if not (mask >> j) & 1:
                new_mask = mask | (1 << j)
                dp[new_mask] = min(dp[new_mask], dp[mask] + cost[i][j])

    return dp[(1 << n) - 1]


# ============================================================
# §9  树形 DP
# ============================================================

def tree_maximum_independent_set(adj: list[list[int]],
                                 root: int = 0) -> int:
    """树的最大独立集 —— 树形 DP O(n)。"""
    n = len(adj)
    dp = [[0, 0] for _ in range(n)]          # [不选, 选]
    visited = [False] * n

    def dfs(u: int) -> None:
        visited[u] = True
        dp[u][1] = 1
        for v in adj[u]:
            if not visited[v]:
                dfs(v)
                dp[u][0] += max(dp[v][0], dp[v][1])
                dp[u][1] += dp[v][0]

    dfs(root)
    return max(dp[root])


def tree_diameter(adj: list[list[int]]) -> int:
    """树的直径 —— 两遍 BFS/DFS（针对无向树）。"""
    n = len(adj)

    def farthest(start: int) -> tuple[int, int]:
        dist = [-1] * n
        q = [start]
        dist[start] = 0
        furthest_node = start
        for u in q:
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
                    if dist[v] > dist[furthest_node]:
                        furthest_node = v
        return furthest_node, dist[furthest_node]

    far_node, _ = farthest(0)
    _, diameter = farthest(far_node)
    return diameter


# ============================================================
# §10  概率 DP & 期望 DP
# ============================================================

def dice_rolls_probability(n: int, target: int) -> float:
    """n 个骰子掷出和为 target 的概率 —— O(n * target)。"""
    dp = [[0.0] * (target + 1) for _ in range(n + 1)]
    dp[0][0] = 1.0

    for i in range(1, n + 1):
        for s_val in range(i, min(target, 6 * i) + 1):
            for face in range(1, min(7, s_val + 1)):
                dp[i][s_val] += dp[i - 1][s_val - face] / 6.0

    return dp[n][target]


def random_walk_expected_steps(n: int) -> list[float]:
    """
    一维随机游走 —— 从位置 i 走到 0 或 n 的期望步数。
    状态转移: E[i] = 1 + 0.5*E[i-1] + 0.5*E[i+1]
    使用高斯消元或 DP 求解。
    """
    A = [[0.0] * (n + 1) for _ in range(n + 1)]
    b = [0.0] * (n + 1)

    A[0][0] = 1.0
    b[0] = 0.0
    A[n][n] = 1.0
    b[n] = 0.0

    for i in range(1, n):
        A[i][i - 1] = 0.5
        A[i][i] = -1.0
        A[i][i + 1] = 0.5
        b[i] = -1.0

    # 三对角矩阵: Thomas 算法
    a = [0.0] + [0.5] * (n - 1)
    c_val = [-1.0] * (n + 1)
    c_val[0] = 1.0
    c_val[n] = 1.0
    d = [0.5] * (n - 1) + [0.0]

    # 前向消元
    for i in range(1, n + 1):
        m = a[i] / c_val[i - 1]
        c_val[i] -= m * d[i - 1]
        b[i] -= m * b[i - 1]

    # 回代
    x = [0.0] * (n + 1)
    x[n] = b[n] / c_val[n]
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - d[i] * x[i + 1]) / c_val[i]

    return x


# ============================================================
# §11  数位 DP
# ============================================================

def count_digit_one(n: int) -> int:
    """统计 1 到 n 中数字 1 出现的次数 (LeetCode 233) —— 数位 DP。"""
    s = str(n)
    length = len(s)

    @lru_cache(maxsize=None)
    def dp(pos: int, tight: bool, count: int) -> int:
        if pos == length:
            return count
        limit = int(s[pos]) if tight else 9
        total = 0
        for d in range(limit + 1):
            total += dp(pos + 1,
                        tight and (d == limit),
                        count + (d == 1))
        return total

    return dp(0, True, 0)


def numbers_without_consecutive_ones(n: int) -> int:
    """统计 <= n 中不含连续 1 的数个数 (LeetCode 600) —— 数位 DP。"""
    s = bin(n)[2:]
    length = len(s)

    @lru_cache(maxsize=None)
    def dp(pos: int, prev_one: bool, tight: bool) -> int:
        if pos == length:
            return 1
        limit = int(s[pos]) if tight else 1
        total = 0
        for d in range(limit + 1):
            if d == 1 and prev_one:
                continue
            total += dp(pos + 1, d == 1, tight and (d == limit))
        return total

    return dp(0, False, True)


# ============================================================
# §12  演示
# ============================================================

def demo_dp() -> None:
    print("=" * 60)
    print("动态规划全集演示")
    print("=" * 60)

    print(f"Fib(30) Memo:    {fib_memo(30)}")
    print(f"Fib(30) Tab:     {fib_tabulation(30)}")
    print(f"Fib(30) Matrix:  {fib_matrix(30)}")

    w, v = [2, 3, 4, 5], [3, 4, 5, 6]
    print(f"\n0-1 背包 ({w}, {v}, cap=8): {knapsack_01(w, v, 8)}")
    max_val, items = knapsack_01_with_items(w, v, 8)
    print(f"  最大值={max_val}, 物品={items}")
    print(f"完全背包: {knapsack_complete(w, v, 8)}")
    print(f"多重背包: {knapsack_multiple(w, v, [2, 1, 3, 2], 8)}")

    print(f"\nLCS('AGGTAB','GXTXAYB'): {lcs('AGGTAB', 'GXTXAYB')}")
    print(f"LCS 内容: {lcs_string('AGGTAB', 'GXTXAYB')}")
    print(f"LIS([10,9,2,5,3,7,101,18]): {lis([10, 9, 2, 5, 3, 7, 101, 18])}")
    print(f"LIS 序列: {lis_sequence([10, 9, 2, 5, 3, 7, 101, 18])}")

    print(f"\n编辑距离('kitten','sitting'): {edit_distance('kitten', 'sitting')}")
    ed, ed_ops = edit_distance_operations("horse", "ros")
    print(f"编辑距离('horse','ros'): {ed}")
    print(f"  操作: {ed_ops}")

    coins = [1, 5, 10, 25]
    print(f"\n最少硬币 (coins={coins}, amount=63): {coin_change(coins, 63)}")
    print(f"方案数: {coin_change_count_ways(coins, 10)}")
    print(f"切钢条 (prices=[1,5,8,9,10,17,17,20]): {rod_cutting([1, 5, 8, 9, 10, 17, 17, 20])}")

    dims = [30, 35, 15, 5, 10, 20, 25]
    mcm_cost, mcm_parens = matrix_chain_order(dims)
    print(f"\n矩阵链乘法 (dims={dims}): 最小标量乘法={mcm_cost}")
    print(f"  括号化: {mcm_parens}")

    print(f"\n石子合并 [3,4,5,6,7]: {stone_merge([3, 4, 5, 6, 7])}")
    print(f"回文分割 'aab': {palindrome_partition('aab')}")
    print(f"戳气球 [3,1,5,8]: {burst_balloons([3, 1, 5, 8])}")

    tsp_dist = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0],
    ]
    print(f"\nTSP (4城市): {tsp_dp(tsp_dist)}")

    cost = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
    print(f"指派问题 最小成本: {assignment_problem(cost)}")

    tree = [[1, 2], [0, 3, 4], [0], [1], [1]]
    print(f"\n树最大独立集: {tree_maximum_independent_set(tree)}")
    print(f"树直径: {tree_diameter(tree)}")

    print(f"\n2骰子和为7的概率: {dice_rolls_probability(2, 7):.4f}")
    print(f"1到100中1出现次数: {count_digit_one(100)}")
    print(f"不含连续1的数(<=5): {numbers_without_consecutive_ones(5)}")


if __name__ == "__main__":
    demo_dp()
    print("\n✅ 动态规划篇执行完毕!")
