"""Reinforcement Learning algorithms from scratch."""
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from collections import deque, namedtuple
import random


Experience = namedtuple("Experience", ["state", "action", "reward", "next_state", "done"])

class ReplayBuffer:
    def __init__(self, capacity: int = 100000):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.position = 0
    def push(self, *args): self.buffer.append(Experience(*args))
    def sample(self, batch_size: int) -> List[Experience]:
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    def __len__(self): return len(self.buffer)

class PrioritizedReplayBuffer:
    def __init__(self, capacity: int = 100000, alpha: float = 0.6, beta: float = 0.4):
        self.capacity = capacity; self.alpha = alpha; self.beta = beta
        self.buffer = []; self.priorities = np.zeros(capacity, dtype=np.float32)
        self.position = 0; self.max_priority = 1.0
    def push(self, *args):
        if len(self.buffer) < self.capacity: self.buffer.append(Experience(*args))
        else: self.buffer[self.position] = Experience(*args)
        self.priorities[self.position] = self.max_priority
        self.position = (self.position + 1) % self.capacity
    def sample(self, batch_size: int):
        probs = self.priorities[:len(self.buffer)] ** self.alpha
        probs /= probs.sum()
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        weights = (len(self.buffer) * probs[indices]) ** -self.beta
        weights /= weights.max()
        return [self.buffer[i] for i in indices], indices, weights
    def update_priorities(self, indices, priorities):
        for idx, prio in zip(indices, priorities):
            self.priorities[idx] = prio
            self.max_priority = max(self.max_priority, prio)

class BaseAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99):
        self.state_dim = state_dim; self.action_dim = action_dim
        self.lr = lr; self.gamma = gamma
    def select_action(self, state, epsilon=0.0): raise NotImplementedError
    def update(self, batch): raise NotImplementedError
    def save(self, path): pass
    def load(self, path): pass

class DQNAgent(BaseAgent):
    """Deep Q-Network agent."""
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], lr=1e-3, gamma=0.99,
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995,
                 target_update_freq=100, double_dqn=True, dueling=True):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.epsilon = epsilon_start; self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay; self.target_update_freq = target_update_freq
        self.double_dqn = double_dqn; self.dueling = dueling
        self.q_network = self._build_network(hidden_dims)
        self.target_network = self._build_network(hidden_dims)
        self.target_network.update_from(self.q_network)
        self.update_count = 0
    def _build_network(self, hidden_dims): return None  # Network building stub
    def select_action(self, state, epsilon=None):
        eps = epsilon if epsilon is not None else self.epsilon
        if np.random.random() < eps: return np.random.randint(self.action_dim)
        q_values = self.q_network.forward(state)
        return np.argmax(q_values)
    def update(self, batch):
        self.update_count += 1
        if self.update_count % self.target_update_freq == 0:
            self.target_network.update_from(self.q_network)
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

class PolicyGradientAgent(BaseAgent):
    """REINFORCE / Vanilla Policy Gradient."""
    def __init__(self, state_dim, action_dim, hidden_dims=[128, 128], lr=1e-3, gamma=0.99,
                 entropy_coef=0.01, baseline=True):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.entropy_coef = entropy_coef; self.baseline = baseline
        self.policy_network = None  # Build later
        self.value_network = None if not baseline else None
        self.episode_states, self.episode_actions, self.episode_rewards = [], [], []
    def select_action(self, state, epsilon=0.0):
        logits = self.policy_network(state)
        probs = np.exp(logits - logits.max()) / np.exp(logits - logits.max()).sum()
        return np.random.choice(self.action_dim, p=probs)
    def update(self, batch): pass

class A2CAgent(BaseAgent):
    """Advantage Actor-Critic (A2C)."""
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], lr=3e-4, gamma=0.99,
                 gae_lambda=0.95, value_coef=0.5, entropy_coef=0.01, max_grad_norm=0.5):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.gae_lambda = gae_lambda; self.value_coef = value_coef
        self.entropy_coef = entropy_coef; self.max_grad_norm = max_grad_norm
        self.actor = None  # policy network
        self.critic = None  # value network
    def select_action(self, state, deterministic=False): pass
    def compute_gae(self, rewards, values, dones):
        advantages = np.zeros_like(rewards)
        gae = 0
        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * (1 - dones[t]) * (values[t+1] if t+1 < len(values) else 0) - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages[t] = gae
        return advantages

class PPOAgent(BaseAgent):
    """Proximal Policy Optimization."""
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], lr=3e-4, gamma=0.99,
                 epsilon_clip=0.2, value_coef=0.5, entropy_coef=0.01, n_epochs=10,
                 batch_size=64, gae_lambda=0.95, max_grad_norm=0.5):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.epsilon_clip = epsilon_clip; self.value_coef = value_coef
        self.entropy_coef = entropy_coef; self.n_epochs = n_epochs
        self.batch_size = batch_size; self.gae_lambda = gae_lambda
        self.max_grad_norm = max_grad_norm
        self.actor = None; self.critic = None
        self.memory = []
    def select_action(self, state, deterministic=False): pass
    def update(self):
        if len(self.memory) < self.batch_size: return
        # PPO update logic
        pass

class SACAgent(BaseAgent):
    """Soft Actor-Critic."""
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], lr=3e-4, gamma=0.99,
                 tau=0.005, alpha=0.2, automatic_alpha_tuning=True):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.tau = tau; self.alpha = alpha
        self.automatic_alpha_tuning = automatic_alpha_tuning
        self.actor = None; self.critic1 = None; self.critic2 = None
        self.critic1_target = None; self.critic2_target = None
        self.target_entropy = -action_dim
    def select_action(self, state, deterministic=False):
        mean, log_std = self.actor(state)
        if deterministic: return np.tanh(mean)
        std = np.exp(log_std)
        z = mean + std * np.random.randn(*mean.shape)
        return np.tanh(z)
    def update(self, batch): pass

class TD3Agent(BaseAgent):
    """Twin Delayed DDPG."""
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], lr=3e-4, gamma=0.99,
                 tau=0.005, policy_noise=0.2, noise_clip=0.5, policy_update_freq=2):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.tau = tau; self.policy_noise = policy_noise
        self.noise_clip = noise_clip; self.policy_update_freq = policy_update_freq
        self.actor = None; self.actor_target = None
        self.critic1 = None; self.critic1_target = None
        self.critic2 = None; self.critic2_target = None
        self.update_count = 0
    def select_action(self, state, add_noise=False): pass
    def update(self, batch):
        if self.update_count % self.policy_update_freq == 0:
            pass  # Delayed policy update

class DDPGAgent(BaseAgent):
    """Deep Deterministic Policy Gradient."""
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], lr=1e-4, gamma=0.99,
                 tau=0.001, action_noise_std=0.1):
        super().__init__(state_dim, action_dim, lr, gamma)
        self.tau = tau; self.action_noise_std = action_noise_std
        self.actor = None; self.actor_target = None
        self.critic = None; self.critic_target = None
    def select_action(self, state, add_noise=True): pass
    def update(self, batch): pass

class NoisyLinear:
    """Noisy linear layer for exploration."""
    def __init__(self, in_features, out_features, sigma_init=0.5):
        self.in_features = in_features; self.out_features = out_features
        self.sigma_init = sigma_init
        self.weight_mu = None; self.weight_sigma = None
        self.bias_mu = None; self.bias_sigma = None
    def forward(self, x): return x  # Stub

class CategoricalDQN:
    """C51 / Categorical DQN with distributional RL."""
    def __init__(self, state_dim, action_dim, num_atoms=51, v_min=-10, v_max=10):
        self.num_atoms = num_atoms; self.v_min = v_min; self.v_max = v_max
        self.support = np.linspace(v_min, v_max, num_atoms)
        self.delta_z = (v_max - v_min) / (num_atoms - 1)
    def project_distribution(self, next_dist, rewards, dones):
        batch_size = len(rewards)
        Tz = rewards[:, None] + (1 - dones[:, None]) * self.support[None, :]
        Tz = np.clip(Tz, self.v_min, self.v_max)
        b = (Tz - self.v_min) / self.delta_z
        l, u = np.floor(b).astype(np.int64), np.ceil(b).astype(np.int64)
        return np.zeros((batch_size, self.num_atoms))  # Simplified

class MADDPGAgent:
    """Multi-Agent Deep Deterministic Policy Gradient."""
    def __init__(self, n_agents, state_dims, action_dims):
        self.n_agents = n_agents; self.state_dims = state_dims
        self.action_dims = action_dims
        self.agents = [DDPGAgent(sd, ad) for sd, ad in zip(state_dims, action_dims)]

class QMIXAgent:
    """QMIX: Monotonic Value Function Factorisation."""
    def __init__(self, n_agents, state_dim, action_dim):
        self.n_agents = n_agents; self.state_dim = state_dim
        self.action_dim = action_dim
        self.mixing_network = None  # Hypernetwork architecture
        self.agent_q_networks = [None] * n_agents

class MCTSNode:
    """Monte Carlo Tree Search node."""
    def __init__(self, state, parent=None, action=None, prior=0.0):
        self.state = state; self.parent = parent; self.action = action
        self.prior = prior; self.children = {}; self.visit_count = 0
        self.total_value = 0.0; self.mean_value = 0.0
    def is_leaf(self): return len(self.children) == 0
    def expand(self, action_probs):
        for action, prob in action_probs.items():
            self.children[action] = MCTSNode(None, self, action, prob)
    def select_child(self, c_puct=1.0):
        best_score = -float("inf"); best_child = None
        for child in self.children.values():
            score = child.mean_value + c_puct * child.prior * np.sqrt(self.visit_count) / (1 + child.visit_count)
            if score > best_score: best_score, best_child = score, child
        return best_child

class EnvWrapper:
    """Base environment wrapper."""
    def __init__(self, env): self.env = env
    def reset(self): return self.env.reset()
    def step(self, action): return self.env.step(action)
    @property
    def observation_space(self): return self.env.observation_space
    @property
    def action_space(self): return self.env.action_space

class FrameStackWrapper(EnvWrapper):
    """FrameStack environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class FrameSkipWrapper(EnvWrapper):
    """FrameSkip environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class ResizeObsWrapper(EnvWrapper):
    """ResizeObs environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class NormalizeObsWrapper(EnvWrapper):
    """NormalizeObs environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class RewardClipWrapper(EnvWrapper):
    """RewardClip environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class TimeLimitWrapper(EnvWrapper):
    """TimeLimit environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class ActionRepeatWrapper(EnvWrapper):
    """ActionRepeat environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class RandomStartWrapper(EnvWrapper):
    """RandomStart environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class DelayedRewardWrapper(EnvWrapper):
    """DelayedReward environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class StickyActionsWrapper(EnvWrapper):
    """StickyActions environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class NoopResetWrapper(EnvWrapper):
    """NoopReset environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class FireResetWrapper(EnvWrapper):
    """FireReset environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class EpisodicLifeWrapper(EnvWrapper):
    """EpisodicLife environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class MaxAndSkipWrapper(EnvWrapper):
    """MaxAndSkip environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class ClipRewardWrapper(EnvWrapper):
    """ClipReward environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class WarpFrameWrapper(EnvWrapper):
    """WarpFrame environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class ScaleRewardWrapper(EnvWrapper):
    """ScaleReward environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class GrayscaleObsWrapper(EnvWrapper):
    """GrayscaleObs environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class ChannelFirstWrapper(EnvWrapper):
    """ChannelFirst environment wrapper."""
    def __init__(self, env, **kwargs):
        super().__init__(env); self.kwargs = kwargs
    def reset(self): return super().reset()
    def step(self, action): return super().step(action)

class CartPoleEnv:
    """Classic cart-pole balancing environment.
    State dim: 4, Action dim: 2
    """
    def __init__(self):
        self.observation_space = (4,)
        self.action_space = (2,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(4, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(4).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class MountainCarEnv:
    """Mountain car under-powered climb environment.
    State dim: 2, Action dim: 3
    """
    def __init__(self):
        self.observation_space = (2,)
        self.action_space = (3,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(2, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(2).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class AcrobotEnv:
    """Acrobot swing-up environment.
    State dim: 6, Action dim: 3
    """
    def __init__(self):
        self.observation_space = (6,)
        self.action_space = (3,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(6, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(6).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class PendulumEnv:
    """Inverted pendulum swing-up environment.
    State dim: 3, Action dim: 1
    """
    def __init__(self):
        self.observation_space = (3,)
        self.action_space = (1,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(3, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(3).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class LunarLanderEnv:
    """Lunar lander discrete environment.
    State dim: 8, Action dim: 4
    """
    def __init__(self):
        self.observation_space = (8,)
        self.action_space = (4,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(8, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(8).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class BipedalWalkerEnv:
    """Bipedal walker continuous environment.
    State dim: 24, Action dim: 4
    """
    def __init__(self):
        self.observation_space = (24,)
        self.action_space = (4,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(24, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(24).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class GridWorldEnv:
    """Simple grid world navigation environment.
    State dim: 2, Action dim: 4
    """
    def __init__(self):
        self.observation_space = (2,)
        self.action_space = (4,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(2, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(2).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class TicTacToeEnv:
    """Tic-tac-toe environment.
    State dim: 9, Action dim: 9
    """
    def __init__(self):
        self.observation_space = (9,)
        self.action_space = (9,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(9, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(9).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class Connect4Env:
    """Connect four environment.
    State dim: 42, Action dim: 7
    """
    def __init__(self):
        self.observation_space = (42,)
        self.action_space = (7,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(42, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(42).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class ChessEnvEnv:
    """Chess environment stub environment.
    State dim: 64, Action dim: 4096
    """
    def __init__(self):
        self.observation_space = (64,)
        self.action_space = (4096,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(64, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(64).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class GoEnvEnv:
    """Go environment stub environment.
    State dim: 361, Action dim: 362
    """
    def __init__(self):
        self.observation_space = (361,)
        self.action_space = (362,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(361, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(361).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class PokerEnvEnv:
    """Simplified poker environment.
    State dim: 5, Action dim: 5
    """
    def __init__(self):
        self.observation_space = (5,)
        self.action_space = (5,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(5, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(5).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class BlackjackEnv:
    """Blackjack environment.
    State dim: 3, Action dim: 2
    """
    def __init__(self):
        self.observation_space = (3,)
        self.action_space = (2,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(3, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(3).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class CliffWalkingEnv:
    """Cliff walking environment.
    State dim: 48, Action dim: 4
    """
    def __init__(self):
        self.observation_space = (48,)
        self.action_space = (4,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(48, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(48).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class FrozenLakeEnv:
    """Frozen lake environment.
    State dim: 16, Action dim: 4
    """
    def __init__(self):
        self.observation_space = (16,)
        self.action_space = (4,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(16, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(16).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class TaxiEnv:
    """Taxi problem environment.
    State dim: 500, Action dim: 6
    """
    def __init__(self):
        self.observation_space = (500,)
        self.action_space = (6,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(500, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(500).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class BanditEnvEnv:
    """Multi-armed bandit environment.
    State dim: 1, Action dim: 10
    """
    def __init__(self):
        self.observation_space = (1,)
        self.action_space = (10,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(1, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(1).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class InventoryEnvEnv:
    """Inventory management environment.
    State dim: 10, Action dim: 5
    """
    def __init__(self):
        self.observation_space = (10,)
        self.action_space = (5,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(10, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(10).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class PortfolioEnvEnv:
    """Portfolio optimization environment.
    State dim: 20, Action dim: 10
    """
    def __init__(self):
        self.observation_space = (20,)
        self.action_space = (10,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(20, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(20).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

class TrafficEnvEnv:
    """Traffic light control environment.
    State dim: 100, Action dim: 4
    """
    def __init__(self):
        self.observation_space = (100,)
        self.action_space = (4,)
        self.state = None; self.done = False
    def reset(self):
        self.state = np.zeros(100, dtype=np.float32)
        self.done = False
        return self.state
    def step(self, action):
        reward = 0.0; self.done = np.random.random() < 0.02
        self.state = np.random.randn(100).astype(np.float32) * 0.1
        return self.state, reward, self.done, {}
    def render(self, mode="human"): pass
    def close(self): pass
    def seed(self, seed=None): np.random.seed(seed)

