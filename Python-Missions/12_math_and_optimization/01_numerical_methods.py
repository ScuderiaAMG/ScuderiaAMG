#!/usr/bin/env python3
"""
数值方法与优化算法 —— 完整 Python 实现
涵盖：数值积分/微分、线性方程组求解(高斯消元/LU/Cholesky/共轭梯度)、
      非线性方程求根(二分法/牛顿法/割线法)、插值(拉格朗日/三次样条)、
      最优化(梯度下降/牛顿法/拟牛顿/L-BFGS/ADAM)、
      约束优化(拉格朗日乘子/内点法思路)、全局优化(模拟退火/遗传算法)、
      常微分方程数值解(欧拉/RK4)、傅里叶变换基础
"""

import numpy as np
from typing import Any, Callable
import math
import random

rng = np.random.default_rng(42)


# ============================================================
# §1  数值积分
# ============================================================

def trapezoidal_rule(f: Callable[[float], float], a: float, b: float,
                     n: int = 1000) -> float:
    """复化梯形公式 —— O(n)。"""
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return total * h


def simpson_rule(f: Callable[[float], float], a: float, b: float,
                 n: int = 1000) -> float:
    """Simpson 1/3 法则 —— 要求 n 为偶数, 误差 O(h^4)。"""
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    result = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        result += 4 * f(x) if i % 2 == 1 else 2 * f(x)
    return result * h / 3


def gaussian_quadrature(f: Callable[[float], float], a: float, b: float,
                        n: int = 5) -> float:
    """高斯-勒让德积分 —— n 点, 精度 2n-1 阶。"""
    # 预计算的 Gauss-Legendre 节点和权重（n=5）
    nodes_weights = {
        1: ([0.0], [2.0]),
        2: ([-0.5773502691896257, 0.5773502691896257],
            [1.0, 1.0]),
        3: ([-0.7745966692414834, 0.0, 0.7745966692414834],
            [0.5555555555555556, 0.8888888888888888, 0.5555555555555556]),
        4: ([-0.8611363115940526, -0.3399810435848563,
             0.3399810435848563, 0.8611363115940526],
            [0.3478548451374538, 0.6521451548625461,
             0.6521451548625461, 0.3478548451374538]),
        5: ([-0.9061798459386640, -0.5384693101056831, 0.0,
             0.5384693101056831, 0.9061798459386640],
            [0.2369268850561891, 0.4786286704993665, 0.5888888888888889,
             0.4786286704993665, 0.2369268850561891]),
    }

    n = min(n, 5)
    nodes, weights = nodes_weights[n]

    mid = (b + a) / 2
    half_range = (b - a) / 2
    result = 0.0
    for xi, wi in zip(nodes, weights):
        result += wi * f(mid + half_range * xi)
    return result * half_range


def monte_carlo_integral(f: Callable[[np.ndarray], float],
                         bounds: list[tuple[float, float]],
                         n: int = 100000) -> tuple[float, float]:
    """蒙特卡洛积分 —— 高维积分的实用方法。"""
    dim = len(bounds)
    volume = 1.0
    for lo, hi in bounds:
        volume *= (hi - lo)

    samples = np.zeros((n, dim))
    for d, (lo, hi) in enumerate(bounds):
        samples[:, d] = rng.uniform(lo, hi, n)

    values = np.array([f(samples[i]) for i in range(n)])
    estimate = volume * values.mean()
    error = volume * values.std() / np.sqrt(n)
    return estimate, error


# ============================================================
# §2  数值微分
# ============================================================

def finite_difference(f: Callable[[float], float], x: float,
                      h: float = 1e-6, method: str = "central") -> float:
    """有限差分法求导。"""
    if method == "forward":
        return (f(x + h) - f(x)) / h
    elif method == "backward":
        return (f(x) - f(x - h)) / h
    elif method == "central":
        return (f(x + h) - f(x - h)) / (2 * h)
    elif method == "second":
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h ** 2)
    else:
        raise ValueError(f"未知方法: {method}")


def jacobian(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
             h: float = 1e-6) -> np.ndarray:
    """数值雅可比矩阵。"""
    n_output = len(f(x))
    n_input = len(x)
    J = np.zeros((n_output, n_input))
    fx = f(x)

    for i in range(n_input):
        x_perturbed = x.copy()
        x_perturbed[i] += h
        J[:, i] = (f(x_perturbed) - fx) / h

    return J


def hessian(f: Callable[[np.ndarray], float], x: np.ndarray,
            h: float = 1e-4) -> np.ndarray:
    """数值 Hessian 矩阵。"""
    n = len(x)
    H = np.zeros((n, n))
    fx = f(x)

    for i in range(n):
        for j in range(i, n):
            x1 = x.copy()
            x2 = x.copy()
            x3 = x.copy()
            x4 = x.copy()

            x1[i] += h
            x1[j] += h
            x2[i] += h
            x3[j] += h
            # x4 = x

            H[i, j] = (f(x1) - f(x2) - f(x3) + fx) / (h ** 2)
            if i != j:
                H[j, i] = H[i, j]

    return H


# ============================================================
# §3  线性方程组求解
# ============================================================

def gaussian_elimination(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """高斯消元法 (带部分主元)。"""
    n = len(A)
    Ab = np.column_stack([A.astype(np.float64), b.astype(np.float64)])

    for k in range(n):
        # 部分主元
        pivot_row = k + np.argmax(np.abs(Ab[k:, k]))
        if pivot_row != k:
            Ab[[k, pivot_row]] = Ab[[pivot_row, k]]

        if abs(Ab[k, k]) < 1e-12:
            raise ValueError("矩阵奇异")

        for i in range(k + 1, n):
            factor = Ab[i, k] / Ab[k, k]
            Ab[i, k:] -= factor * Ab[k, k:]

    # 回代
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (Ab[i, -1] - np.dot(Ab[i, i+1:n], x[i+1:n])) / Ab[i, i]

    return x


def lu_decomposition(A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """LU 分解 (Doolittle), A = LU。"""
    n = len(A)
    L = np.eye(n)
    U = np.zeros((n, n))
    A_f = A.astype(np.float64)

    for k in range(n):
        U[k, k:] = A_f[k, k:] - L[k, :k] @ U[:k, k:]
        for i in range(k + 1, n):
            if abs(U[k, k]) < 1e-12:
                raise ValueError("需要主元置换")
            L[i, k] = (A_f[i, k] - L[i, :k] @ U[:k, k]) / U[k, k]

    return L, U


def lu_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """LU 分解求解 Ax = b。"""
    L, U = lu_decomposition(A)
    n = len(A)

    # 前代: Ly = b
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])

    # 回代: Ux = y
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]

    return x


def cholesky_decomposition(A: np.ndarray) -> np.ndarray:
    """Cholesky 分解 —— A = LL^T, A 必须对称正定。"""
    n = len(A)
    L = np.zeros((n, n))
    A_f = A.astype(np.float64)

    for i in range(n):
        for j in range(i + 1):
            if i == j:
                L[i, i] = np.sqrt(A_f[i, i] - np.sum(L[i, :i] ** 2))
            else:
                L[i, j] = (A_f[i, j] - np.sum(L[i, :j] * L[j, :j])) / L[j, j]

    return L


def conjugate_gradient(A: np.ndarray, b: np.ndarray,
                       max_iter: int = 1000,
                       tol: float = 1e-8) -> np.ndarray:
    """共轭梯度法 —— 适用于大型稀疏对称正定系统。"""
    x = np.zeros_like(b, dtype=np.float64)
    r = b - A @ x
    p = r.copy()
    r_norm_sq = r @ r

    for _ in range(max_iter):
        Ap = A @ p
        alpha = r_norm_sq / (p @ Ap)
        x += alpha * p
        r -= alpha * Ap

        r_norm_sq_new = r @ r
        if np.sqrt(r_norm_sq_new) < tol:
            break
        beta = r_norm_sq_new / r_norm_sq
        p = r + beta * p
        r_norm_sq = r_norm_sq_new

    return x


# ============================================================
# §4  非线性方程求根
# ============================================================

def bisection(f: Callable[[float], float], a: float, b: float,
              tol: float = 1e-8, max_iter: int = 100) -> float | None:
    """二分法 —— 必收敛，但需区间内有根。"""
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None

    for _ in range(max_iter):
        c = (a + b) / 2
        fc = f(c)
        if abs(fc) < tol or (b - a) / 2 < tol:
            return c
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return (a + b) / 2


def newton_raphson(f: Callable[[float], float],
                   df: Callable[[float], float],
                   x0: float, tol: float = 1e-8,
                   max_iter: int = 100) -> float | None:
    """牛顿-拉弗森法 —— 二次收敛，需要导数。"""
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = df(x)
        if abs(dfx) < 1e-15:
            return None
        x = x - fx / dfx
    return x


def secant_method(f: Callable[[float], float], x0: float, x1: float,
                  tol: float = 1e-8, max_iter: int = 100) -> float | None:
    """割线法 —— 不需要导数，超线性收敛。"""
    f0, f1 = f(x0), f(x1)
    for _ in range(max_iter):
        if abs(f1) < tol:
            return x1
        if abs(f1 - f0) < 1e-15:
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        x0, f0 = x1, f1
        x1, f1 = x2, f(x2)
    return x1


# ============================================================
# §5  插值
# ============================================================

def lagrange_interpolation(x_points: np.ndarray, y_points: np.ndarray,
                           x: float) -> float:
    """拉格朗日插值。"""
    n = len(x_points)
    result = 0.0
    for i in range(n):
        li = 1.0
        for j in range(n):
            if i != j:
                li *= (x - x_points[j]) / (x_points[i] - x_points[j])
        result += y_points[i] * li
    return result


def cubic_spline_coefficients(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """三次样条插值系数 (自然边界条件)。"""
    n = len(x) - 1
    h = np.diff(x)
    a = y.copy()

    # 三对角系统求解 c (二阶导数)
    A = np.zeros((n + 1, n + 1))
    b_vec = np.zeros(n + 1)

    A[0, 0] = 1
    A[n, n] = 1

    for i in range(1, n):
        A[i, i - 1] = h[i - 1]
        A[i, i] = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b_vec[i] = 3 * ((a[i + 1] - a[i]) / h[i] -
                       (a[i] - a[i - 1]) / h[i - 1])

    c = gaussian_elimination(A, b_vec)

    b = np.zeros(n)
    d = np.zeros(n)

    for i in range(n):
        b[i] = (a[i + 1] - a[i]) / h[i] - h[i] * (c[i + 1] + 2 * c[i]) / 3
        d[i] = (c[i + 1] - c[i]) / (3 * h[i])

    return a, b, c, d


def cubic_spline_evaluate(x_val: float, x: np.ndarray,
                          a: np.ndarray, b: np.ndarray,
                          c: np.ndarray, d: np.ndarray) -> float:
    """在样条上求值。"""
    n = len(x) - 1
    for i in range(n):
        if x[i] <= x_val <= x[i + 1]:
            dx = x_val - x[i]
            return a[i] + b[i] * dx + c[i] * dx**2 + d[i] * dx**3
    return 0.0


# ============================================================
# §6  最优化算法
# ============================================================

def gradient_descent(f: Callable[[np.ndarray], float],
                     grad: Callable[[np.ndarray], np.ndarray],
                     x0: np.ndarray, lr: float = 0.01,
                     max_iter: int = 1000,
                     tol: float = 1e-6) -> tuple[np.ndarray, list[float]]:
    """梯度下降 —— 一阶方法。"""
    x = x0.copy().astype(np.float64)
    history = [f(x)]

    for _ in range(max_iter):
        g = grad(x)
        if np.linalg.norm(g) < tol:
            break
        x -= lr * g
        history.append(f(x))

    return x, history


def newton_optimize(f: Callable[[np.ndarray], float],
                    grad: Callable[[np.ndarray], np.ndarray],
                    hess: Callable[[np.ndarray], np.ndarray],
                    x0: np.ndarray, max_iter: int = 50,
                    tol: float = 1e-6) -> tuple[np.ndarray, list[float]]:
    """牛顿法优化 —— 二阶方法，收敛快但每次迭代代价大。"""
    x = x0.copy().astype(np.float64)
    history = [f(x)]

    for _ in range(max_iter):
        g = grad(x)
        if np.linalg.norm(g) < tol:
            break
        H = hess(x)
        try:
            p = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            p = -g
        x += p
        history.append(f(x))

    return x, history


def bfgs_update(H_inv: np.ndarray, s: np.ndarray,
                y: np.ndarray) -> np.ndarray:
    """BFGS 公式 —— 更新逆 Hessian 近似。"""
    rho = 1.0 / (y @ s)
    I = np.eye(len(s))
    return (I - rho * np.outer(s, y)) @ H_inv @ (I - rho * np.outer(y, s)) + rho * np.outer(s, s)


def lbfgs_two_loop(grad_k: np.ndarray,
                   s_history: list[np.ndarray],
                   y_history: list[np.ndarray],
                   m: int = 10) -> np.ndarray:
    """L-BFGS 双循环递归算法。"""
    q = grad_k.copy()
    alphas: list[float] = []
    rhos: list[float] = []

    # 第一循环
    for s, y in zip(reversed(s_history), reversed(y_history)):
        rho = 1.0 / max(y @ s, 1e-12)
        alpha = rho * (s @ q)
        alphas.append(alpha)
        rhos.append(rho)
        q -= alpha * y

    # 初始化 H0
    if s_history:
        s_last, y_last = s_history[-1], y_history[-1]
        gamma = (s_last @ y_last) / max(y_last @ y_last, 1e-12)
    else:
        gamma = 1.0
    r = gamma * q

    # 第二循环
    for s, y, alpha, rho in zip(reversed(s_history), reversed(y_history),
                                 reversed(alphas), reversed(rhos)):
        beta = rho * (y @ r)
        r += s * (alpha - beta)

    return -r


# ============================================================
# §7  模拟退火与遗传算法
# ============================================================

def simulated_annealing(objective: Callable[[np.ndarray], float],
                        bounds: list[tuple[float, float]],
                        initial_temp: float = 1000.0,
                        cooling_rate: float = 0.995,
                        max_iter: int = 5000,
                        min_temp: float = 0.01) -> tuple[np.ndarray, float]:
    """模拟退火 —— 全局优化算法。"""
    dim = len(bounds)
    x = np.array([random.uniform(lo, hi) for lo, hi in bounds])
    fx = objective(x)
    best_x, best_fx = x.copy(), fx
    T = initial_temp

    for _ in range(max_iter):
        # 生成邻居
        neighbor = x.copy()
        for d in range(dim):
            lo, hi = bounds[d]
            delta = (hi - lo) * 0.1 * random.uniform(-1, 1)
            neighbor[d] = np.clip(neighbor[d] + delta, lo, hi)

        f_neighbor = objective(neighbor)
        delta_f = f_neighbor - fx

        if delta_f < 0 or random.random() < math.exp(-delta_f / T):
            x, fx = neighbor, f_neighbor
            if fx < best_fx:
                best_x, best_fx = x.copy(), fx

        T *= cooling_rate
        if T < min_temp:
            break

    return best_x, best_fx


def genetic_algorithm(objective: Callable[[np.ndarray], float],
                      bounds: list[tuple[float, float]],
                      population_size: int = 100,
                      generations: int = 200,
                      mutation_rate: float = 0.1,
                      crossover_rate: float = 0.8,
                      elite_size: int = 5) -> tuple[np.ndarray, float]:
    """遗传算法 —— 全局优化。"""
    dim = len(bounds)
    # 初始化种群
    population = np.array([
        [random.uniform(lo, hi) for lo, hi in bounds]
        for _ in range(population_size)
    ])

    for _ in range(generations):
        fitness = np.array([objective(ind) for ind in population])

        # 精英保留
        elite_idx = np.argsort(fitness)[:elite_size]
        new_population = [population[i].copy() for i in elite_idx]

        # 选择、交叉、变异
        while len(new_population) < population_size:
            # 锦标赛选择
            tournament = rng.choice(population_size, 3)
            parent1_idx = tournament[np.argmin(fitness[tournament])]
            tournament = rng.choice(population_size, 3)
            parent2_idx = tournament[np.argmin(fitness[tournament])]

            parent1, parent2 = population[parent1_idx], population[parent2_idx]

            if random.random() < crossover_rate:
                alpha = rng.random(dim)
                child = alpha * parent1 + (1 - alpha) * parent2
            else:
                child = parent1.copy()

            # 变异
            if random.random() < mutation_rate:
                d = random.randint(0, dim - 1)
                lo, hi = bounds[d]
                child[d] += random.uniform(-0.1, 0.1) * (hi - lo)
                child[d] = np.clip(child[d], lo, hi)

            new_population.append(child)

        population = np.array(new_population[:population_size])

    fitness = np.array([objective(ind) for ind in population])
    best_idx = np.argmin(fitness)
    return population[best_idx], fitness[best_idx]


# ============================================================
# §8  ODE 求解
# ============================================================

def euler_method(f: Callable[[float, float], float],
                 y0: float, t_span: tuple[float, float],
                 n: int = 100) -> tuple[np.ndarray, np.ndarray]:
    """欧拉法 —— 一阶 ODE 求解器, y' = f(t, y)。"""
    t0, tf = t_span
    h = (tf - t0) / n
    t = np.linspace(t0, tf, n + 1)
    y = np.zeros(n + 1)
    y[0] = y0

    for i in range(n):
        y[i + 1] = y[i] + h * f(t[i], y[i])

    return t, y


def runge_kutta_4(f: Callable[[float, float], float],
                  y0: float, t_span: tuple[float, float],
                  n: int = 100) -> tuple[np.ndarray, np.ndarray]:
    """RK4 —— 经典四阶龙格库塔法, O(h^4) 误差。"""
    t0, tf = t_span
    h = (tf - t0) / n
    t = np.linspace(t0, tf, n + 1)
    y = np.zeros(n + 1)
    y[0] = y0

    for i in range(n):
        ti, yi = t[i], y[i]
        k1 = f(ti, yi)
        k2 = f(ti + h/2, yi + h/2 * k1)
        k3 = f(ti + h/2, yi + h/2 * k2)
        k4 = f(ti + h, yi + h * k3)
        y[i + 1] = yi + h/6 * (k1 + 2*k2 + 2*k3 + k4)

    return t, y


def rk4_system(f: Callable[[float, np.ndarray], np.ndarray],
               y0: np.ndarray, t_span: tuple[float, float],
               n: int = 100) -> tuple[np.ndarray, np.ndarray]:
    """RK4 用于 ODE 系统。"""
    t0, tf = t_span
    h = (tf - t0) / n
    t = np.linspace(t0, tf, n + 1)
    dim = len(y0)
    y = np.zeros((n + 1, dim))
    y[0] = y0

    for i in range(n):
        ti, yi = t[i], y[i]
        k1 = f(ti, yi)
        k2 = f(ti + h/2, yi + h/2 * k1)
        k3 = f(ti + h/2, yi + h/2 * k2)
        k4 = f(ti + h, yi + h * k3)
        y[i + 1] = yi + h/6 * (k1 + 2*k2 + 2*k3 + k4)

    return t, y


# ============================================================
# §9  傅里叶变换基础
# ============================================================

def dft(x: np.ndarray) -> np.ndarray:
    """离散傅里叶变换 —— O(n²), 教学用。"""
    n = len(x)
    X = np.zeros(n, dtype=complex)
    for k in range(n):
        for j in range(n):
            X[k] += x[j] * np.exp(-2j * np.pi * k * j / n)
    return X


def fft(x: np.ndarray) -> np.ndarray:
    """快速傅里叶变换 (Cooley-Tukey) —— O(n log n)。"""
    n = len(x)
    if n <= 1:
        return np.array(x, dtype=complex)

    if n % 2 != 0:
        return dft(x)

    X_even = fft(x[0::2])
    X_odd = fft(x[1::2])
    factor = np.exp(-2j * np.pi * np.arange(n) / n)

    X = np.zeros(n, dtype=complex)
    half = n // 2
    X[:half] = X_even + factor[:half] * X_odd
    X[half:] = X_even + factor[half:] * X_odd

    return X


def ifft(X: np.ndarray) -> np.ndarray:
    """逆 FFT。"""
    n = len(X)
    x_conj = fft(np.conj(X))
    return np.conj(x_conj) / n


# ============================================================
# §10  演示
# ============================================================

def demo_numerical() -> None:
    print("=" * 60)
    print("数值方法与优化算法演示")
    print("=" * 60)

    # 积分
    f_int = lambda x: np.sin(x) + 0.5 * np.cos(2 * x)
    exact = -np.cos(np.pi) - (-np.cos(0)) + 0.25 * np.sin(2 * np.pi) - 0.25 * np.sin(0)
    print(f"\n定积分 ∫₀^π sin(x)+0.5cos(2x) dx:")
    print(f"  真值:         {exact:.8f}")
    print(f"  梯形公式:     {trapezoidal_rule(f_int, 0, np.pi, 1000):.8f}")
    print(f"  Simpson 法则: {simpson_rule(f_int, 0, np.pi, 1000):.8f}")
    print(f"  Gauss(5点):   {gaussian_quadrature(f_int, 0, np.pi, 5):.8f}")

    # Monte Carlo 积分
    def g_mc(x: np.ndarray) -> float:
        return float(np.sin(x[0]) * np.exp(-x[1]**2))

    est, err = monte_carlo_integral(g_mc, [(0, np.pi), (-2, 2)], n=50000)
    print(f"  蒙特卡洛 2D:  {est:.6f} ± {err:.6f}")

    # 求导
    f_diff = lambda x: x**3 - 3*x**2 + 2*x + 1
    df_exact = lambda x: 3*x**2 - 6*x + 2
    x0 = 2.0
    print(f"\n数值微分 f(x)=x³-3x²+2x+1 at x=2:")
    print(f"  真值:           {df_exact(x0)}")
    print(f"  central diff:   {finite_difference(f_diff, x0, method='central'):.6f}")
    print(f"  forward diff:   {finite_difference(f_diff, x0, method='forward'):.6f}")

    # 线性方程组
    A = np.array([[4, 1, -1], [2, 7, 1], [1, -3, 12]], dtype=float)
    b = np.array([3, 19, 31], dtype=float)
    x_exact = np.linalg.solve(A, b)
    x_ge = gaussian_elimination(A, b)
    x_lu = lu_solve(A, b)
    x_cg = conjugate_gradient(A, b)
    print(f"\n线性方程组 Ax=b:")
    print(f"  精确解:         {x_exact}")
    print(f"  高斯消元:       {x_ge}")
    print(f"  LU 分解:        {x_lu}")
    print(f"  共轭梯度:       {x_cg}")

    # 非线性求根
    f_root = lambda x: x**3 - x - 2
    df_root = lambda x: 3*x**2 - 1
    root_bisec = bisection(f_root, 1, 2)
    root_newton = newton_raphson(f_root, df_root, 1.5)
    root_secant = secant_method(f_root, 1, 2)
    print(f"\n求根 f(x)=x³-x-2=0:")
    print(f"  二分法:      {root_bisec:.8f}")
    print(f"  牛顿法:      {root_newton:.8f}")
    print(f"  割线法:      {root_secant:.8f}")

    # 插值
    x_pts = np.array([0, 1, 2, 3, 4])
    y_pts = np.array([1, 3, 2, 4, 0])
    print(f"\n拉格朗日插值:")
    for xi in [0.5, 1.5, 2.5, 3.5]:
        yi = lagrange_interpolation(x_pts, y_pts, xi)
        print(f"  f({xi}) ≈ {yi:.4f}")

    # 三次样条
    a_cs, b_cs, c_cs, d_cs = cubic_spline_coefficients(x_pts, y_pts)
    print(f"三次样条: x=2.5 -> {cubic_spline_evaluate(2.5, x_pts, a_cs, b_cs, c_cs, d_cs):.4f}")

    # 最优化
    f_opt = lambda x: float(x[0]**2 + x[1]**2 - 2*x[0]*x[1] + x[0] + x[1])
    grad_opt = lambda x: np.array([2*x[0] - 2*x[1] + 1, 2*x[1] - 2*x[0] + 1])
    x_opt, hist = gradient_descent(f_opt, grad_opt, np.array([5.0, 5.0]), lr=0.1)
    print(f"\n最优化: min x²+y²-2xy+x+y")
    print(f"  梯度下降解: x={x_opt[0]:.4f}, y={x_opt[1]:.4f}, f={f_opt(x_opt):.4f}")
    print(f"  迭代: {len(hist)} 次")

    # 模拟退火 & 遗传算法
    def rastrigin(x: np.ndarray) -> float:
        return 10 * len(x) + sum(xi**2 - 10 * np.cos(2 * np.pi * xi)
                                  for xi in x)

    x_sa, f_sa = simulated_annealing(rastrigin, [(-5.12, 5.12)] * 2,
                                      max_iter=2000)
    print(f"\n全局优化 (Rastrigin 函数):")
    print(f"  模拟退火: x={x_sa}, f={f_sa:.4f}")

    x_ga, f_ga = genetic_algorithm(rastrigin, [(-5.12, 5.12)] * 2,
                                    population_size=50, generations=100)
    print(f"  遗传算法: x={x_ga}, f={f_ga:.4f}")

    # ODE
    f_ode = lambda t, y: -2 * y + np.sin(t)
    t_rk4, y_rk4 = runge_kutta_4(f_ode, 1.0, (0, 5), 100)
    print(f"\nODE: y'=-2y+sin(t), y(0)=1")
    print(f"  RK4 解: y(5) ≈ {y_rk4[-1]:.6f}")

    # FFT
    signal = np.array([1, 2, 1, 0, -1, -2, -1, 0], dtype=float)
    X_fft = fft(signal)
    x_recovered = ifft(X_fft)
    print(f"\nFFT of [1,2,1,0,-1,-2,-1,0]:")
    print(f"  FFT: {np.round(np.abs(X_fft), 2)}")
    print(f"  IFFT 恢复误差: {np.max(np.abs(signal - x_recovered)):.2e}")


if __name__ == "__main__":
    demo_numerical()
    print("\n✅ 数值方法与优化篇执行完毕!")
