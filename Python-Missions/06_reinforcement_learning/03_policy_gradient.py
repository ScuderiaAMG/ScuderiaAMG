#!/usr/bin/env python3
"""
策略梯度方法 —— 从 REINFORCE 到 A2C
涵盖：REINFORCE (蒙特卡洛策略梯度)、带基线的 REINFORCE、
      Actor-Critic (A2C)、GAE (广义优势估计)、
      连续动作空间的策略梯度
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from collections import namedtuple, deque
from typing import Any
import random
import math

Trajectory = namedtuple("Trajectory",
                        ["states", "actions", "rewards", "log_probs", "dones"])


# ============================================================
# §1  策略网络
# ============================================================

class DiscretePolicy(nn.Module):
    """离散动作空间的策略网络。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 128) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.distributions.Categorical:
        logits = self.net(x)
        return torch.distributions.Categorical(logits=logits)

    def get_action(self, state: torch.Tensor,
                   evaluate: bool = False) -> tuple[int, torch.Tensor]:
        dist = self(state)
        if evaluate:
            action = torch.argmax(dist.probs, dim=-1)
        else:
            action = dist.sample()
        log_prob = dist.log_prob(action)
        return int(action.item()), log_prob


class ContinuousPolicy(nn.Module):
    """连续动作空间的策略网络 (高斯策略)。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 128, log_std_min: float = -20,
                 log_std_max: float = 2) -> None:
        super().__init__()
        self.log_std_min = log_std_min
        self.log_std_max = log_std_max

        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )
        self.mean_head = nn.Linear(hidden_dim, action_dim)
        self.log_std_head = nn.Linear(hidden_dim, action_dim)

    def forward(self, x: torch.Tensor) -> torch.distributions.Normal:
        features = self.net(x)
        mean = self.mean_head(features)
        log_std = self.log_std_head(features)
        log_std = torch.clamp(log_std, self.log_std_min, self.log_std_max)
        std = torch.exp(log_std)
        return torch.distributions.Normal(mean, std)

    def get_action(self, state: torch.Tensor,
                   evaluate: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
        dist = self(state)
        if evaluate:
            action = dist.mean
        else:
            action = dist.rsample()              # reparameterization trick
        log_prob = dist.log_prob(action).sum(dim=-1)
        # 将 action 裁剪到 [-1, 1]（假设环境需要）
        action = torch.tanh(action)
        return action, log_prob


# ============================================================
# §2  价值网络 (Critic)
# ============================================================

class ValueNetwork(nn.Module):
    """状态价值函数 V(s) 或 状态-动作价值函数 Q(s,a)。"""

    def __init__(self, state_dim: int, hidden_dim: int = 128) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ============================================================
# §3  REINFORCE (蒙特卡洛策略梯度)
# ============================================================

class REINFORCE:
    """REINFORCE — 最基础的策略梯度算法。"""

    def __init__(self, policy: DiscretePolicy, lr: float = 1e-3,
                 gamma: float = 0.99) -> None:
        self.policy = policy
        self.optimizer = optim.Adam(policy.parameters(), lr=lr)
        self.gamma = gamma

    def compute_returns(self, rewards: list[float],
                        dones: list[bool]) -> torch.Tensor:
        """计算折扣回报 G_t = Σ γ^k r_{t+k}。"""
        returns = []
        G = 0.0
        for reward, done in zip(reversed(rewards), reversed(dones)):
            if done:
                G = 0.0
            G = reward + self.gamma * G
            returns.insert(0, G)

        returns_tensor = torch.tensor(returns, dtype=torch.float32)
        # 标准化回报（稳定性提升）
        returns_tensor = (returns_tensor - returns_tensor.mean()) / (returns_tensor.std() + 1e-8)
        return returns_tensor

    def update(self, states: torch.Tensor, actions: list[int],
               rewards: list[float], log_probs: list[torch.Tensor],
               dones: list[bool]) -> float:
        returns = self.compute_returns(rewards, dones)

        log_prob_tensor = torch.stack(log_probs)
        policy_loss = -(log_prob_tensor * returns).mean()

        self.optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=1.0)
        self.optimizer.step()

        return float(policy_loss.item())


class REINFORCEWithBaseline(REINFORCE):
    """REINFORCE with Baseline — 减去 V(s) 降低方差。"""

    def __init__(self, policy: DiscretePolicy, value_net: ValueNetwork,
                 lr_policy: float = 1e-3, lr_value: float = 1e-3,
                 gamma: float = 0.99) -> None:
        super().__init__(policy, lr_policy, gamma)
        self.value_net = value_net
        self.value_optimizer = optim.Adam(value_net.parameters(), lr=lr_value)

    def update(self, states: torch.Tensor, actions: list[int],
               rewards: list[float], log_probs: list[torch.Tensor],
               dones: list[bool]) -> float:
        returns = self.compute_returns(rewards, dones)

        # Critic update
        values = self.value_net(states).squeeze()
        value_loss = F.mse_loss(values, returns)

        self.value_optimizer.zero_grad()
        value_loss.backward()
        self.value_optimizer.step()

        # Actor update (with advantage = returns - baseline)
        with torch.no_grad():
            advantages = returns - self.value_net(states).squeeze()

        log_prob_tensor = torch.stack(log_probs)
        policy_loss = -(log_prob_tensor * advantages).mean()

        self.optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=1.0)
        self.optimizer.step()

        return float(policy_loss.item())


# ============================================================
# §4  A2C (Advantage Actor-Critic)
# ============================================================

class A2C:
    """同步 Advantage Actor-Critic。

    使用 n-step TD 或 GAE 估计优势函数，
    同时更新 Actor (策略) 和 Critic (价值函数)。
    """

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 128, lr: float = 3e-4,
                 gamma: float = 0.99, gae_lambda: float = 0.95,
                 entropy_coef: float = 0.01,
                 value_coef: float = 0.5,
                 max_grad_norm: float = 0.5,
                 n_steps: int = 5) -> None:
        self.actor = DiscretePolicy(state_dim, action_dim, hidden_dim)
        self.critic = ValueNetwork(state_dim, hidden_dim)
        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=lr,
        )
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm
        self.n_steps = n_steps

    def compute_gae(self, rewards: list[float], values: list[float],
                    dones: list[bool]) -> tuple[torch.Tensor, torch.Tensor]:
        """广义优势估计 (GAE)。"""
        advantages = []
        gae = 0.0
        next_value = 0.0
        for t in reversed(range(len(rewards))):
            if dones[t]:
                next_value = 0.0
                gae = 0.0
            delta = rewards[t] + self.gamma * next_value - values[t]
            gae = delta + self.gamma * self.gae_lambda * gae
            advantages.insert(0, gae)
            next_value = values[t]

        advantages_tensor = torch.tensor(advantages, dtype=torch.float32)
        returns = advantages_tensor + torch.tensor(values, dtype=torch.float32)
        # 标准化优势
        advantages_tensor = (advantages_tensor - advantages_tensor.mean()) / \
                            (advantages_tensor.std() + 1e-8)
        return advantages_tensor, returns

    def update(self, states: torch.Tensor, actions: list[int],
               rewards: list[float], log_probs: list[torch.Tensor],
               dones: list[bool]) -> dict[str, float]:
        # 计算价值
        with torch.no_grad():
            values_list = self.critic(states).squeeze().tolist()
            if isinstance(values_list, float):
                values_list = [values_list]

        advantages, returns = self.compute_gae(rewards, values_list, dones)

        # 重新计算 log_prob 以构建计算图
        dist = self.actor(states)
        new_log_probs = dist.log_prob(torch.tensor(actions))
        entropy = dist.entropy().mean()

        # Actor 损失
        actor_loss = -(new_log_probs * advantages.detach()).mean()

        # Critic 损失
        values = self.critic(states).squeeze()
        critic_loss = F.mse_loss(values, returns)

        # 总损失
        total_loss = actor_loss + self.value_coef * critic_loss - self.entropy_coef * entropy

        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            max_norm=self.max_grad_norm,
        )
        self.optimizer.step()

        return {
            "total_loss": float(total_loss.item()),
            "actor_loss": float(actor_loss.item()),
            "critic_loss": float(critic_loss.item()),
            "entropy": float(entropy.item()),
        }


# ============================================================
# §5  环境: Acrobot 风格（简单连续任务）
# ============================================================

class SimpleEnv:
    """简单的倒立摆风格环境 — 离散动作。"""

    def __init__(self) -> None:
        self.max_steps = 200
        self.steps = 0
        self.state: np.ndarray | None = None

    def reset(self) -> np.ndarray:
        self.steps = 0
        # [angle, angular_velocity]
        self.state = np.array([np.pi + np.random.uniform(-0.1, 0.1),
                               np.random.uniform(-0.1, 0.1)])
        return self.state.copy()

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        theta, theta_dot = self.state  # type: ignore[misc]

        # 动力学
        g = 10.0
        m = 1.0
        l = 1.0
        dt = 0.05
        max_torque = 2.0

        torque = max_torque if action == 1 else -max_torque
        theta_ddot = (g / l * np.sin(theta) + torque / (m * l**2))
        # 加点噪声
        theta_ddot += np.random.normal(0, 0.01)

        theta_dot = theta_dot + theta_ddot * dt
        theta = theta + theta_dot * dt

        self.state = np.array([theta, theta_dot])
        self.steps += 1

        # 目标是保持直立 (theta = 0, 越近越好)
        # 把角度归一化到 [-pi, pi]
        theta_normalized = ((theta + np.pi) % (2 * np.pi)) - np.pi
        upright_reward = np.cos(theta_normalized)  # 1 为完美直立
        done = self.steps >= self.max_steps

        return self.state.copy(), float(upright_reward), done


# ============================================================
# §6  训练演示
# ============================================================

def collect_trajectory(env: SimpleEnv, agent: Any,
                       max_steps: int = 200) -> Trajectory:
    """收集一条完整的轨迹 (episode)。"""
    states: list[np.ndarray] = []
    actions: list[int] = []
    rewards: list[float] = []
    log_probs: list[torch.Tensor] = []
    dones: list[bool] = []

    state = env.reset()
    done = False
    step = 0

    while not done:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action, log_prob = agent.get_action(state_tensor)
        next_state, reward, done = env.step(action)

        states.append(state)
        actions.append(action)
        rewards.append(reward)
        log_probs.append(log_prob)
        dones.append(done or step >= max_steps - 1)

        state = next_state
        step += 1

    return Trajectory(states, actions, rewards, log_probs, dones)


def demo_reinforce() -> None:
    print("=" * 60)
    print("REINFORCE 在倒立摆上的训练")
    print("=" * 60)

    env = SimpleEnv()
    policy = DiscretePolicy(state_dim=2, action_dim=2, hidden_dim=64)
    agent = REINFORCE(policy, lr=1e-3, gamma=0.99)

    n_episodes = 300
    episode_rewards: list[float] = []

    for ep in range(n_episodes):
        traj = collect_trajectory(env, agent, max_steps=200)

        states_tensor = torch.FloatTensor(np.array(traj.states))
        loss = agent.update(states_tensor, traj.actions,
                            traj.rewards, traj.log_probs, traj.dones)

        total_reward = sum(traj.rewards)
        episode_rewards.append(total_reward)

        if (ep + 1) % 50 == 0:
            avg_r = np.mean(episode_rewards[-50:])
            print(f"Episode {ep+1:4d} | reward: {total_reward:6.1f} | "
                  f"avg50: {avg_r:6.1f} | loss: {loss:.4f}")

    print(f"\n最终 50 episode 平均奖励: {np.mean(episode_rewards[-50:]):.1f}")


def demo_a2c() -> None:
    print("\n" + "=" * 60)
    print("A2C 在倒立摆上的训练")
    print("=" * 60)

    env = SimpleEnv()
    a2c = A2C(
        state_dim=2, action_dim=2, hidden_dim=64,
        lr=3e-4, gamma=0.99, gae_lambda=0.95,
        entropy_coef=0.01, value_coef=0.5,
        n_steps=5,
    )

    n_episodes = 300
    episode_rewards: list[float] = []

    for ep in range(n_episodes):
        traj = collect_trajectory(env, a2c, max_steps=200)

        states_tensor = torch.FloatTensor(np.array(traj.states))
        info = a2c.update(states_tensor, traj.actions,
                          traj.rewards, traj.log_probs, traj.dones)

        total_reward = sum(traj.rewards)
        episode_rewards.append(total_reward)

        if (ep + 1) % 50 == 0:
            avg_r = np.mean(episode_rewards[-50:])
            print(f"Episode {ep+1:4d} | reward: {total_reward:6.1f} | "
                  f"avg50: {avg_r:6.1f} | "
                  f"actor: {info['actor_loss']:.3f} | "
                  f"critic: {info['critic_loss']:.3f}")

    print(f"\n最终 50 episode 平均奖励: {np.mean(episode_rewards[-50:]):.1f}")


def demo_continuous_policy() -> None:
    """连续动作空间的策略梯度演示。"""
    print("\n" + "=" * 60)
    print("连续动作空间策略梯度演示")
    print("=" * 60)

    state_dim, action_dim = 3, 2
    policy = ContinuousPolicy(state_dim, action_dim, hidden_dim=64)

    # 随机输入
    x = torch.randn(5, state_dim)
    action, log_prob = policy.get_action(x)
    print(f"输入 {x.shape} -> 动作 {action.shape}")
    print(f"动作示例:\n{action[:3]}")
    print(f"log_prob 示例: {log_prob[:3]}")
    print(f"动作范围: [{action.min().item():.3f}, {action.max().item():.3f}]")


if __name__ == "__main__":
    demo_reinforce()
    demo_a2c()
    demo_continuous_policy()
    print("\n✅ 策略梯度篇全部执行完毕!")
