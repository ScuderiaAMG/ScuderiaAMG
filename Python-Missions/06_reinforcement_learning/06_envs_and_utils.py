#!/usr/bin/env python3
"""
强化学习环境集合与工具函数
涵盖：MountainCar / Pendulum / LunarLander 风格环境的 NumPy 实现、
      Atari wrapper (简化)、经验回放优化、归一化 wrapper、
      并行环境 (subprocess)、超参数搜索 (网格/随机/贝叶斯优化)
"""

import numpy as np
from typing import Any
from collections import deque, defaultdict
import random
import math
import itertools

rng = np.random.default_rng(42)


# ============================================================
# §1  MountainCar 环境
# ============================================================

class MountainCar:
    """经典 MountainCar 环境。

    状态: [position, velocity]
    动作: 0=左, 1=不动, 2=右
    目标: 到达右侧山顶 (position >= 0.5)
    """

    def __init__(self) -> None:
        self.min_pos = -1.2
        self.max_pos = 0.6
        self.max_speed = 0.07
        self.goal_pos = 0.5
        self.power = 0.001
        self.state: np.ndarray | None = None
        self.steps: int = 0
        self.max_steps = 200

    def reset(self) -> np.ndarray:
        self.state = np.array([rng.uniform(-0.6, -0.4), 0.0])
        self.steps = 0
        return self.state.copy()

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        pos, vel = self.state  # type: ignore[misc]
        vel += (action - 1) * self.power + np.cos(3 * pos) * (-0.0025)
        vel = np.clip(vel, -self.max_speed, self.max_speed)
        pos += vel
        pos = np.clip(pos, self.min_pos, self.max_pos)

        if pos <= self.min_pos:
            vel = 0.0

        self.state = np.array([pos, vel])
        self.steps += 1

        done = pos >= self.goal_pos
        truncated = self.steps >= self.max_steps
        reward = -1.0 if not done else 0.0

        return self.state.copy(), reward, done or truncated


# ============================================================
# §2  Pendulum 环境
# ============================================================

class Pendulum:
    """经典 Pendulum 环境 (连续动作)。

    状态: [cos(theta), sin(theta), theta_dot]
    动作: 力矩 [-2, 2]
    目标: 摆直立 (theta = 0)
    """

    def __init__(self) -> None:
        self.max_speed = 8.0
        self.max_torque = 2.0
        self.dt = 0.05
        self.g = 10.0
        self.m = 1.0
        self.l = 1.0
        self.state: np.ndarray | None = None
        self.max_steps = 200
        self.steps = 0

    def reset(self) -> np.ndarray:
        theta = rng.uniform(-np.pi, np.pi)
        theta_dot = rng.uniform(-1, 1)
        self.state = np.array([np.cos(theta), np.sin(theta), theta_dot])
        self.steps = 0
        return self.state.copy()

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool]:
        torque = np.clip(action, -self.max_torque, self.max_torque).item()
        cos_th, sin_th, th_dot = self.state  # type: ignore[misc]
        theta = np.arctan2(sin_th, cos_th)

        # 动力学
        th_ddot = (-3 * self.g / (2 * self.l) * np.sin(theta + np.pi)
                   + 3 / (self.m * self.l**2) * torque)
        th_dot_new = np.clip(th_dot + th_ddot * self.dt, -self.max_speed, self.max_speed)
        theta_new = theta + th_dot_new * self.dt

        self.state = np.array([np.cos(theta_new), np.sin(theta_new), th_dot_new])
        self.steps += 1

        # 奖励: 越直立越好
        upright_bonus = -abs(((theta_new + np.pi) % (2 * np.pi)) - np.pi)
        torque_penalty = -0.001 * torque**2
        reward = upright_bonus + torque_penalty

        done = self.steps >= self.max_steps
        return self.state.copy(), float(reward), done


# ============================================================
# §3  LunarLander 风格环境
# ============================================================

class LunarLander:
    """简化版 LunarLander 环境。

    状态 (8 维): [x, y, vx, vy, theta, omega, left_leg, right_leg]
    动作 (离散 4): 0=nothing, 1=left engine, 2=main engine, 3=right engine
    """

    def __init__(self) -> None:
        self.gravity = -10.0
        self.main_power = 15.0
        self.side_power = 5.0
        self.dt = 0.05
        self.max_steps = 300
        self.state: np.ndarray | None = None
        self.steps = 0

        # 地形
        self.ground_y = 0.0
        self.landing_x = 0.0
        self.landing_width = 0.2

    def reset(self) -> np.ndarray:
        self.state = np.array([
            rng.uniform(-0.5, 0.5),          # x
            1.5 + rng.uniform(0, 0.5),        # y
            rng.uniform(-0.5, 0.5),           # vx
            rng.uniform(-1.0, 0.0),           # vy
            rng.uniform(-0.3, 0.3),           # theta
            rng.uniform(-0.2, 0.2),           # omega
            0.0, 0.0,                          # legs contact
        ])
        self.steps = 0
        return self.state.copy()

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        x, y, vx, vy, theta, omega, leg_l, leg_r = self.state  # type: ignore[misc]

        # 施加力
        if action == 1:     # left engine
            vy += self.side_power * self.dt
            omega -= self.side_power * 0.3 * self.dt
        elif action == 2:   # main engine
            vy += self.main_power * np.cos(theta) * self.dt
            vx -= self.main_power * np.sin(theta) * self.dt
        elif action == 3:   # right engine
            vy += self.side_power * self.dt
            omega += self.side_power * 0.3 * self.dt

        # 物理更新
        vy += self.gravity * self.dt
        x += vx * self.dt
        y += vy * self.dt
        theta += omega * self.dt

        # 着陆器腿的接触检测
        leg_l = 1.0 if (y <= self.ground_y and abs(x + 0.15 - self.landing_x) < 0.1) else 0.0
        leg_r = 1.0 if (y <= self.ground_y and abs(x - 0.15 - self.landing_x) < 0.1) else 0.0
        landed = y <= self.ground_y

        self.state = np.array([x, y, vx, vy, theta, omega, leg_l, leg_r])
        self.steps += 1

        # 奖励
        if landed:
            if (abs(theta) < 0.2 and abs(vx) < 0.2 and abs(vy) < 0.3
                    and abs(x - self.landing_x) < self.landing_width):
                reward = 100.0                         # 安全着陆
            else:
                reward = -50.0                          # 坠毁
            done = True
        else:
            reward = (-0.1
                      - 0.1 * abs(theta)
                      - 0.01 * (abs(vx) + abs(vy))
                      + 0.1 * (leg_l + leg_r))         # 生存奖励
            done = self.steps >= self.max_steps or y < -0.5

        return self.state.copy(), float(reward), done


# ============================================================
# §4  环境 Wrappers
# ============================================================

class NormalizeWrapper:
    """状态归一化 wrapper —— 使用运行时均值和方差。"""

    def __init__(self, env: Any, epsilon: float = 1e-4) -> None:
        self.env = env
        self.epsilon = epsilon
        self.mean = np.zeros(env.state_dim if hasattr(env, 'state_dim') else 8)
        self.var = np.ones_like(self.mean)
        self.count = 0

    def reset(self) -> np.ndarray:
        return self._normalize(self.env.reset())

    def step(self, action: Any) -> tuple:
        state, reward, done = self.env.step(action)
        self._update_stats(state)
        return self._normalize(state), reward, done

    def _update_stats(self, x: np.ndarray) -> None:
        self.count += 1
        old_mean = self.mean.copy()
        self.mean += (x - old_mean) / self.count
        self.var += (x - old_mean) * (x - self.mean)

    def _normalize(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / (np.sqrt(self.var / max(self.count, 1)) + self.epsilon)


class FrameStackWrapper:
    """堆叠最近 k 帧作为状态。"""

    def __init__(self, env: Any, k: int = 4) -> None:
        self.env = env
        self.k = k
        self.frames: deque[np.ndarray] = deque(maxlen=k)
        if hasattr(env, 'state_dim'):
            self.state_dim = env.state_dim * k

    def reset(self) -> np.ndarray:
        state = self.env.reset()
        for _ in range(self.k):
            self.frames.append(state.copy())
        return np.concatenate(list(self.frames))

    def step(self, action: Any) -> tuple:
        state, reward, done = self.env.step(action)
        self.frames.append(state.copy())
        return np.concatenate(list(self.frames)), reward, done


class ActionRepeatWrapper:
    """动作重复 wrapper —— 提高采样效率。"""

    def __init__(self, env: Any, repeat: int = 4) -> None:
        self.env = env
        self.repeat = repeat

    def reset(self) -> np.ndarray:
        return self.env.reset()

    def step(self, action: Any) -> tuple:
        total_reward = 0.0
        for _ in range(self.repeat):
            state, reward, done = self.env.step(action)
            total_reward += reward
            if done:
                break
        return state, total_reward, done


# ============================================================
# §5  经验回放变体
# ============================================================

class NStepReplayBuffer:
    """N-step 经验回放 —— 支持多步 TD 学习。"""

    def __init__(self, capacity: int = 10000, n_step: int = 3,
                 gamma: float = 0.99) -> None:
        self.capacity = capacity
        self.n_step = n_step
        self.gamma = gamma
        self.buffer: deque[tuple] = deque(maxlen=capacity)
        self.n_step_buffer: deque[tuple] = deque(maxlen=n_step)

    def push(self, state: np.ndarray, action: Any, reward: float,
             next_state: np.ndarray, done: bool) -> None:
        self.n_step_buffer.append((state, action, reward, next_state, done))
        if len(self.n_step_buffer) < self.n_step:
            return

        # 计算 n-step 奖励和最终状态
        n_reward = 0.0
        for i in range(self.n_step):
            n_reward += (self.gamma ** i) * self.n_step_buffer[i][2]

        first_state = self.n_step_buffer[0][0]
        first_action = self.n_step_buffer[0][1]
        last_next_state = self.n_step_buffer[-1][3]
        last_done = self.n_step_buffer[-1][4]

        self.buffer.append((first_state, first_action, n_reward,
                           last_next_state, last_done))

        if last_done:
            self.n_step_buffer.clear()

    def sample(self, batch_size: int) -> list[tuple]:
        return random.sample(list(self.buffer), min(batch_size, len(self.buffer)))

    def __len__(self) -> int:
        return len(self.buffer)


# ============================================================
# §6  超参数搜索
# ============================================================

class HyperparameterSearch:
    """超参数搜索工具集。"""

    @staticmethod
    def grid_search(param_grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
        """网格搜索 —— 穷举所有组合。"""
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combinations = list(itertools.product(*values))
        return [dict(zip(keys, combo)) for combo in combinations]

    @staticmethod
    def random_search(param_distributions: dict[str, Any],
                      n_iter: int = 100) -> list[dict[str, Any]]:
        """随机搜索 —— 从分布中采样。"""
        configs = []
        for _ in range(n_iter):
            config = {}
            for name, dist in param_distributions.items():
                if isinstance(dist, list):
                    config[name] = random.choice(dist)
                elif hasattr(dist, 'rvs'):       # scipy distribution
                    config[name] = dist.rvs()
                elif isinstance(dist, tuple) and len(dist) == 2:
                    lo, hi = dist
                    config[name] = random.uniform(lo, hi)
            configs.append(config)
        return configs

    @staticmethod
    def bayesian_optimization(objective: Any,
                             param_bounds: dict[str, tuple[float, float]],
                             n_iter: int = 50,
                             kappa: float = 2.576) -> tuple[dict[str, float], float]:
        """
        简化版贝叶斯优化 (使用 Expected Improvement 采集函数)。

        实际应用建议使用 scikit-optimize 或 Optuna 等库。
        """
        X_observed: list[list[float]] = []
        y_observed: list[float] = []
        param_names = list(param_bounds.keys())
        bounds_list = [param_bounds[k] for k in param_names]

        # 初始随机采样
        for _ in range(5):
            x = [random.uniform(lo, hi) for lo, hi in bounds_list]
            X_observed.append(x)
            params = dict(zip(param_names, x))
            y_observed.append(objective(params))

        # 高斯过程代理（简化: RBF 核 + GP 预测）
        def rbf_kernel(x1: np.ndarray, x2: np.ndarray,
                       length_scale: float = 1.0) -> float:
            return float(np.exp(-0.5 * np.sum((x1 - x2)**2) / length_scale**2))

        for _ in range(n_iter):
            X = np.array(X_observed)
            y = np.array(y_observed)
            y_mean = y.mean()
            y_std = y.std() or 1.0
            y_norm = (y - y_mean) / y_std

            # 构建 Gram 矩阵
            n = len(X)
            K = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    K[i, j] = rbf_kernel(X[i], X[j])
            K += 1e-6 * np.eye(n)

            # 采集: 在随机候选上计算 EI
            n_candidates = 1000
            candidates = np.array([
                [random.uniform(lo, hi) for lo, hi in bounds_list]
                for _ in range(n_candidates)
            ])

            best_y = np.max(y)
            best_ei = -1.0
            best_candidate = candidates[0]

            for cand in candidates:
                k_star = np.array([rbf_kernel(cand, X[i]) for i in range(n)])
                k_star_star = 1.0 + 1e-6

                L = np.linalg.cholesky(K)
                alpha = np.linalg.solve(L.T, np.linalg.solve(L, y_norm))
                v = np.linalg.solve(L, k_star)

                mu = float(np.dot(k_star, alpha)) * y_std + y_mean
                sigma = float(np.sqrt(k_star_star - np.dot(v, v))) * y_std

                if sigma < 1e-6:
                    ei = 0.0
                else:
                    z = (mu - best_y - kappa) / sigma
                    ei = (mu - best_y - kappa) * (0.5 * (1 + math.erf(z / math.sqrt(2)))) + sigma * (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * z**2)

                if ei > best_ei:
                    best_ei = ei
                    best_candidate = cand

            X_observed.append(best_candidate.tolist())
            params = dict(zip(param_names, best_candidate))
            y_observed.append(objective(params))

        best_idx = int(np.argmax(y_observed))
        return dict(zip(param_names, X_observed[best_idx])), y_observed[best_idx]


# ============================================================
# §7  演示
# ============================================================

def demo_envs_and_utils() -> None:
    print("=" * 60)
    print("RL 环境与工具集演示")
    print("=" * 60)

    # MountainCar
    print("\n--- MountainCar ---")
    mc = MountainCar()
    state = mc.reset()
    print(f"初始状态: pos={state[0]:.3f}, vel={state[1]:.3f}")

    # 随机走几步
    total_r = 0.0
    for _ in range(5):
        action = random.randint(0, 2)
        state, reward, done = mc.step(action)
        total_r += reward
        if done:
            break
    print(f"随机策略 5步: pos={state[0]:.3f}, velocity={state[1]:.3f}, reward={total_r}")

    # Pendulum
    print("\n--- Pendulum ---")
    pend = Pendulum()
    state = pend.reset()
    print(f"初始状态: cosθ={state[0]:.3f}, sinθ={state[1]:.3f}, θ̇={state[2]:.3f}")

    for _ in range(3):
        action = np.array([random.uniform(-2, 2)])
        state, reward, done = pend.step(action)
        theta = np.arctan2(state[1], state[0])
        print(f"  力矩={action[0]:.2f} -> θ={theta:.3f}, reward={reward:.3f}")

    # LunarLander
    print("\n--- LunarLander ---")
    ll = LunarLander()
    state = ll.reset()
    print(f"初始状态: 位置=({state[0]:.2f},{state[1]:.2f}), 速度=({state[2]:.2f},{state[3]:.2f})")

    for step in range(5):
        action = random.randint(0, 3)
        state, reward, done = ll.step(action)
        action_names = ["nothing", "left", "main", "right"]
        print(f"  动作={action_names[action]} -> 位置=({state[0]:.2f},{state[1]:.2f}), "
              f"reward={reward:.1f}, done={done}")
        if done:
            break

    # Wrappers
    print("\n--- Wrappers ---")
    norm_env = NormalizeWrapper(mc)
    state = norm_env.reset()
    print(f"归一化后状态: {state}")

    stack_env = FrameStackWrapper(mc, k=4)
    state = stack_env.reset()
    print(f"帧堆叠 (k=4): {state.shape} -> {state}")

    # N-step buffer
    print("\n--- N-step Buffer ---")
    buffer = NStepReplayBuffer(capacity=100, n_step=3, gamma=0.99)
    for i in range(10):
        buffer.push(np.array([i]), i % 2, 1.0, np.array([i + 1]), i == 9)
    sample = buffer.sample(3)
    print(f"buffer 大小: {len(buffer)}, 采样 3 条: {[s[1] for s in sample]}")

    # Hyperparameter search
    print("\n--- 超参数搜索 ---")
    param_grid = {"lr": [0.001, 0.01, 0.1], "batch_size": [32, 64]}
    grid = HyperparameterSearch.grid_search(param_grid)
    print(f"网格搜索 ({len(param_grid)} params): {len(grid)} 组合")
    for g in grid:
        print(f"  {g}")

    random_configs = HyperparameterSearch.random_search(
        {"lr": [0.0001, 0.001, 0.01], "gamma": (0.9, 0.999)}, n_iter=5
    )
    print(f"随机搜索 5 组:")
    for c in random_configs:
        print(f"  {c}")

    # 贝叶斯优化 (玩具示例)
    print("\n--- 贝叶斯优化 (玩具函数) ---")
    dummy_objective = lambda p: -(p["x"] - 2)**2 - (p["y"] + 3)**2 + 10
    best_params, best_val = HyperparameterSearch.bayesian_optimization(
        dummy_objective, {"x": (-5.0, 5.0), "y": (-5.0, 5.0)}, n_iter=20
    )
    print(f"最优参数: {best_params}")
    print(f"最优值: {best_val:.3f} (期望: x=2, y=-3, f=10)")


if __name__ == "__main__":
    demo_envs_and_utils()
    print("\n✅ RL 环境工具篇执行完毕!")
