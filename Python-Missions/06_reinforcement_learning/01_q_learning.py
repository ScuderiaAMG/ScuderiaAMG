#!/usr/bin/env python3
"""
强化学习 —— 表格型 Q-Learning 与 SARSA
涵盖：GridWorld / FrozenLake 环境、ε-贪婪策略、Q 表更新、
      SARSA (on-policy)、Q-Learning (off-policy)、Double Q-Learning、
      超参数对收敛的影响分析
"""

import numpy as np
from collections import defaultdict
from typing import Any
import itertools

rng = np.random.default_rng(42)


# ============================================================
# §1  GridWorld 环境
# ============================================================

class GridWorld:
    """可配置的网格世界环境。

    状态: (row, col) 坐标
    动作: 0=上, 1=右, 2=下, 3=左
    奖励: 目标 +10, 陷阱 -10, 每步 -1
    """

    def __init__(self, rows: int = 5, cols: int = 5,
                 start: tuple[int, int] = (0, 0),
                 goal: tuple[int, int] = (4, 4),
                 traps: list[tuple[int, int]] | None = None) -> None:
        self.rows = rows
        self.cols = cols
        self.start = start
        self.goal = goal
        self.traps = traps or [(2, 2)]

        self.action_deltas = {
            0: (-1, 0),  # 上
            1: (0, 1),   # 右
            2: (1, 0),   # 下
            3: (0, -1),  # 左
        }
        self.state = start

    def reset(self) -> tuple[int, int]:
        self.state = self.start
        return self.state

    def step(self, action: int) -> tuple[tuple[int, int], float, bool]:
        dr, dc = self.action_deltas[action]
        r, c = self.state
        nr = max(0, min(self.rows - 1, r + dr))
        nc = max(0, min(self.cols - 1, c + dc))
        self.state = (nr, nc)

        if self.state == self.goal:
            return self.state, 10.0, True
        if self.state in self.traps:
            return self.state, -10.0, True
        return self.state, -1.0, False

    @property
    def n_states(self) -> int:
        return self.rows * self.cols

    @property
    def n_actions(self) -> int:
        return 4

    def state_to_idx(self, state: tuple[int, int]) -> int:
        return state[0] * self.cols + state[1]


# ============================================================
# §2  ε-贪婪策略
# ============================================================

class EpsilonGreedy:
    def __init__(self, epsilon: float = 0.1, decay: float = 0.999,
                 min_epsilon: float = 0.01) -> None:
        self.epsilon = epsilon
        self.decay = decay
        self.min_epsilon = min_epsilon

    def select_action(self, q_table: np.ndarray, state: int,
                      n_actions: int) -> int:
        if rng.random() < self.epsilon:
            return rng.integers(0, n_actions)
        return int(np.argmax(q_table[state]))

    def decay_epsilon(self) -> None:
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)

    def greedy_action(self, q_table: np.ndarray, state: int) -> int:
        return int(np.argmax(q_table[state]))


# ============================================================
# §3  Q-Learning (Off-Policy)
# ============================================================

def q_learning(
    env: GridWorld,
    episodes: int = 500,
    alpha: float = 0.1,
    gamma: float = 0.99,
    epsilon: float = 0.1,
) -> tuple[np.ndarray, list[float], list[int]]:
    """
    Q-Learning 算法:
    Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') - Q(s,a)]
    """

    q_table = np.zeros((env.n_states, env.n_actions))
    policy = EpsilonGreedy(epsilon)
    episode_rewards: list[float] = []
    episode_steps: list[int] = []

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0.0
        steps = 0
        done = False

        while not done:
            state_idx = env.state_to_idx(state)
            action = policy.select_action(q_table, state_idx, env.n_actions)

            next_state, reward, done = env.step(action)
            next_state_idx = env.state_to_idx(next_state)

            # Q-Learning 更新 (off-policy: max over Q)
            best_next_action = np.argmax(q_table[next_state_idx])
            td_target = reward + gamma * q_table[next_state_idx, best_next_action]
            td_error = td_target - q_table[state_idx, action]
            q_table[state_idx, action] += alpha * td_error

            state = next_state
            total_reward += reward
            steps += 1

        policy.decay_epsilon()
        episode_rewards.append(total_reward)
        episode_steps.append(steps)

    return q_table, episode_rewards, episode_steps


# ============================================================
# §4  SARSA (On-Policy)
# ============================================================

def sarsa(
    env: GridWorld,
    episodes: int = 500,
    alpha: float = 0.1,
    gamma: float = 0.99,
    epsilon: float = 0.1,
) -> tuple[np.ndarray, list[float], list[int]]:
    """
    SARSA 算法:
    Q(s,a) ← Q(s,a) + α [r + γ Q(s',a') - Q(s,a)]
    关键区别: a' 由当前策略采样（On-policy）
    """

    q_table = np.zeros((env.n_states, env.n_actions))
    policy = EpsilonGreedy(epsilon)
    episode_rewards: list[float] = []
    episode_steps: list[int] = []

    for ep in range(episodes):
        state = env.reset()
        state_idx = env.state_to_idx(state)
        action = policy.select_action(q_table, state_idx, env.n_actions)
        total_reward = 0.0
        steps = 0
        done = False

        while not done:
            next_state, reward, done = env.step(action)
            next_state_idx = env.state_to_idx(next_state)

            # 提前选择下一个动作（On-policy）
            next_action = policy.select_action(q_table, next_state_idx, env.n_actions)

            td_target = reward + gamma * q_table[next_state_idx, next_action]
            td_error = td_target - q_table[state_idx, action]
            q_table[state_idx, action] += alpha * td_error

            state = next_state
            state_idx = next_state_idx
            action = next_action
            total_reward += reward
            steps += 1

        policy.decay_epsilon()
        episode_rewards.append(total_reward)
        episode_steps.append(steps)

    return q_table, episode_rewards, episode_steps


# ============================================================
# §5  Double Q-Learning
# ============================================================

def double_q_learning(
    env: GridWorld,
    episodes: int = 500,
    alpha: float = 0.1,
    gamma: float = 0.99,
    epsilon: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, list[float], list[int]]:
    """
    Double Q-Learning — 使用两个 Q 表缓解最大化偏差:
    Q_A(s,a) ← Q_A(s,a) + α [r + γ Q_B(s', argmax_a' Q_A(s',a')) - Q_A(s,a)]
    Q_B 同理，每次随机选择更新哪个表。
    """

    q_a = np.zeros((env.n_states, env.n_actions))
    q_b = np.zeros((env.n_states, env.n_actions))
    policy = EpsilonGreedy(epsilon)
    episode_rewards: list[float] = []
    episode_steps: list[int] = []

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0.0
        steps = 0
        done = False

        while not done:
            state_idx = env.state_to_idx(state)
            # 使用两个 Q 表的均值选择动作
            combined_q = q_a + q_b
            action = policy.select_action(combined_q, state_idx, env.n_actions)

            next_state, reward, done = env.step(action)
            next_state_idx = env.state_to_idx(next_state)

            if rng.random() < 0.5:
                # 更新 Q_A
                best_a = np.argmax(q_a[next_state_idx])
                td_target = reward + gamma * q_b[next_state_idx, best_a]
                q_a[state_idx, action] += alpha * (td_target - q_a[state_idx, action])
            else:
                # 更新 Q_B
                best_b = np.argmax(q_b[next_state_idx])
                td_target = reward + gamma * q_a[next_state_idx, best_b]
                q_b[state_idx, action] += alpha * (td_target - q_b[state_idx, action])

            state = next_state
            total_reward += reward
            steps += 1

        policy.decay_epsilon()
        episode_rewards.append(total_reward)
        episode_steps.append(steps)

    return q_a, q_b, episode_rewards, episode_steps


# ============================================================
# §6  演示与对比
# ============================================================

def demo_gridworld_q_learning() -> None:
    print("=" * 60)
    print("Q-Learning 在 GridWorld 上的训练")
    print("=" * 60)

    env = GridWorld(rows=5, cols=5)
    q_table, rewards, steps = q_learning(env, episodes=400, alpha=0.1, gamma=0.99)

    # 打印 Q 表
    print("\n训练后的 Q 表 (每状态的最佳动作值):")
    actions_symbols = ["↑", "→", "↓", "←"]
    for r in range(env.rows):
        row_str = ""
        for c in range(env.cols):
            state_idx = r * env.cols + c
            best_a = np.argmax(q_table[state_idx])
            max_q = np.max(q_table[state_idx])
            row_str += f"  {actions_symbols[best_a]}({max_q:5.1f})"
        print(row_str)

    # 评估策略
    policy = EpsilonGreedy(epsilon=0.0)          # 纯贪婪策略评估
    env_test = GridWorld(rows=5, cols=5)
    state = env_test.reset()
    path = [state]
    total_reward = 0.0
    done = False
    while not done:
        state_idx = env_test.state_to_idx(state)
        action = policy.greedy_action(q_table, state_idx)
        next_state, reward, done = env_test.step(action)
        path.append(next_state)
        total_reward += reward
        state = next_state
        if len(path) > 50:                       # 防止死循环
            break

    print(f"\n最优路径: {' -> '.join(str(p) for p in path)}")
    print(f"总奖励: {total_reward}")

    # 训练曲线摘要
    print(f"\n前 20 个 episode 均奖励: {np.mean(rewards[:20]):.1f}")
    print(f"最后 20 个 episode 均奖励: {np.mean(rewards[-20:]):.1f}")


def demo_algorithm_comparison() -> None:
    print("\n" + "=" * 60)
    print("Q-Learning vs SARSA vs Double Q-Learning 对比")
    print("=" * 60)

    episodes = 300

    # 多次运行取平均
    n_runs = 3
    all_ql_rewards: list[np.ndarray] = []
    all_sarsa_rewards: list[np.ndarray] = []
    all_dql_rewards: list[np.ndarray] = []

    for run in range(n_runs):
        env1 = GridWorld()
        env2 = GridWorld()
        env3 = GridWorld()

        _, ql_r, _ = q_learning(env1, episodes=episodes)
        _, sarsa_r, _ = sarsa(env2, episodes=episodes)
        _, _, dql_r, _ = double_q_learning(env3, episodes=episodes)

        all_ql_rewards.append(ql_r)
        all_sarsa_rewards.append(sarsa_r)
        all_dql_rewards.append(dql_r)

    # 平均
    ql_mean = np.mean(all_ql_rewards, axis=0)
    sarsa_mean = np.mean(all_sarsa_rewards, axis=0)
    dql_mean = np.mean(all_dql_rewards, axis=0)

    # 平滑
    def smooth(data: np.ndarray, window: int = 10) -> np.ndarray:
        return np.convolve(data, np.ones(window) / window, mode="valid")

    print(f"{'算法':<25} {'前 20 ep 均奖励':>16} {'最后 20 ep 均奖励':>18}")
    print(f"{'Q-Learning':<25} {ql_mean[:20].mean():>16.1f} {ql_mean[-20:].mean():>18.1f}")
    print(f"{'SARSA':<25} {sarsa_mean[:20].mean():>16.1f} {sarsa_mean[-20:].mean():>18.1f}")
    print(f"{'Double Q-Learning':<25} {dql_mean[:20].mean():>16.1f} {dql_mean[-20:].mean():>18.1f}")

    print("\n注: 在确定性环境中 Q-Learning 通常收敛更快；")
    print("在随机环境中 SARSA 更保守安全；Double Q-Learning 缓解高估偏差。")


# ============================================================
# §7  FrozenLake 环境（自实现）
# ============================================================

class FrozenLake:
    """4x4 FrozenLake 风格环境。

    状态索引:
     0  1  2  3
     4  5  6  7
     8  9 10 11
    12 13 14 15

    目标状态: 15，陷阱: 5, 7, 11, 12
    动作: 0=左, 1=下, 2=右, 3=上
    随机性: 每个动作有 1/3 概率滑到相邻方向
    """

    def __init__(self) -> None:
        self.n_states = 16
        self.n_actions = 4
        self.goal = 15
        self.holes = {5, 7, 11, 12}
        self.state = 0

        # 预计算转移表 (含随机性)
        self._build_transitions()

    def _build_transitions(self) -> None:
        """构建随机转移概率表。"""
        self.P: dict[int, dict[int, list[tuple[float, int, float, bool]]]] = {}

        action_deltas = {
            0: (0, -1),   # 左
            1: (1, 0),    # 下
            2: (0, 1),    # 右
            3: (-1, 0),   # 上
        }

        for s in range(16):
            self.P[s] = {}
            r, c = divmod(s, 4)
            for a in range(4):
                transitions = []
                # 主方向 (1/3) + 两个侧方向 (各 1/3)
                for drift, prob in [(0, 1/3), (-1, 1/3), (1, 1/3)]:
                    actual_a = (a + drift) % 4
                    dr, dc = action_deltas[actual_a]
                    nr = max(0, min(3, r + dr))
                    nc = max(0, min(3, c + dc))
                    next_s = nr * 4 + nc

                    if next_s == self.goal:
                        reward, done = 1.0, True
                    elif next_s in self.holes:
                        reward, done = 0.0, True
                    else:
                        reward, done = 0.0, False

                    transitions.append((prob, next_s, reward, done))
                self.P[s][a] = transitions

    def reset(self) -> int:
        self.state = 0
        return self.state

    def step(self, action: int) -> tuple[int, float, bool]:
        transitions = self.P[self.state][action]
        probs, next_states, rewards, dones = zip(*transitions)
        idx = rng.choice(len(probs), p=probs)
        self.state = next_states[idx]            # type: ignore[assignment]
        return self.state, rewards[idx], dones[idx]  # type: ignore[return-value]


def demo_frozen_lake() -> None:
    print("\n" + "=" * 60)
    print("FrozenLake — 随机环境中的 Q-Learning")
    print("=" * 60)

    env = FrozenLake()
    q_table = np.zeros((env.n_states, env.n_actions))
    policy = EpsilonGreedy(epsilon=0.3, decay=0.995, min_epsilon=0.01)
    success_history: list[int] = []

    episodes = 2000
    alpha = 0.1
    gamma = 0.99

    for ep in range(episodes):
        state = env.reset()
        done = False
        success = 0

        while not done:
            action = policy.select_action(q_table, state, env.n_actions)
            next_state, reward, done = env.step(action)

            best_next = np.argmax(q_table[next_state])
            td_target = reward + gamma * q_table[next_state, best_next]
            q_table[state, action] += alpha * (td_target - q_table[state, action])

            state = next_state
            if done and reward > 0:
                success = 1

        policy.decay_epsilon()
        success_history.append(success)

    # 评估最终策略
    eval_episodes = 100
    successes = 0
    for _ in range(eval_episodes):
        state = env.reset()
        done = False
        while not done:
            action = np.argmax(q_table[state])
            state, reward, done = env.step(action)
            if done and reward > 0:
                successes += 1

    print(f"Q 表收敛后的最优策略:")
    arrows = ["←", "↓", "→", "↑"]
    for r in range(4):
        row_str = ""
        for c in range(4):
            s = r * 4 + c
            if s == env.goal:
                row_str += "  🏁 "
            elif s in env.holes:
                row_str += "  💀 "
            else:
                row_str += f"  {arrows[np.argmax(q_table[s])]} "
            # print value too
            row_str += f"({np.max(q_table[s]):.2f})"
        print(row_str)

    print(f"\n评估成功率: {successes}/{eval_episodes} = {successes/eval_episodes:.1%}")
    last_100 = np.mean(success_history[-100:])
    print(f"训练最后 100 episode 平均成功率: {last_100:.1%}")


if __name__ == "__main__":
    demo_gridworld_q_learning()
    demo_algorithm_comparison()
    demo_frozen_lake()
    print("\n✅ Q-Learning 篇全部执行完毕!")
