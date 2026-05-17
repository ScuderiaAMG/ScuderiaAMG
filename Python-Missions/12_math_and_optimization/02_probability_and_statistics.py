#!/usr/bin/env python3
"""
概率论与数理统计 —— Python 实现
涵盖：概率分布（离散/连续）、假设检验（t检验/卡方检验/ANOVA）、
      贝叶斯推断、MCMC (Metropolis-Hastings)、Bootstrap、
      回归分析（线性/多项式/岭回归/套索）、KL散度/JS散度、
      信息论（熵/互信息）、蒙特卡洛方法
"""

import numpy as np
from typing import Any, Callable
from collections import Counter
import math
import random

rng = np.random.default_rng(42)


# ============================================================
# §1  概率分布
# ============================================================

class Distribution:
    """概率分布基类。"""

    def pdf(self, x: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def log_pdf(self, x: np.ndarray) -> np.ndarray:
        return np.log(self.pdf(x))

    def sample(self, n: int = 1) -> np.ndarray:
        raise NotImplementedError


class Gaussian(Distribution):
    def __init__(self, mu: float = 0.0, sigma: float = 1.0) -> None:
        self.mu = mu
        self.sigma = sigma

    def pdf(self, x: np.ndarray) -> np.ndarray:
        return (1 / (self.sigma * np.sqrt(2 * np.pi)) *
                np.exp(-0.5 * ((x - self.mu) / self.sigma) ** 2))

    def sample(self, n: int = 1) -> np.ndarray:
        return rng.normal(self.mu, self.sigma, n)


class Bernoulli(Distribution):
    def __init__(self, p: float = 0.5) -> None:
        self.p = p

    def pmf(self, x: np.ndarray) -> np.ndarray:
        return np.where(x == 1, self.p, 1 - self.p)

    def sample(self, n: int = 1) -> np.ndarray:
        return rng.binomial(1, self.p, n)


class Poisson(Distribution):
    def __init__(self, lam: float = 1.0) -> None:
        self.lam = lam

    def pmf(self, x: np.ndarray) -> np.ndarray:
        return np.exp(-self.lam) * self.lam ** x / np.array(
            [math.factorial(int(xi)) for xi in x]
        )

    def sample(self, n: int = 1) -> np.ndarray:
        return rng.poisson(self.lam, n)


class Beta(Distribution):
    def __init__(self, a: float = 1.0, b: float = 1.0) -> None:
        self.a = a
        self.b = b
        self._B = math.gamma(a) * math.gamma(b) / math.gamma(a + b)

    def pdf(self, x: np.ndarray) -> np.ndarray:
        return (x ** (self.a - 1) * (1 - x) ** (self.b - 1) / self._B)

    def sample(self, n: int = 1) -> np.ndarray:
        return rng.beta(self.a, self.b, n)


class Gamma(Distribution):
    def __init__(self, shape: float = 1.0, scale: float = 1.0) -> None:
        self.shape = shape
        self.scale = scale

    def pdf(self, x: np.ndarray) -> np.ndarray:
        return (x ** (self.shape - 1) * np.exp(-x / self.scale) /
                (self.scale ** self.shape * math.gamma(self.shape)))

    def sample(self, n: int = 1) -> np.ndarray:
        return rng.gamma(self.shape, self.scale, n)


class Categorical(Distribution):
    def __init__(self, probs: list[float]) -> None:
        self.probs = np.array(probs) / np.sum(probs)

    def pmf(self, x: int) -> float:
        return float(self.probs[x])

    def sample(self, n: int = 1) -> np.ndarray:
        return rng.choice(len(self.probs), size=n, p=self.probs)


class MultivariateGaussian(Distribution):
    def __init__(self, mu: np.ndarray, sigma: np.ndarray) -> None:
        self.mu = mu
        self.sigma = sigma
        self.d = len(mu)
        self._L = np.linalg.cholesky(sigma)

    def pdf(self, x: np.ndarray) -> np.ndarray:
        diff = x - self.mu
        z = np.linalg.solve(self._L, diff.T).T
        quad = np.sum(z ** 2, axis=-1)
        log_det = 2 * np.sum(np.log(np.diag(self._L)))
        return np.exp(-0.5 * (self.d * np.log(2 * np.pi) + log_det + quad))

    def sample(self, n: int = 1) -> np.ndarray:
        z = rng.normal(0, 1, (n, self.d))
        return self.mu + z @ self._L.T


# ============================================================
# §2  假设检验
# ============================================================

def t_test_one_sample(data: np.ndarray, mu0: float = 0.0) -> dict[str, float]:
    """单样本 t 检验 —— H0: μ = μ0。"""
    n = len(data)
    xbar = np.mean(data)
    s = np.std(data, ddof=1)
    t_stat = (xbar - mu0) / (s / np.sqrt(n))
    df = n - 1

    # 使用近似正态
    p_value = 2 * (1 - _t_cdf_approx(abs(t_stat), df))
    return {"t_statistic": float(t_stat), "p_value": p_value, "df": df,
            "mean": float(xbar), "std": float(s)}


def t_test_two_sample(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """双样本 t 检验 (等方差假设) —— H0: μx = μy。"""
    nx, ny = len(x), len(y)
    xbar, ybar = np.mean(x), np.mean(y)
    sx2, sy2 = np.var(x, ddof=1), np.var(y, ddof=1)

    sp2 = ((nx - 1) * sx2 + (ny - 1) * sy2) / (nx + ny - 2)
    t_stat = (xbar - ybar) / np.sqrt(sp2 * (1/nx + 1/ny))
    df = nx + ny - 2

    p_value = 2 * (1 - _t_cdf_approx(abs(t_stat), df))
    return {"t_statistic": float(t_stat), "p_value": p_value, "df": df}


def chi_square_test(observed: np.ndarray) -> dict[str, float]:
    """卡方独立性检验。"""
    row_sum = observed.sum(axis=1, keepdims=True)
    col_sum = observed.sum(axis=0, keepdims=True)
    total = observed.sum()
    expected = row_sum @ col_sum / total

    chi2 = np.sum((observed - expected) ** 2 / expected)
    df = (observed.shape[0] - 1) * (observed.shape[1] - 1)

    # Wilson-Hilferty 近似
    z = ((chi2 / df) ** (1/3) - (1 - 2/(9*df))) / np.sqrt(2/(9*df))
    p_value = 2 * (1 - _norm_cdf_approx(abs(z)))

    return {"chi2": float(chi2), "df": df, "p_value": p_value}


def one_way_anova(*groups: np.ndarray) -> dict[str, float]:
    """单因素方差分析 (ANOVA)。"""
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)
    k = len(groups)
    N = len(all_data)

    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_within = sum(np.sum((g - np.mean(g)) ** 2) for g in groups)

    df_between = k - 1
    df_within = N - k
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    F = ms_between / ms_within

    # 近似 F -> p (使用 Snedecor)
    p_value = 1 - _f_cdf_approx(F, df_between, df_within)

    return {"F_statistic": float(F), "p_value": p_value,
            "df_between": df_between, "df_within": df_within}


def _t_cdf_approx(t: float, df: int) -> float:
    """t 分布的 CDF 近似。"""
    x = df / (df + t ** 2)
    return 0.5 * (1 + _incomplete_beta_approx(0.5, df / 2, x))


def _norm_cdf_approx(x: float) -> float:
    """标准正态 CDF 近似。"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _f_cdf_approx(F: float, df1: int, df2: int) -> float:
    """F 分布的 CDF 近似。"""
    x = df2 / (df2 + df1 * F)
    return _incomplete_beta_approx(df2 / 2, df1 / 2, x)


def _incomplete_beta_approx(a: float, b: float, x: float) -> float:
    """不完全 Beta 函数 (使用连分数展开)。"""
    if x < 0 or x > 1:
        return 0.0
    if x == 0:
        return 0.0
    if x == 1:
        return 1.0

    # 使用 Numpy 的内置函数作为近似
    from scipy.special import betainc
    try:
        return float(betainc(a, b, x))
    except ImportError:
        # 非常粗略的近似
        return min(1.0, x * (a / (a + b)))


# ============================================================
# §3  贝叶斯推断
# ============================================================

class BetaBinomialModel:
    """Beta 先验 + 二项似然 → Beta 后验 (共轭)。"""

    def __init__(self, prior_a: float = 1.0, prior_b: float = 1.0) -> None:
        self.prior_a = prior_a
        self.prior_b = prior_b
        self.posterior_a = prior_a
        self.posterior_b = prior_b

    def update(self, successes: int, trials: int) -> None:
        self.posterior_a += successes
        self.posterior_b += (trials - successes)

    def posterior_mean(self) -> float:
        return self.posterior_a / (self.posterior_a + self.posterior_b)

    def posterior_interval(self, alpha: float = 0.05) -> tuple[float, float]:
        """等尾可信区间。"""
        lo = Beta(self.posterior_a, self.posterior_b).sample(10000)
        return (float(np.percentile(lo, 100 * alpha / 2)),
                float(np.percentile(lo, 100 * (1 - alpha / 2))))


class NormalNormalModel:
    """正态先验 + 正态似然 (已知方差) → 正态后验。"""

    def __init__(self, prior_mu: float = 0.0, prior_tau2: float = 1.0,
                 known_sigma2: float = 1.0) -> None:
        self.prior_mu = prior_mu
        self.prior_tau2 = prior_tau2
        self.sigma2 = known_sigma2
        self.posterior_mu = prior_mu
        self.posterior_tau2 = prior_tau2

    def update(self, data: np.ndarray) -> None:
        n = len(data)
        xbar = np.mean(data)
        prior_precision = 1 / self.prior_tau2
        data_precision = n / self.sigma2
        self.posterior_tau2 = 1 / (prior_precision + data_precision)
        self.posterior_mu = (self.posterior_tau2 *
                             (prior_precision * self.prior_mu +
                              data_precision * xbar))

    def posterior_mean(self) -> float:
        return self.posterior_mu


# ============================================================
# §4  MCMC (Metropolis-Hastings)
# ============================================================

def metropolis_hastings(target_log_pdf: Callable[[float], float],
                        proposal_std: float = 1.0,
                        n_samples: int = 10000,
                        burn_in: int = 2000,
                        initial: float = 0.0) -> np.ndarray:
    """Metropolis-Hastings 采样。"""
    samples = np.zeros(n_samples)
    current = initial
    current_log_pdf = target_log_pdf(current)
    accepted = 0

    for i in range(n_samples + burn_in):
        proposal = rng.normal(current, proposal_std)
        proposal_log_pdf = target_log_pdf(proposal)

        log_ratio = proposal_log_pdf - current_log_pdf
        if math.log(rng.random()) < log_ratio:
            current = proposal
            current_log_pdf = proposal_log_pdf
            if i >= burn_in:
                accepted += 1

        if i >= burn_in:
            samples[i - burn_in] = current

    acceptance_rate = accepted / n_samples
    return samples


def gibbs_sampler_bivariate(target_conditional_x: Callable[[float], float],
                            target_conditional_y: Callable[[float], float],
                            n_iter: int = 5000,
                            burn_in: int = 1000) -> np.ndarray:
    """二元 Gibss 采样 —— 从条件分布中轮流采样。"""
    samples = np.zeros((n_iter, 2))
    x = 0.0
    y = 0.0

    for i in range(n_iter + burn_in):
        x = target_conditional_x(y)
        y = target_conditional_y(x)
        if i >= burn_in:
            samples[i - burn_in] = [x, y]

    return samples


# ============================================================
# §5  Bootstrap
# ============================================================

def bootstrap_ci(data: np.ndarray, statistic: Callable[[np.ndarray], float],
                 n_bootstrap: int = 10000, alpha: float = 0.05,
                 method: str = "percentile") -> dict[str, Any]:
    """Bootstrap 置信区间。"""
    n = len(data)
    boot_stats = np.zeros(n_bootstrap)

    for i in range(n_bootstrap):
        sample = rng.choice(data, n, replace=True)
        boot_stats[i] = statistic(sample)

    if method == "percentile":
        lo = np.percentile(boot_stats, 100 * alpha / 2)
        hi = np.percentile(boot_stats, 100 * (1 - alpha / 2))
    elif method == "bca":
        # BCa (Bias-Corrected and Accelerated)
        z0 = _norm_quantile(np.mean(boot_stats < statistic(data)))
        # Jackknife acceleration
        jack = np.zeros(n)
        for i in range(n):
            jack[i] = statistic(np.delete(data, i))
        a = np.sum((jack.mean() - jack) ** 3) / (6 * np.sum((jack.mean() - jack) ** 2) ** 1.5)
        z_alpha = _norm_quantile(alpha / 2)
        z_1_alpha = _norm_quantile(1 - alpha / 2)
        adj_lo = z0 + (z0 + z_alpha) / (1 - a * (z0 + z_alpha))
        adj_hi = z0 + (z0 + z_1_alpha) / (1 - a * (z0 + z_1_alpha))
        lo = np.percentile(boot_stats, 100 * _norm_cdf_approx(adj_lo))
        hi = np.percentile(boot_stats, 100 * _norm_cdf_approx(adj_hi))
    else:
        raise ValueError(f"Unknown method: {method}")

    return {"ci": (float(lo), float(hi)),
            "bootstrap_mean": float(np.mean(boot_stats)),
            "bootstrap_std": float(np.std(boot_stats)),
            "original_stat": float(statistic(data))}


def _norm_quantile(p: float) -> float:
    """正态分位数近似。"""
    return math.sqrt(2) * math.erfinv(2 * p - 1)


# ============================================================
# §6  回归分析
# ============================================================

class LinearRegression:
    """普通最小二乘 (OLS) 线性回归。"""

    def __init__(self, fit_intercept: bool = True) -> None:
        self.fit_intercept = fit_intercept
        self.coef_: np.ndarray | None = None
        self.intercept_: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegression":
        if self.fit_intercept:
            X = np.column_stack([np.ones(len(X)), X])
        try:
            self.coef_ = np.linalg.solve(X.T @ X, X.T @ y)
        except np.linalg.LinAlgError:
            self.coef_ = np.linalg.lstsq(X, y, rcond=None)[0]

        if self.fit_intercept:
            self.intercept_ = float(self.coef_[0])
            self.coef_ = self.coef_[1:]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.coef_ + self.intercept_  # type: ignore[operator]


class RidgeRegression:
    """岭回归 —— 带 L2 正则化。"""

    def __init__(self, alpha: float = 1.0, fit_intercept: bool = True) -> None:
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.coef_: np.ndarray | None = None
        self.intercept_: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeRegression":
        if self.fit_intercept:
            self.intercept_ = float(np.mean(y))
            y_centered = y - self.intercept_
        else:
            y_centered = y

        n, p = X.shape
        I = np.eye(p)
        self.coef_ = np.linalg.solve(X.T @ X + self.alpha * I, X.T @ y_centered)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.coef_ + self.intercept_  # type: ignore[operator]


class LassoRegression:
    """Lasso —— 坐标下降法求解 L1 正则化。"""

    def __init__(self, alpha: float = 1.0, max_iter: int = 1000,
                 tol: float = 1e-4) -> None:
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.coef_: np.ndarray | None = None
        self.intercept_: float = 0.0

    def _soft_threshold(self, x: float, lam: float) -> float:
        if x > lam:
            return x - lam
        if x < -lam:
            return x + lam
        return 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LassoRegression":
        n, p = X.shape
        self.intercept_ = float(np.mean(y))
        r = y - self.intercept_
        self.coef_ = np.zeros(p)

        X_norm_sq = np.sum(X ** 2, axis=0) + 1e-10

        for _ in range(self.max_iter):
            coef_old = self.coef_.copy()
            for j in range(p):
                r_j = r + X[:, j] * self.coef_[j]
                rho = X[:, j].T @ r_j
                self.coef_[j] = self._soft_threshold(rho, self.alpha) / X_norm_sq[j]
                r = r_j - X[:, j] * self.coef_[j]

            if np.max(np.abs(self.coef_ - coef_old)) < self.tol:
                break
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.coef_ + self.intercept_  # type: ignore[operator]


# ============================================================
# §7  信息论
# ============================================================

def entropy(p: np.ndarray) -> float:
    """香农熵 H(p) = -Σ p(x) log p(x)。"""
    p_clean = p[p > 0]
    if len(p_clean) == 0:
        return 0.0
    return float(-np.sum(p_clean * np.log2(p_clean)))


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL 散度 D_KL(P || Q) = Σ p(x) log(p(x)/q(x))。"""
    mask = (p > 0) & (q > 0)
    return float(np.sum(p[mask] * np.log2(p[mask] / q[mask])))


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """JS 散度 —— KL 的对称版本。"""
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)


def mutual_information(joint: np.ndarray) -> float:
    """互信息 I(X;Y) = Σ p(x,y) log(p(x,y)/(p(x)·p(y)))。"""
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)
    mi = 0.0
    for i in range(joint.shape[0]):
        for j in range(joint.shape[1]):
            if joint[i, j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (px[i] * py[j]))
    return float(mi)


# ============================================================
# §8  蒙特卡洛方法
# ============================================================

def monte_carlo_pi(n: int = 100000) -> tuple[float, float]:
    """蒙特卡洛估算 π。"""
    points = rng.uniform(-1, 1, (n, 2))
    in_circle = np.sum(points[:, 0]**2 + points[:, 1]**2 <= 1)
    pi_est = 4 * in_circle / n
    err = 4 * np.sqrt(in_circle / n * (1 - in_circle / n) / n)
    return pi_est, err


def importance_sampling(target_func: Callable[[float], float],
                        proposal: Distribution,
                        n: int = 10000) -> tuple[float, float]:
    """重要性采样 —— 估计 E[f(X)]。"""
    samples = proposal.sample(n)

    # 假设 target 是 N(0,1), proposal 为给定分布
    target_dist = Gaussian(0, 1)
    target_pdf = target_dist.pdf(samples)
    proposal_pdf = proposal.pdf(samples)

    weights = target_pdf / (proposal_pdf + 1e-12)
    weights /= weights.sum()

    estimate = np.sum(weights * target_func(samples))
    variance = np.sum(weights * (target_func(samples) - estimate) ** 2)
    return estimate, np.sqrt(variance / n)


def rejection_sampling(target_pdf: Callable[[float], float],
                       proposal: Distribution,
                       envelope_factor: float,
                       n_samples: int = 1000) -> np.ndarray:
    """拒绝采样。"""
    samples: list[float] = []
    while len(samples) < n_samples:
        x = proposal.sample(1)[0]
        u = rng.uniform(0, envelope_factor * proposal.pdf(np.array([x]))[0])
        if u < target_pdf(x):
            samples.append(x)
    return np.array(samples)


# ============================================================
# §9  演示
# ============================================================

def demo_statistics() -> None:
    print("=" * 60)
    print("概率统计与信息论演示")
    print("=" * 60)

    # 概率分布
    normal = Gaussian(0, 1)
    print(f"正态 N(0,1) PDF at x=0: {normal.pdf(np.array([0]))[0]:.4f}")
    print(f"正态 sample(5): {normal.sample(5)}")

    beta_dist = Beta(2, 5)
    print(f"Beta(2,5) sample(5): {beta_dist.sample(5)}")

    cat = Categorical([0.1, 0.3, 0.6])
    print(f"Cat(0.1,0.3,0.6) sample(5): {cat.sample(5)}")

    mvn = MultivariateGaussian(np.array([0.0, 0.0]),
                               np.array([[1.0, 0.5], [0.5, 1.0]]))
    print(f"MVN sample(3):\n{mvn.sample(3)}")

    # t检验
    print("\n--- t 检验 ---")
    data_a = rng.normal(5.2, 2.0, 30)
    data_b = rng.normal(6.8, 2.0, 30)
    t1 = t_test_one_sample(data_a, mu0=5.0)
    print(f"单样本: t={t1['t_statistic']:.4f}, p={t1['p_value']:.4f}")
    t2 = t_test_two_sample(data_a, data_b)
    print(f"双样本: t={t2['t_statistic']:.4f}, p={t2['p_value']:.4f}")

    # 卡方检验
    obs = np.array([[20, 15, 10], [10, 25, 20]])
    chi2 = chi_square_test(obs)
    print(f"卡方检验: chi2={chi2['chi2']:.4f}, p={chi2['p_value']:.4f}")

    # ANOVA
    g1 = rng.normal(5, 2, 20)
    g2 = rng.normal(7, 2, 20)
    g3 = rng.normal(6, 2, 20)
    anova = one_way_anova(g1, g2, g3)
    print(f"ANOVA: F={anova['F_statistic']:.4f}, p={anova['p_value']:.4f}")

    # 贝叶斯推断
    print("\n--- 贝叶斯推断 ---")
    bb = BetaBinomialModel(prior_a=1, prior_b=1)
    bb.update(successes=7, trials=10)
    print(f"Beta-Binomial: posterior mean={bb.posterior_mean():.3f}")

    # MCMC
    print("\n--- MCMC ---")
    def target_log_pdf(x: float) -> float:
        # 混合高斯
        return np.log(0.5 * np.exp(-0.5 * (x - 2)**2) / np.sqrt(2 * np.pi) +
                      0.5 * np.exp(-0.5 * (x + 2)**2) / np.sqrt(2 * np.pi))

    samples = metropolis_hastings(target_log_pdf, proposal_std=1.5,
                                  n_samples=5000, burn_in=1000)
    print(f"MH 采样: mean={samples.mean():.3f}, std={samples.std():.3f}")

    # Bootstrap
    print("\n--- Bootstrap ---")
    data_bs = rng.exponential(2.0, 50)
    boot_result = bootstrap_ci(data_bs, np.median, n_bootstrap=5000)
    print(f"Bootstrap 中位数 CI: ({boot_result['ci'][0]:.3f}, {boot_result['ci'][1]:.3f})")

    # 回归
    print("\n--- 回归分析 ---")
    X_reg = rng.normal(0, 1, (100, 3))
    true_beta = np.array([2.0, -1.0, 0.5])
    y_reg = X_reg @ true_beta + rng.normal(0, 0.5, 100)

    ols = LinearRegression()
    ols.fit(X_reg, y_reg)
    print(f"OLS 系数: {ols.coef_}")

    ridge = RidgeRegression(alpha=0.1)
    ridge.fit(X_reg, y_reg)
    print(f"Ridge 系数: {ridge.coef_}")

    lasso = LassoRegression(alpha=0.05)
    lasso.fit(X_reg, y_reg)
    print(f"Lasso 系数: {lasso.coef_}")

    # 信息论
    print("\n--- 信息论 ---")
    p = np.array([0.25, 0.25, 0.25, 0.25])
    q = np.array([0.7, 0.1, 0.1, 0.1])
    print(f"熵 H(p) = {entropy(p):.4f} bits")
    print(f"KL(p||q) = {kl_divergence(p, q):.4f} bits")
    print(f"JS(p,q)  = {js_divergence(p, q):.4f} bits")

    # 蒙特卡洛
    print("\n--- 蒙特卡洛 ---")
    pi_est, pi_err = monte_carlo_pi(50000)
    print(f"MC π ≈ {pi_est:.6f} ± {pi_err:.6f}")


if __name__ == "__main__":
    demo_statistics()
    print("\n✅ 概率统计篇执行完毕!")
