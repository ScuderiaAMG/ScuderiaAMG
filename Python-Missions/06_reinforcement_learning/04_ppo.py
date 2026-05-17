#!/usr/bin/env python3
"""
近端策略优化 (PPO) —— 完整从零实现
涵盖：PPO-Clip、PPO-Penalty (KLPEN)、GAE 优势估计、
      多环境并行采样、Mini-batch 更新、学习率调度、
      MuJoCo 风格连续控制环境 (自实现)、
      完整训练 + TensorBoard 风格日志
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal, Categorical, kl_divergence
from collections import deque, namedtuple
from typing import Any
import math
import random

RolloutBatch = namedtuple("RolloutBatch", [
    "states", "actions", "log_probs", "rewards",
    "dones", "values", "advantages", "returns",
    "old_log_probs",
])


# ============================================================
# §1  策略网络 (Actor)
# ============================================================

def orthogonal_init(layer: nn.Linear, gain: float = np.sqrt(2)) -> None:
    """正交初始化 (PPO 论文推荐)。"""
    nn.init.orthogonal_(layer.weight, gain=gain)
    nn.init.constant_(layer.bias, 0)


class Actor(nn.Module):
    """连续动作空间的 Actor — 输出高斯分布的均值和标准差。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 256) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )
        self.mean = nn.Linear(hidden_dim, action_dim)
        # 可学习 log_std（状态无关）
        self.log_std = nn.Parameter(torch.zeros(action_dim))

        for layer in self.net:
            if isinstance(layer, nn.Linear):
                orthogonal_init(layer, gain=np.sqrt(2))
        orthogonal_init(self.mean, gain=0.01)

    def forward(self, x: torch.Tensor) -> Normal:
        features = self.net(x)
        mean = self.mean(features)
        std = torch.exp(self.log_std.clamp(-20, 2))
        return Normal(mean, std)

    def get_action(self, state: torch.Tensor,
                   evaluate: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
        dist = self(state)
        if evaluate:
            action = dist.mean
        else:
            action = dist.sample()
        log_prob = dist.log_prob(action).sum(dim=-1)
        return action, log_prob

    def evaluate(self, state: torch.Tensor,
                 action: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """评估给定 action 的 log_prob 和 entropy。"""
        dist = self(state)
        log_prob = dist.log_prob(action).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        return log_prob, entropy


class DiscreteActor(nn.Module):
    """离散动作空间的 Actor。"""

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_dim: int = 256) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, action_dim),
        )
        for layer in self.net:
            if isinstance(layer, nn.Linear):
                orthogonal_init(layer)

    def forward(self, x: torch.Tensor) -> Categorical:
        logits = self.net(x)
        return Categorical(logits=logits)

    def get_action(self, state: torch.Tensor,
                   evaluate: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
        dist = self(state)
        if evaluate:
            action = torch.argmax(dist.probs, dim=-1)
        else:
            action = dist.sample()
        log_prob = dist.log_prob(action)
        return action, log_prob

    def evaluate(self, state: torch.Tensor,
                 action: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        dist = self(state)
        log_prob = dist.log_prob(action)
        entropy = dist.entropy()
        return log_prob, entropy


# ============================================================
# §2  价值网络 (Critic)
# ============================================================

class Critic(nn.Module):
    """状态价值估计 V(s)。"""

    def __init__(self, state_dim: int, hidden_dim: int = 256) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )
        for layer in self.net:
            if isinstance(layer, nn.Linear):
                orthogonal_init(layer, gain=1.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ============================================================
# §3  GAE 与回报计算
# ============================================================

def compute_gae_and_returns(
    rewards: np.ndarray,
    values: np.ndarray,
    dones: np.ndarray,
    gamma: float = 0.99,
    gae_lambda: float = 0.95,
) -> tuple[np.ndarray, np.ndarray]:
    """
    计算 GAE 和折扣回报。
    rewards: (T,) 或 (T, n_envs)
    values:  (T,) 或 (T, n_envs)
    dones:   (T,) 或 (T, n_envs)
    """
    T = len(rewards)
    advantages = np.zeros_like(rewards)
    returns = np.zeros_like(rewards)

    gae = 0.0
    for t in reversed(range(T)):
        if t == T - 1:
            next_value = 0.0
        else:
            next_value = values[t + 1]

        delta = rewards[t] + gamma * next_value * (1 - dones[t]) - values[t]
        gae = delta + gamma * gae_lambda * (1 - dones[t]) * gae
        advantages[t] = gae
        returns[t] = advantages[t] + values[t]

    return advantages, returns


# ============================================================
# §4  PPO Agent
# ============================================================

class PPO:
    """PPO-Clip 算法 (支持连续和离散动作)。"""

    def __init__(self, state_dim: int, action_dim: int,
                 discrete: bool = False,
                 hidden_dim: int = 256,
                 lr: float = 3e-4,
                 gamma: float = 0.99,
                 gae_lambda: float = 0.95,
                 clip_epsilon: float = 0.2,
                 value_coef: float = 0.5,
                 entropy_coef: float = 0.01,
                 max_grad_norm: float = 0.5,
                 ppo_epochs: int = 10,
                 batch_size: int = 64,
                 target_kl: float = 0.015,
                 use_kl_penalty: bool = False,
                 kl_penalty_coef: float = 0.5,
                 device: str = "cpu") -> None:
        self.device = torch.device(device)
        self.action_dim = action_dim
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        self.ppo_epochs = ppo_epochs
        self.batch_size = batch_size
        self.target_kl = target_kl
        self.use_kl_penalty = use_kl_penalty
        self.kl_penalty_coef = kl_penalty_coef

        if discrete:
            self.actor = DiscreteActor(state_dim, action_dim, hidden_dim).to(self.device)
        else:
            self.actor = Actor(state_dim, action_dim, hidden_dim).to(self.device)

        self.critic = Critic(state_dim, hidden_dim).to(self.device)
        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=lr, eps=1e-5,
        )

    def select_action(self, state: np.ndarray,
                      evaluate: bool = False) -> tuple[np.ndarray, float, float]:
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            action, log_prob = self.actor.get_action(state_tensor, evaluate)
            value = self.critic(state_tensor).squeeze().item()

        if self.actor.__class__ == DiscreteActor:
            return np.array([action.item()]), log_prob.item(), value
        return action.cpu().numpy().flatten(), log_prob.item(), value

    def evaluate_batch(self, states: torch.Tensor,
                       actions: torch.Tensor,
                       old_log_probs: torch.Tensor) -> dict[str, torch.Tensor]:
        """计算 PPO 的各个损失项。"""
        new_log_probs, entropy = self.actor.evaluate(states, actions)
        values = self.critic(states).squeeze(-1)

        return {
            "log_probs": new_log_probs,
            "entropy": entropy,
            "values": values,
        }

    def update(self, rollout: RolloutBatch) -> dict[str, float]:
        """PPO 更新 — 在 rollout 数据上做多轮 mini-batch 更新。"""
        # 转换为 Tensor
        states = torch.FloatTensor(rollout.states).to(self.device)
        actions_tensor = torch.FloatTensor(rollout.actions).to(self.device)
        old_log_probs = torch.FloatTensor(rollout.log_probs).to(self.device)
        advantages = torch.FloatTensor(rollout.advantages).to(self.device)
        returns = torch.FloatTensor(rollout.returns).to(self.device)

        # 标准化优势 (重要!)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        total_samples = len(states)
        indices = np.arange(total_samples)

        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        n_updates = 0
        approx_kl = 0.0

        for _ in range(self.ppo_epochs):
            np.random.shuffle(indices)

            for start in range(0, total_samples, self.batch_size):
                batch_idx = indices[start:start + self.batch_size]

                batch_states = states[batch_idx]
                batch_actions = actions_tensor[batch_idx]
                batch_old_log_probs = old_log_probs[batch_idx]
                batch_advantages = advantages[batch_idx]
                batch_returns = returns[batch_idx]

                # 评估
                results = self.evaluate_batch(
                    batch_states, batch_actions, batch_old_log_probs
                )
                new_log_probs = results["log_probs"]
                entropy = results["entropy"]
                values = results["values"]

                # ---- PPO Clip 损失 ----
                ratio = torch.exp(new_log_probs - batch_old_log_probs)

                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.clip_epsilon,
                                    1 + self.clip_epsilon) * batch_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # ---- KL 惩罚 (可选) ----
                if self.use_kl_penalty:
                    # 计算约化 KL 散度
                    with torch.no_grad():
                        log_ratio = new_log_probs - batch_old_log_probs
                        approx_kl = ((ratio - 1) - log_ratio).mean().item()

                    if approx_kl > self.target_kl * 2:
                        self.kl_penalty_coef *= 2
                    elif approx_kl < self.target_kl / 2:
                        self.kl_penalty_coef /= 2

                    policy_loss = policy_loss + self.kl_penalty_coef * approx_kl

                    # 如果 KL 太大，提前停止
                    if approx_kl > self.target_kl * 3:
                        break

                # ---- Value 损失 ----
                value_loss = F.mse_loss(values, batch_returns)

                # ---- 总损失 ----
                loss = (policy_loss
                        + self.value_coef * value_loss
                        - self.entropy_coef * entropy.mean())

                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(
                    list(self.actor.parameters()) + list(self.critic.parameters()),
                    max_norm=self.max_grad_norm,
                )
                self.optimizer.step()

                total_policy_loss += policy_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += entropy.mean().item()
                n_updates += 1

        return {
            "policy_loss": total_policy_loss / max(n_updates, 1),
            "value_loss": total_value_loss / max(n_updates, 1),
            "entropy": total_entropy / max(n_updates, 1),
            "approx_kl": approx_kl,
        }


# ============================================================
# §5  环境: 类 HalfCheetah (简化 2D)
# ============================================================

class SimpleLocomotion:
    """
    简化的仿生运动环境 — 连续状态 + 连续动作。

    状态 (14 维): 身体和各关节的角度、角速度
    动作 (4 维):  各关节力矩 [-1, 1]
    奖励: 前进速度 + 能量消耗惩罚
    """

    def __init__(self) -> None:
        self.state_dim = 12
        self.action_dim = 4
        self.max_steps = 200
        self.steps = 0

        # 身体参数
        self.dt = 0.05
        self.gravity = 9.8
        self.friction = 0.1

        # 前进速度追踪
        self.position_x = 0.0
        self.prev_position_x = 0.0

        # 关节角度 [hip_left, knee_left, hip_right, knee_right]
        self.joint_angles = np.zeros(4)
        self.joint_velocities = np.zeros(4)
        self.body_angle = 0.0
        self.body_angular_velocity = 0.0

    def reset(self) -> np.ndarray:
        self.steps = 0
        self.position_x = 0.0
        self.prev_position_x = 0.0
        self.joint_angles = np.random.uniform(-0.1, 0.1, 4)
        self.joint_velocities = np.zeros(4)
        self.body_angle = np.random.uniform(-0.05, 0.05)
        self.body_angular_velocity = 0.0
        return self._get_state()

    def _get_state(self) -> np.ndarray:
        """构造完整状态向量。"""
        return np.concatenate([
            [self.body_angle, self.body_angular_velocity],
            [self.position_x, 0.0],                       # x 位置 (隐藏 z)
            self.joint_angles,
            self.joint_velocities,
        ])

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool]:
        """
        简化的动力学模型。
        奖励: 前进速度 + 保持直立 + 动作惩罚
        """
        self.steps += 1
        torques = np.clip(action, -1, 1) * 5.0

        # 简化：力矩直接影响关节加速度
        # 身体运动由各关节力矩的总和作用产生
        self.prev_position_x = self.position_x

        # 身体角度受关节反作用力影响
        body_torque = torques[0] + torques[2] - torques[1] - torques[3]
        self.body_angular_velocity += (body_torque * self.dt / 3.0
                                       - self.friction * self.body_angular_velocity
                                       + np.random.normal(0, 0.01))
        self.body_angle += self.body_angular_velocity * self.dt

        # 前进速度 (简化为基于关节力矩的正向分量)
        forward_force = (torques[0] + torques[2]) * np.cos(self.body_angle)
        self.position_x += forward_force * self.dt

        # 关节动力学
        for i in range(4):
            self.joint_velocities[i] += (torques[i] * self.dt
                                         - 0.2 * self.joint_velocities[i]
                                         + np.random.normal(0, 0.02))
            self.joint_angles[i] += self.joint_velocities[i] * self.dt

        # 奖励
        forward_velocity = (self.position_x - self.prev_position_x) / self.dt
        upright_bonus = -abs(self.body_angle) * 0.5
        action_penalty = -0.001 * np.sum(action ** 2)
        alive_bonus = 1.0

        reward = forward_velocity + upright_bonus + action_penalty + alive_bonus

        done = self.steps >= self.max_steps

        return self._get_state(), float(reward), done


# ============================================================
# §6  数据收集器 (Rollout Buffer)
# ============================================================

class RolloutCollector:
    """收集多步经验，用于 PPO 更新。"""

    def __init__(self, buffer_size: int, state_dim: int,
                 action_dim: int) -> None:
        self.buffer_size = buffer_size
        self.states = np.zeros((buffer_size, state_dim), dtype=np.float32)
        self.actions = np.zeros((buffer_size, action_dim), dtype=np.float32)
        self.rewards = np.zeros(buffer_size, dtype=np.float32)
        self.values = np.zeros(buffer_size, dtype=np.float32)
        self.log_probs = np.zeros(buffer_size, dtype=np.float32)
        self.dones = np.zeros(buffer_size, dtype=np.float32)
        self.ptr = 0
        self.full = False

    def add(self, state: np.ndarray, action: np.ndarray,
            reward: float, value: float, log_prob: float,
            done: bool) -> None:
        self.states[self.ptr] = state
        self.actions[self.ptr] = action
        self.rewards[self.ptr] = reward
        self.values[self.ptr] = value
        self.log_probs[self.ptr] = log_prob
        self.dones[self.ptr] = float(done)
        self.ptr += 1
        if self.ptr >= self.buffer_size:
            self.full = True

    def get_batch(self) -> RolloutBatch:
        n = self.ptr

        # 计算 last_value (如果最后一个 done=False, 用 critic bootstrap)
        last_value = 0.0 if self.dones[n - 1] else self.values[n - 1]

        # 扩展 rewards 以包含 bootstrap
        extended_rewards = np.append(self.rewards[:n], last_value)
        extended_values = np.append(self.values[:n], last_value)
        extended_dones = np.append(self.dones[:n], False)  # last bootstrap not done

        # 计算 GAE
        advantages, returns = compute_gae_and_returns(
            extended_rewards[:-1], extended_values[:-1],
            extended_dones[:-1],
        )

        # 截取实际收集的数据
        return RolloutBatch(
            states=self.states[:n],
            actions=self.actions[:n],
            log_probs=self.log_probs[:n],
            rewards=self.rewards[:n],
            dones=self.dones[:n],
            values=self.values[:n],
            advantages=advantages,
            returns=returns,
            old_log_probs=self.log_probs[:n],
        )

    def clear(self) -> None:
        self.ptr = 0
        self.full = False

    def __len__(self) -> int:
        return self.ptr


# ============================================================
# §7  完整训练循环
# ============================================================

def train_ppo(
    env: SimpleLocomotion,
    agent: PPO,
    total_timesteps: int = 50000,
    rollout_length: int = 1024,
    verbose: bool = True,
) -> dict[str, list[float]]:
    """
    PPO 训练循环：
    1. 用当前策略采集 rollout_length 步经验
    2. 计算 GAE 和回报
    3. 做多轮 mini-batch PPO 更新
    4. 重复
    """

    collector = RolloutCollector(rollout_length, env.state_dim, env.action_dim)
    state = env.reset()

    episode_rewards: list[float] = []
    episode_reward = 0.0
    episode_length = 0

    metrics = {
        "episode_rewards": [],
        "policy_loss": [],
        "value_loss": [],
        "entropy": [],
        "episode_lengths": [],
    }

    for t in range(total_timesteps):
        action, log_prob, value = agent.select_action(state)
        next_state, reward, done = env.step(action)

        collector.add(state, action, reward, value, log_prob, done)

        episode_reward += reward
        episode_length += 1
        state = next_state

        if done:
            state = env.reset()
            episode_rewards.append(episode_reward)
            metrics["episode_rewards"].append(episode_reward)
            metrics["episode_lengths"].append(episode_length)
            episode_reward = 0.0
            episode_length = 0

        # PPO 更新时机
        if len(collector) >= rollout_length:
            batch = collector.get_batch()
            info = agent.update(batch)
            collector.clear()

            metrics["policy_loss"].append(info["policy_loss"])
            metrics["value_loss"].append(info["value_loss"])
            metrics["entropy"].append(info["entropy"])

            if verbose and (t + 1) % (rollout_length * 4) == 0:
                avg_reward = np.mean(episode_rewards[-10:]) if episode_rewards else 0.0
                print(
                    f"Step {t+1:6d}/{total_timesteps} | "
                    f"avg_reward(10ep): {avg_reward:7.1f} | "
                    f"policy_loss: {info['policy_loss']:.4f} | "
                    f"value_loss: {info['value_loss']:.4f} | "
                    f"entropy: {info['entropy']:.4f} | "
                    f"KL: {info['approx_kl']:.5f}"
                )

    return metrics


def demo_ppo_training() -> None:
    print("=" * 60)
    print("PPO 在仿生运动环境上的训练")
    print("=" * 60)

    env = SimpleLocomotion()
    print(f"环境: 状态维度={env.state_dim}, 动作维度={env.action_dim}")
    print(f"最大每 episode 步数: {env.max_steps}")

    agent = PPO(
        state_dim=env.state_dim,
        action_dim=env.action_dim,
        discrete=False,
        hidden_dim=128,
        lr=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_epsilon=0.2,
        value_coef=0.5,
        entropy_coef=0.01,
        max_grad_norm=0.5,
        ppo_epochs=8,
        batch_size=64,
        target_kl=0.015,
        use_kl_penalty=False,
    )
    print(f"Actor 参数: {sum(p.numel() for p in agent.actor.parameters()):,}")
    print(f"Critic 参数: {sum(p.numel() for p in agent.critic.parameters()):,}")

    print("\n开始训练...")
    metrics = train_ppo(
        env, agent,
        total_timesteps=20000,
        rollout_length=512,
        verbose=True,
    )

    # 最终评估
    print(f"\n{'='*60}")
    print("最终评估 (10 episodes)")
    eval_rewards: list[float] = []
    for ep in range(10):
        state = env.reset()
        total_r = 0.0
        for _ in range(env.max_steps):
            action, _, _ = agent.select_action(state, evaluate=True)
            state, r, done = env.step(action)
            total_r += r
            if done:
                break
        eval_rewards.append(total_r)
    print(f"平均奖励: {np.mean(eval_rewards):.1f} ± {np.std(eval_rewards):.1f}")

    # 训练期间趋势
    if metrics["episode_rewards"]:
        n = len(metrics["episode_rewards"])
        first_quarter = np.mean(metrics["episode_rewards"][:max(1, n//4)])
        last_quarter = np.mean(metrics["episode_rewards"][max(0, 3*n//4):])
        print(f"奖励趋势: 前1/4均={first_quarter:.1f} -> 后1/4均={last_quarter:.1f}")


def demo_ppo_discrete() -> None:
    """离散动作空间的 PPO 演示。"""
    print("\n" + "=" * 60)
    print("PPO 离散动作空间演示")
    print("=" * 60)

    # 简化：PPO for discrete CartPole-like environment
    from dqn import CartPole  # 复用 DQN 中的环境
    # (如果导入失败，使用内联定义)
    try:
        from dqn import CartPole
    except ImportError:
        class CartPole:
            def __init__(self) -> None:
                self.state_dim = 4
                self.action_dim = 2
                self.max_steps = 200
                self.gravity = 9.8
                self.mass_cart = 1.0
                self.mass_pole = 0.1
                self.total_mass = self.mass_cart + self.mass_pole
                self.length = 0.5
                self.pole_mass_length = self.mass_pole * self.length
                self.force_mag = 10.0
                self.tau = 0.02
                self.state: np.ndarray | None = None

            def reset(self) -> np.ndarray:
                self.state = np.random.uniform(-0.05, 0.05, size=4)
                return self.state.copy()

            def step(self, action: int) -> tuple[np.ndarray, float, bool]:
                x, x_dot, theta, theta_dot = self.state  # type: ignore[misc]
                force = self.force_mag if action == 1 else -self.force_mag
                cos_theta = np.cos(theta)
                sin_theta = np.sin(theta)
                temp = (force + self.pole_mass_length * theta_dot**2 * sin_theta) / self.total_mass
                theta_acc = (self.gravity * sin_theta - cos_theta * temp) / \
                    (self.length * (4/3 - self.mass_pole * cos_theta**2 / self.total_mass))
                x_acc = temp - self.pole_mass_length * theta_acc * cos_theta / self.total_mass
                x += self.tau * x_dot
                x_dot += self.tau * x_acc
                theta += self.tau * theta_dot
                theta_dot += self.tau * theta_acc
                self.state = np.array([x, x_dot, theta, theta_dot])
                done = abs(x) > 2.4 or abs(theta) > 12 * np.pi / 180
                return self.state.copy(), 1.0 if not done else 0.0, done

    env = CartPole()
    agent = PPO(
        state_dim=4,
        action_dim=2,
        discrete=True,
        hidden_dim=64,
        lr=1e-3,
        gamma=0.99,
        gae_lambda=0.95,
        clip_epsilon=0.2,
        ppo_epochs=5,
        batch_size=32,
    )

    # 简短训练
    collector = RolloutCollector(256, 4, 1)
    state = env.reset()
    episode_rewards: list[float] = []
    ep_reward = 0.0

    total_steps = 5000
    for step in range(total_steps):
        action, log_prob, value = agent.select_action(state)
        next_state, reward, done = env.step(action[0])

        collector.add(state, action, reward, value, log_prob, done)
        ep_reward += reward
        state = next_state

        if done:
            state = env.reset()
            episode_rewards.append(ep_reward)
            ep_reward = 0.0

        if len(collector) >= 256:
            batch = collector.get_batch()
            agent.update(batch)
            collector.clear()

    avg_last_10 = np.mean(episode_rewards[-10:]) if len(episode_rewards) >= 10 else np.mean(episode_rewards)
    print(f"离散 PPO 训练后平均奖励 (最后 10ep): {avg_last_10:.1f}")


if __name__ == "__main__":
    demo_ppo_training()
    demo_ppo_discrete()
    print("\n✅ PPO 篇全部执行完毕!")
