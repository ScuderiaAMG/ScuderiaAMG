#!/usr/bin/env python3
"""
NumPy 基础 —— 数值计算基石
涵盖：ndarray 创建与属性、索引与切片、广播机制、通用函数 (ufunc)、
      线性代数、随机数、结构化数组、内存布局、性能优化技巧
"""

import numpy as np
import time
from numpy import random as npr
from numpy import linalg as la


# ============================================================
# §1  ndarray 创建与属性
# ============================================================

def demo_array_creation() -> None:
    print("=" * 60)
    print("§1  ndarray 创建与属性")
    print("=" * 60)

    # 从列表创建
    a1 = np.array([1, 2, 3, 4, 5])
    a2 = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
    print(f"1D: {a1}, dtype={a1.dtype}, shape={a1.shape}, ndim={a1.ndim}")
    print(f"2D:\n{a2}, dtype={a2.dtype}")

    # 内建函数创建
    zeros = np.zeros((3, 4))                     # 全 0
    ones = np.ones((2, 3))                       # 全 1
    eye = np.eye(4)                              # 单位矩阵
    full = np.full((2, 3), 7.5)                  # 填充值
    diag = np.diag([1, 2, 3, 4])                 # 对角矩阵
    print(f"zeros(3,4):\n{zeros}")
    print(f"eye(4):\n{eye}")
    print(f"diag([1,2,3,4]):\n{diag}")

    # 序列生成
    arange_arr = np.arange(0, 10, 2)             # 步长 2
    linspace_arr = np.linspace(0, 1, 5)          # 均匀 5 个点
    logspace_arr = np.logspace(0, 3, 4)          # 对数刻度: 10^0, 10^1, 10^2, 10^3
    print(f"arange(0,10,2):  {arange_arr}")
    print(f"linspace(0,1,5): {linspace_arr}")
    print(f"logspace(0,3,4): {logspace_arr}")

    # 从函数生成
    fromfunction = np.fromfunction(lambda i, j: i + j, (3, 3), dtype=int)
    print(f"fromfunction(i+j):\n{fromfunction}")

    # 属性
    arr = np.random.randn(3, 4, 5)
    print(f"\nRandom array: shape={arr.shape}, ndim={arr.ndim}, "
          f"size={arr.size}, itemsize={arr.itemsize} bytes, "
          f"nbytes={arr.nbytes} bytes ({arr.nbytes / 1024:.1f} KB)")


# ============================================================
# §2  索引与切片
# ============================================================

def demo_indexing() -> None:
    print("\n" + "=" * 60)
    print("§2  索引与切片")
    print("=" * 60)

    arr = np.arange(24).reshape(4, 6)
    print(f"原始数组 (4x6):\n{arr}")

    # 基础切片
    print(f"\narr[1, 2]        = {arr[1, 2]}")
    print(f"arr[1:3, 2:5]    =\n{arr[1:3, 2:5]}")
    print(f"arr[:, ::2]       =\n{arr[:, ::2]}")     # 所有行，每隔一列

    # 花式索引 (fancy indexing)
    print(f"arr[[0, 2, 3]]   =\n{arr[[0, 2, 3]]}")   # 整数数组索引
    print(f"arr[[0, 3], [1, 4]] = {arr[[0, 3], [1, 4]]}")  # (0,1) 和 (3,4)

    # 布尔索引
    mask = arr % 5 == 0
    print(f"arr[arr % 5 == 0] = {arr[mask]}")
    arr[mask] = -1
    print(f"赋值后:\n{arr}")

    # np.where
    arr2 = np.arange(12).reshape(3, 4)
    indices = np.where(arr2 > 5)
    result_where = np.where(arr2 > 5, arr2 * 10, arr2)
    print(f"np.where(arr2>5, *10, keep):\n{result_where}")
    print(f"条件索引位置: {indices}")

    # np.take / np.put
    src = np.array([10, 20, 30, 40, 50])
    print(f"np.take(src, [0, 2, 4]) = {np.take(src, [0, 2, 4])}")

    # 省略号 (Ellipsis) — 对于高维数组
    arr3d = np.arange(60).reshape(3, 4, 5)
    print(f"arr3d[0, ...] =\n{arr3d[0, ...]}")        # 等价于 arr3d[0, :, :]
    print(f"arr3d[..., 0] =\n{arr3d[..., 0]}")        # 等价于 arr3d[:, :, 0]


# ============================================================
# §3  广播 (Broadcasting)
# ============================================================

def demo_broadcasting() -> None:
    print("\n" + "=" * 60)
    print("§3  广播 (Broadcasting)")
    print("=" * 60)

    # 规则：从后往前对齐维度，兼容的情况：
    #   1) 维度相等
    #   2) 某维度为 1
    a = np.array([[1, 2, 3], [4, 5, 6]])        # shape (2, 3)
    b = np.array([10, 20, 30])                   # shape (3,)
    c = np.array([[100], [200]])                 # shape (2, 1)
    d = np.array(5)                              # shape () 标量

    print(f"a (2,3) + b (3,):\n{a + b}")         # b 被广播为 (1,3) -> (2,3)
    print(f"a (2,3) + c (2,1):\n{a + c}")        # c 被广播为 (2,3)
    print(f"a + b + c:\n{a + b + c}")            # 复杂的多重广播

    # 显式广播
    a_broad, b_broad = np.broadcast_arrays(a, c)
    print(f"broadcast_arrays(a, c) -> shapes: {a_broad.shape}, {b_broad.shape}")

    # 实用案例：数据中心化
    data = np.random.randn(100, 5)               # 100 个样本，5 个特征
    mean = data.mean(axis=0)                     # shape (5,)
    centered = data - mean                       # (100,5) - (5,) 广播
    print(f"中心化: 原始均值={data.mean(axis=0)[:3]}, 中心化后均值={centered.mean(axis=0)[:3]}")

    # 实用案例：外积
    x = np.array([1, 2, 3])
    y = np.array([4, 5])
    outer = x[:, np.newaxis] * y[np.newaxis, :]
    print(f"外积 x[:,None]*y[None,:]:\n{outer}")

    # meshgrid
    xs, ys = np.meshgrid(np.linspace(-1, 1, 3), np.linspace(-1, 1, 3))
    print(f"meshgrid xs:\n{xs}")
    print(f"meshgrid ys:\n{ys}")


# ============================================================
# §4  通用函数 (ufunc) 与向量化
# ============================================================

def demo_ufunc() -> None:
    print("\n" + "=" * 60)
    print("§4  通用函数 (ufunc)")
    print("=" * 60)

    arr = np.linspace(0, np.pi, 6)

    # 一元 ufunc
    print(f"sin({arr}) = {np.sin(arr)}")
    print(f"exp({arr}) = {np.exp(arr)}")
    print(f"log(1+{arr}) = {np.log1p(arr)}")      # log(1+x) 对小 x 更精确
    print(f"sqrt({arr}) = {np.sqrt(arr)}")

    # 二元 ufunc
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    print(f"add:          {np.add(x, y)}")
    print(f"multiply:     {np.multiply(x, y)}")
    print(f"power:        {np.power(x, y)}")
    print(f"maximum:      {np.maximum(x, y)}")
    print(f"mod:          {np.mod(y, x)}")

    # ufunc 方法
    # reduce
    print(f"np.add.reduce([1,2,3,4,5]) = {np.add.reduce([1, 2, 3, 4, 5])}")  # 累加
    # accumulate
    print(f"np.add.accumulate([1,2,3,4,5]) = {np.add.accumulate([1, 2, 3, 4, 5])}")
    # outer
    print(f"np.multiply.outer([1,2],[3,4,5]):\n{np.multiply.outer([1, 2], [3, 4, 5])}")
    # reduceat
    arr_a = np.arange(10)
    print(f"np.add.reduceat(range(10), [0,5,7]): {np.add.reduceat(arr_a, [0, 5, 7])}")

    # 自定义 ufunc (frompyfunc)
    def classify(x: float) -> str:
        return "low" if x < 0.33 else ("mid" if x < 0.67 else "high")

    classify_ufunc = np.frompyfunc(classify, 1, 1)
    vals = np.linspace(0, 1, 9)
    print(f"classify_ufunc: {classify_ufunc(vals)}")
    # 注意：frompyfunc 返回 object 数组，速度慢；生产环境用 np.vectorize 或 np.select
    conditions = [vals < 0.33, vals < 0.67, vals >= 0.67]
    choices = ["low", "mid", "high"]
    classified = np.select(conditions, choices, default="unknown")
    print(f"np.select 版本: {classified}")

    # 向量化 vs 循环性能对比
    n = 1_000_000
    big_arr = np.random.randn(n)

    t0 = time.perf_counter()
    _ = np.sqrt(big_arr)
    vec_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    _ = [x ** 0.5 for x in big_arr]
    loop_time = time.perf_counter() - t0

    print(f"\n性能对比 (n={n:,}):")
    print(f"  np.sqrt:      {vec_time*1000:.1f} ms")
    print(f"  list comp:    {loop_time*1000:.1f} ms")
    print(f"  加速比:        {loop_time/vec_time:.1f}x")


# ============================================================
# §5  线性代数
# ============================================================

def demo_linalg() -> None:
    print("\n" + "=" * 60)
    print("§5  线性代数")
    print("=" * 60)

    # 矩阵乘法
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    print(f"A @ B =\n{A @ B}")
    print(f"np.dot(A, B) =\n{np.dot(A, B)}")
    print(f"np.matmul(A, B) =\n{np.matmul(A, B)}")

    # 内积 / 外积
    v1 = np.array([1, 2, 3])
    v2 = np.array([4, 5, 6])
    print(f"inner(v1,v2) = {np.inner(v1, v2)}")    # 内积
    print(f"outer(v1,v2) =\n{np.outer(v1, v2)}")    # 外积
    print(f"cross(v1,v2) = {np.cross(v1, v2)}")     # 叉积 (仅 3D)

    # 矩阵分解
    A2 = np.array([[4, 2], [1, 3]], dtype=float)

    # 特征值/特征向量
    eigenvalues, eigenvectors = la.eig(A2)
    print(f"特征值: {eigenvalues}")
    print(f"特征向量:\n{eigenvectors}")

    # SVD
    U, S, Vt = la.svd(A2)
    print(f"SVD: S = {S}")
    reconstructed = U @ np.diag(S) @ Vt
    print(f"重建误差: {np.abs(A2 - reconstructed).max():.2e}")

    # QR 分解
    Q, R = la.qr(A2)
    print(f"QR: Q=\n{Q}, R=\n{R}")

    # 求解线性方程组 Ax = b
    A3 = np.array([[3, 1], [1, 2]])
    b = np.array([9, 8])
    x_solve = la.solve(A3, b)
    print(f"解 Ax=b: x = {x_solve}")
    print(f"验证 A@x = {A3 @ x_solve}")

    # 最小二乘
    A_over = np.array([[1, 1], [1, 2], [1, 3]])  # 3x2 超定
    b_over = np.array([6, 9, 12])
    x_lstsq, residuals, rank, singular = la.lstsq(A_over, b_over, rcond=None)
    print(f"\n最小二乘 x = {x_lstsq}")
    print(f"残差: {residuals}")

    # 行列式 / 逆矩阵 / 伪逆
    print(f"det(A2) = {la.det(A2):.2f}")
    print(f"inv(A2) =\n{la.inv(A2)}")
    print(f"pinv(A2) =\n{la.pinv(A2)}")            # 伪逆 (Moore-Penrose)

    # 范数
    print(f"Frobenius norm of A2: {la.norm(A2, 'fro'):.3f}")
    print(f"L2 norm of A2: {la.norm(A2, 2):.3f}")


# ============================================================
# §6  随机数
# ============================================================

def demo_random() -> None:
    print("\n" + "=" * 60)
    print("§6  随机数生成")
    print("=" * 60)

    # 随机数生成器 (推荐方式 — NumPy 1.17+)
    rng = np.random.default_rng(seed=42)

    # 基础分布
    print(f"uniform(0,1,5):     {rng.uniform(0, 1, 5)}")
    print(f"normal(0,1,(2,3)):\n{rng.normal(0, 1, (2, 3))}")
    print(f"integers(1,10,10):  {rng.integers(1, 10, 10)}")
    print(f"choice([1,2,3], 5, p=[0.2,0.3,0.5]): "
          f"{rng.choice([1, 2, 3], 5, p=[0.2, 0.3, 0.5])}")

    # 更多分布
    print(f"binomial(n=10,p=0.5,size=5): {rng.binomial(10, 0.5, 5)}")
    print(f"poisson(lam=3, size=5): {rng.poisson(3, 5)}")
    print(f"exponential(scale=1, size=5): {rng.exponential(1, 5)}")
    print(f"gamma(shape=2,scale=1,size=5): {rng.gamma(2, 1, 5)}")
    print(f"beta(a=0.5,b=0.5,size=5): {rng.beta(0.5, 0.5, 5)}")

    # 随机排列
    arr = np.arange(10)
    rng.shuffle(arr)
    print(f"shuffle: {arr}")
    perm = rng.permutation(10)
    print(f"permutation: {perm}")

    # 从多项分布中抽样
    probs = [0.1, 0.3, 0.4, 0.2]
    samples = rng.multinomial(100, probs, size=3)
    print(f"multinomial(100,{probs},3):\n{samples}")

    # 蒙特卡洛：估算 π
    n_mc = 100_000
    points = rng.uniform(-1, 1, (n_mc, 2))
    in_circle = np.sum(points[:, 0]**2 + points[:, 1]**2 <= 1)
    pi_est = 4 * in_circle / n_mc
    print(f"蒙特卡洛 π ≈ {pi_est:.6f} (误差 {abs(np.pi - pi_est):.6f})")


# ============================================================
# §7  高级操作与技巧
# ============================================================

def demo_advanced_operations() -> None:
    print("\n" + "=" * 60)
    print("§7  高级操作与技巧")
    print("=" * 60)

    # 沿轴操作
    arr = np.arange(24).reshape(2, 3, 4)
    print(f"arr (2,3,4):")
    print(f"  axis=0 sum:\n{arr.sum(axis=0)}")
    print(f"  axis=1 max:\n{arr.max(axis=1)}")
    print(f"  axis=2 argmax:\n{arr.argmax(axis=2)}")

    # 排序
    to_sort = np.array([3, 1, 4, 1, 5, 9, 2, 6])
    print(f"np.sort:       {np.sort(to_sort)}")
    print(f"np.argsort:    {np.argsort(to_sort)}")
    print(f"np.partition:  {np.partition(to_sort, 3)}")   # 第 k 小元素在位置 3

    # 唯一值与计数
    vals = np.array([1, 1, 2, 3, 3, 3, 4, 5, 5])
    uniq, counts = np.unique(vals, return_counts=True)
    print(f"unique: {uniq}, counts: {counts}")

    # 结构化数组
    dtype = np.dtype([("name", "U10"), ("age", "i4"), ("score", "f8")])
    students = np.array([
        ("Alice", 20, 90.5),
        ("Bob", 22, 85.0),
        ("Charlie", 19, 92.3),
    ], dtype=dtype)
    print(f"students['name']: {students['name']}")
    print(f"students['score'].mean(): {students['score'].mean():.2f}")

    # 内存布局 C vs F
    c_order = np.ones((1000, 1000))
    f_order = np.asfortranarray(c_order.copy())
    print(f"C-order flags: {c_order.flags['C_CONTIGUOUS']}, F_CONTIGUOUS={c_order.flags['F_CONTIGUOUS']}")
    # 沿不同轴求和性能差异
    t0 = time.perf_counter()
    _ = c_order.sum(axis=0)                      # C-order 列求和 — 跨步大
    t_c = time.perf_counter() - t0
    t0 = time.perf_counter()
    _ = c_order.sum(axis=1)                      # C-order 行求和 — 连续读取
    t_f = time.perf_counter() - t0
    print(f"C-order: axis=0 sum={t_c*1000:.2f}ms, axis=1 sum={t_f*1000:.2f}ms")

    # np.einsum — 爱因斯坦求和约定
    a = np.arange(6).reshape(2, 3)
    b = np.arange(15).reshape(3, 5)
    # 等价于 a @ b
    matmul_einsum = np.einsum("ij,jk->ik", a, b)
    print(f"einsum matmul:\n{matmul_einsum}")
    # Trace
    m = np.arange(9).reshape(3, 3)
    print(f"einsum trace: {np.einsum('ii->', m)}")
    # 对角线
    print(f"einsum diag:  {np.einsum('ii->i', m)}")

    # 窗函数
    windowed = np.lib.stride_tricks.sliding_window_view(
        np.arange(10), window_shape=3
    )
    print(f"sliding_window(10, 3):\n{windowed}")

    # concatenate / stack / split
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    print(f"np.concatenate([x,y]): {np.concatenate([x, y])}")
    print(f"np.stack([x,y], axis=0):\n{np.stack([x, y], axis=0)}")
    print(f"np.stack([x,y], axis=1):\n{np.stack([x, y], axis=1)}")
    print(f"np.hstack: {np.hstack([x, y])}")
    print(f"np.vstack:\n{np.vstack([x, y])}")

    left, right = np.split(np.arange(10), [3])
    print(f"np.split(range(10), [3]): left={left}, right={right}")


if __name__ == "__main__":
    demo_array_creation()
    demo_indexing()
    demo_broadcasting()
    demo_ufunc()
    demo_linalg()
    demo_random()
    demo_advanced_operations()
    print("\n✅ NumPy 基础篇全部执行完毕!")
