import torch
import torch.optim as optim
import numpy as np
from model import DQN

class DQNAgent:
    def __init__(self, env, device):
        self.device = device
        self.n_actions = env.action_space.n
        self.obs_shape = env.observation_space.shape

        self.q_net = DQN(self.obs_shape, self.n_actions).to(device)
        self.target_net = DQN(self.obs_shape, self.n_actions).to(device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.optimizer = optim.RMSprop(self.q_net.parameters(), lr=0.00025, alpha=0.95, eps=0.01)

        self.epsilon = 1.0
        self.epsilon_final = 0.1
        self.epsilon_decay = 1_000_000
        self.total_steps = 0
        self.gamma = 0.99

    def act(self, obs):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        obs_t = torch.tensor(obs, dtype=torch.uint8, device=self.device).unsqueeze(0)
        q_vals = self.q_net(obs_t)
        return q_vals.max(1)[1].item()

    def update_target_net(self):
        self.target_net.load_state_dict(self.q_net.state_dict())

    def train_step(self, batch):
        states, actions, rewards, next_states, dones = batch
        states = torch.tensor(states, dtype=torch.uint8, device=self.device)
        next_states = torch.tensor(next_states, dtype=torch.uint8, device=self.device)
        actions = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        dones = torch.tensor(dones, dtype=torch.bool, device=self.device)

        current_q = self.q_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        next_q = self.target_net(next_states).max(1)[0].detach()
        next_q[dones] = 0.0
        target_q = rewards + self.gamma * next_q

        loss = torch.nn.functional.mse_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_net.parameters(), 10)
        self.optimizer.step()

        # Epsilon decay
        if self.epsilon > self.epsilon_final:
            self.epsilon -= (1.0 - self.epsilon_final) / self.epsilon_decay
        self.total_steps += 1
        return loss.item()
