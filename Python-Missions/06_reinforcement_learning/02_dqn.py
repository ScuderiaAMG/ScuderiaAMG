#!/usr/bin/env python3
"""
深度 Q 网络 (DQN) —— 完整从零实现
涵盖：经验回放缓冲区、Target Network、Double DQN、Dueling DQN、
      Prioritized Experience Replay、CartPole 环境、
      完整的训练 + 评估流程
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from collections import deque, namedtuple
from typing import Any
import random

# 常量
Transition = namedtuple("Transition",
                        ["state", "action", "reward", "next_state", "done"])


# ============================================================
# §1  经验回放缓冲区
# ============================================================

class ReplayBuffer:
    """标准经验回放缓冲区 (FIFO)。"""

    def __init__(self, capacity: int = 10000) -> None:
        self.buffer: deque[Transition] = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: int, reward: float,
             next_state: np.ndarray, done: bool) -> None:
        self.buffer.append(Transition(state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> list[Transition]:
        return random.sample(self.buffer, batch_size)

    def __len__(self) -> int:
        return len(self.buffer)


class PrioritizedReplayBuffer:
    """优先经验回放 (PER) — 基于 TD 误差的采样权重。"""

    def __init__(self, capacity: int = 10000, alpha: float = 0.6,
                 beta: float = 0.4, beta_increment: float = 0.001,
                 epsilon: float = 1e-6) -> None:
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.epsilon = epsilon

        self.buffer: list[Transition] = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.pos = 0
        self.size = 0

    def push(self, state: np.ndarray, action: int, reward: float,
             next_state: np.ndarray, done: bool) -> None:
        max_prio = self.priorities.max() if self.size > 0 else 1.0
        if self.size < self.capacity:
            self.buffer.append(Transition(state, action, reward, next_state, done))
        else:
            self.buffer[self.pos] = Transition(state, action, reward, next_state, done)
        self.priorities[self.pos] = max_prio
        self.pos = (self.pos + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size: int) -> tuple[list[Transition], np.ndarray, np.ndarray]:
        if self.size < self.capacity:
            probs = self.priorities[:self.size] ** self.alpha
        else:
            probs = self.priorities ** self.alpha
        probs /= probs.sum()

        indices = np.random.choice(self.size, batch_size, p=probs)
        samples = [self.buffer[i] for i in indices]

        # 重要性采样权重
        total = self.size
        weights = (total * probs[indices]) ** (-self.beta)
        weights /= weights.max()

        self.beta = min(1.0, self.beta + self.beta_increment)
        return samples, indices, weights

    def update_priorities(self, indices: np.ndarray, td_errors: np.ndarray) -> None:
        for idx, td_error in zip(indices, td_errors):
            self.priorities[idx] = abs(td_error) + self.epsilon

    def __len__(self) -> int:
        return self.size


# ============================================================
# §2  Q 网络架构
# ============================================================

class DQN(nn.Module):
    """标准 DQN 网络。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 128) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class DuelingDQN(nn.Module):
    """Dueling DQN — 分离 Value 和 Advantage。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 128) -> None:
        super().__init__()
        self.feature = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
        )
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.feature(x)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        # Q(s,a) = V(s) + A(s,a) - mean(A(s,·))
        return value + advantage - advantage.mean(dim=1, keepdim=True)


# ============================================================
# §3  DQN Agent
# ============================================================

class DQNAgent:
    """DQN 智能体 (支持 Double DQN、Dueling、PER)。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 128,
                 lr: float = 1e-3,
                 gamma: float = 0.99,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.01,
                 epsilon_decay: float = 0.995,
                 target_update: int = 10,
                 batch_size: int = 64,
                 buffer_capacity: int = 10000,
                 use_double: bool = True,
                 use_dueling: bool = False,
                 use_per: bool = False,
                 device: str = "cpu") -> None:
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.target_update = target_update
        self.batch_size = batch_size
        self.use_double = use_double
        self.use_per = use_per
        self.device = torch.device(device)

        # 网络
        net_class = DuelingDQN if use_dueling else DQN
        self.q_network = net_class(state_dim, action_dim, hidden_dim).to(self.device)
        self.target_network = net_class(state_dim, action_dim, hidden_dim).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)

        # 回放缓冲区
        if use_per:
            self.memory: Any = PrioritizedReplayBuffer(capacity=buffer_capacity)
        else:
            self.memory = ReplayBuffer(capacity=buffer_capacity)

        self.steps_done = 0

    def select_action(self, state: np.ndarray, evaluate: bool = False) -> int:
        if not evaluate and random.random() < self.epsilon:
            return random.randrange(self.action_dim)

        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return int(q_values.argmax(dim=1).item())

    def store_transition(self, state: np.ndarray, action: int,
                         reward: float, next_state: np.ndarray,
                         done: bool) -> None:
        self.memory.push(state, action, reward, next_state, done)

    def update(self) -> float | None:
        if len(self.memory) < self.batch_size:
            return None

        # 采样
        if self.use_per:
            transitions, indices, weights = self.memory.sample(self.batch_size)
            weights_tensor = torch.FloatTensor(weights).unsqueeze(1).to(self.device)
        else:
            transitions = self.memory.sample(self.batch_size)
            weights_tensor = None

        batch = Transition(*zip(*transitions))

        states = torch.FloatTensor(np.array(batch.state)).to(self.device)
        actions = torch.LongTensor(batch.action).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(batch.reward).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(np.array(batch.next_state)).to(self.device)
        dones = torch.FloatTensor(batch.done).unsqueeze(1).to(self.device)

        # 当前 Q 值
        current_q = self.q_network(states).gather(1, actions)

        with torch.no_grad():
            if self.use_double:
                # Double DQN: 用 online 网络选动作，target 网络估值
                next_actions = self.q_network(next_states).argmax(1, keepdim=True)
                next_q = self.target_network(next_states).gather(1, next_actions)
            else:
                next_q = self.target_network(next_states).max(1, keepdim=True)[0]

            target_q = rewards + self.gamma * next_q * (1 - dones)

        # 损失
        if weights_tensor is not None:
            loss = (weights_tensor * F.smooth_l1_loss(current_q, target_q,
                                                       reduction="none")).mean()
        else:
            loss = F.smooth_l1_loss(current_q, target_q)

        # 优化
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=10.0)
        self.optimizer.step()

        # 更新 PER 优先级
        if self.use_per:
            td_errors = (target_q - current_q).detach().cpu().numpy().flatten()
            self.memory.update_priorities(indices, td_errors)

        return float(loss.item())

    def decay_epsilon(self) -> None:
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def update_target(self) -> None:
        self.target_network.load_state_dict(self.q_network.state_dict())

    def save(self, path: str) -> None:
        torch.save({
            "q_network": self.q_network.state_dict(),
            "target_network": self.target_network.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
        }, path)

    def load(self, path: str) -> None:
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint["q_network"])
        self.target_network.load_state_dict(checkpoint["target_network"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.epsilon = checkpoint["epsilon"]


# ============================================================
# §4  CartPole 环境（自实现）
# ============================================================

class CartPole:
    """经典 CartPole 环境的 NumPy 实现。

    状态: [cart_position, cart_velocity, pole_angle, pole_angular_velocity]
    动作: 0=左推, 1=右推
    """

    def __init__(self) -> None:
        self.gravity = 9.8
        self.mass_cart = 1.0
        self.mass_pole = 0.1
        self.total_mass = self.mass_cart + self.mass_pole
        self.length = 0.5                         # 半杆长
        self.pole_mass_length = self.mass_pole * self.length
        self.force_mag = 10.0
        self.tau = 0.02                           # 时间步长
        self.theta_threshold = 12 * np.pi / 180    # 12 度
        self.x_threshold = 2.4

        self.state: np.ndarray | None = None

    def reset(self) -> np.ndarray:
        self.state = np.random.uniform(-0.05, 0.05, size=4)
        return self.state.copy()

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        x, x_dot, theta, theta_dot = self.state  # type: ignore[misc]
        force = self.force_mag if action == 1 else -self.force_mag

        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        temp = (force + self.pole_mass_length * theta_dot ** 2 * sin_theta) / self.total_mass
        theta_acc = (self.gravity * sin_theta - cos_theta * temp) / \
                    (self.length * (4.0 / 3.0 - self.mass_pole * cos_theta ** 2 / self.total_mass))
        x_acc = temp - self.pole_mass_length * theta_acc * cos_theta / self.total_mass

        # 欧拉积分
        x = x + self.tau * x_dot
        x_dot = x_dot + self.tau * x_acc
        theta = theta + self.tau * theta_dot
        theta_dot = theta_dot + self.tau * theta_acc

        self.state = np.array([x, x_dot, theta, theta_dot])

        done = abs(x) > self.x_threshold or abs(theta) > self.theta_threshold
        reward = 1.0 if not done else 0.0

        return self.state.copy(), reward, done

    @property
    def state_dim(self) -> int:
        return 4

    @property
    def action_dim(self) -> int:
        return 2


# ============================================================
# §5  训练与评估
# ============================================================

def train_dqn(agent: DQNAgent, env: Any, episodes: int = 300,
              max_steps: int = 500, update_freq: int = 4,
              verbose: bool = True) -> list[float]:
    """训练 DQN 智能体。"""
    episode_rewards: list[float] = []
    running_reward = 0.0

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0.0

        for step in range(max_steps):
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.store_transition(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

            if step % update_freq == 0:
                agent.update()

            if done:
                break

        agent.decay_epsilon()

        if ep % agent.target_update == 0:
            agent.update_target()

        episode_rewards.append(total_reward)
        running_reward = 0.05 * total_reward + 0.95 * running_reward

        if verbose and (ep + 1) % 50 == 0:
            recent = np.mean(episode_rewards[-50:])
            print(f"Episode {ep+1:4d}/{episodes} | "
                  f"reward: {total_reward:6.1f} | "
                  f"avg50: {recent:6.1f} | "
                  f"epsilon: {agent.epsilon:.3f}")

    return episode_rewards


def evaluate(agent: DQNAgent, env: Any, n_episodes: int = 10,
             max_steps: int = 500) -> float:
    """评估智能体（无探索）。"""
    total_rewards = 0.0
    for _ in range(n_episodes):
        state = env.reset()
        ep_reward = 0.0
        for _ in range(max_steps):
            action = agent.select_action(state, evaluate=True)
            state, reward, done = env.step(action)
            ep_reward += reward
            if done:
                break
        total_rewards += ep_reward
    return total_rewards / n_episodes


def demo_dqn_cartpole() -> None:
    print("=" * 60)
    print("DQN 在 CartPole 上的训练")
    print("=" * 60)

    env = CartPole()

    # 标准 DQN
    print("\n--- 标准 DQN (with Double DQN) ---")
    agent_dqn = DQNAgent(
        state_dim=env.state_dim,
        action_dim=env.action_dim,
        hidden_dim=64,
        lr=1e-3,
        gamma=0.99,
        epsilon_decay=0.995,
        target_update=10,
        batch_size=64,
        buffer_capacity=5000,
        use_double=True,
        use_dueling=False,
        use_per=False,
    )
    dqn_rewards = train_dqn(agent_dqn, env, episodes=300, verbose=True)
    dqn_score = evaluate(agent_dqn, env, n_episodes=50)

    # Dueling DQN
    print("\n--- Dueling DQN ---")
    agent_dueling = DQNAgent(
        state_dim=env.state_dim,
        action_dim=env.action_dim,
        hidden_dim=64,
        lr=1e-3,
        epsilon_decay=0.995,
        target_update=10,
        batch_size=64,
        buffer_capacity=5000,
        use_double=True,
        use_dueling=True,
        use_per=False,
    )
    dueling_rewards = train_dqn(agent_dueling, env, episodes=300, verbose=True)
    dueling_score = evaluate(agent_dueling, env, n_episodes=50)

    print(f"\n{'='*60}")
    print(f"最终评估 (50 episodes):")
    print(f"  Double DQN:     {dqn_score:.1f}")
    print(f"  Dueling DQN:    {dueling_score:.1f}")


def demo_q_value_analysis() -> None:
    """展示 Q 值过估计问题及 Double DQN 的缓解。"""
    print("\n" + "=" * 60)
    print("Q 值过估计演示")
    print("=" * 60)

    # 对随机状态的 Q 值估计
    state_dim, action_dim = 4, 4
    net = DQN(state_dim, action_dim, hidden_dim=32)

    states = torch.randn(100, state_dim)
    with torch.no_grad():
        q_values = net(states)

    max_q = q_values.max(dim=1)[0]
    print(f"随机状态的 Q 值范围: [{max_q.min().item():.3f}, {max_q.max().item():.3f}]")
    print(f"平均 max Q: {max_q.mean().item():.3f}")
    print(f"真值应为 0（随机初始化网络在随机状态上的期望 Q 值）")
    print("说明: Q-learning 的 max 操作导致系统性过估计，")
    print("Double Q-Learning 通过解耦动作选择和估值来缓解此问题。")


if __name__ == "__main__":
    demo_q_value_analysis()
    demo_dqn_cartpole()
    print("\n✅ DQN 篇全部执行完毕!")
