#!/usr/bin/env python3
"""
蒙特卡洛树搜索 (MCTS) 与 AlphaZero 风格强化学习
涵盖：纯 MCTS (UCT 选择)、MCTS + 神经网络 (AlphaZero 简化版)、
      自对弈训练、连四棋 (Connect Four) 环境、
      完整的搜索 / 训练 / 评估流程
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Any
import math
import random
from collections import defaultdict, deque
import copy


# ============================================================
# §1  Connect Four 环境
# ============================================================

class Connect4:
    """连四棋 —— 6 行 × 7 列，先连成 4 子者胜。"""

    ROWS = 6
    COLS = 7
    WIN_LENGTH = 4

    def __init__(self) -> None:
        self.board = np.zeros((self.ROWS, self.COLS), dtype=np.int8)
        self.current_player = 1                     # 1 或 -1
        self.done = False
        self.winner: int = 0

    def clone(self) -> "Connect4":
        c = Connect4()
        c.board = self.board.copy()
        c.current_player = self.current_player
        c.done = self.done
        c.winner = self.winner
        return c

    def get_valid_moves(self) -> list[int]:
        if self.done:
            return []
        return [c for c in range(self.COLS) if self.board[0, c] == 0]

    def make_move(self, col: int) -> bool:
        if self.done or self.board[0, col] != 0:
            return False
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row, col] == 0:
                self.board[row, col] = self.current_player
                break
        self._check_winner()
        self.current_player = -self.current_player
        return True

    def _check_winner(self) -> None:
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.board[r, c] == 0:
                    continue
                player = self.board[r, c]
                # 右
                if (c + 3 < self.COLS and
                    all(self.board[r, c + i] == player for i in range(4))):
                    self.winner = player
                    self.done = True
                    return
                # 下
                if (r + 3 < self.ROWS and
                    all(self.board[r + i, c] == player for i in range(4))):
                    self.winner = player
                    self.done = True
                    return
                # 右下对角线
                if (r + 3 < self.ROWS and c + 3 < self.COLS and
                    all(self.board[r + i, c + i] == player for i in range(4))):
                    self.winner = player
                    self.done = True
                    return
                # 左下对角线
                if (r + 3 < self.ROWS and c - 3 >= 0 and
                    all(self.board[r + i, c - i] == player for i in range(4))):
                    self.winner = player
                    self.done = True
                    return

        if len(self.get_valid_moves()) == 0:
            self.done = True

    def get_result(self, player: int) -> float:
        """返回 player 视角的结果: 1 (胜), 0 (平), -1 (负)。"""
        if not self.done:
            return 0.0
        if self.winner == 0:
            return 0.0
        return 1.0 if self.winner == player else -1.0

    def get_state_tensor(self) -> np.ndarray:
        """返回 (3, ROWS, COLS) 的张量。"""
        state = np.zeros((3, self.ROWS, self.COLS), dtype=np.float32)
        state[0] = (self.board == self.current_player)
        state[1] = (self.board == -self.current_player)
        state[2] = self.current_player
        return state

    def __repr__(self) -> str:
        symbols = {1: "X", -1: "O", 0: "."}
        return "\n".join(
            " ".join(symbols[self.board[r, c]] for c in range(self.COLS))
            for r in range(self.ROWS)
        )


# ============================================================
# §2  纯 MCTS (无神经网络)
# ============================================================

class MCTSNode:
    """MCTS 节点。"""

    def __init__(self, env: Connect4, parent: "MCTSNode | None" = None,
                 action: int | None = None) -> None:
        self.env = env.clone()
        self.parent = parent
        self.action = action
        self.children: dict[int, MCTSNode] = {}
        self.visit_count: int = 0
        self.total_value: float = 0.0
        self.prior: float = 0.0                     # P(s,a)

    def is_expanded(self) -> bool:
        return len(self.children) > 0

    def value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.total_value / self.visit_count

    def ucb_score(self, child_action: int, c_puct: float = 1.414) -> float:
        """UCT = Q(s,a) + c * sqrt(log(N(s)) / N(s,a))。"""
        child = self.children[child_action]
        Q = child.value()
        U = c_puct * math.sqrt(
            math.log(max(1, self.visit_count)) / max(1, child.visit_count)
        )
        return Q + U


class PureMCTS:
    """纯 MCTS 搜索 (无神经网络)。"""

    def __init__(self, n_simulations: int = 200,
                 c_puct: float = 1.414) -> None:
        self.n_simulations = n_simulations
        self.c_puct = c_puct

    def search(self, env: Connect4) -> dict[int, float]:
        root = MCTSNode(env)

        for _ in range(self.n_simulations):
            node = root
            sim_env = env.clone()

            # 1) SELECT: 沿 UCT 下降到叶节点
            search_path = [node]
            while node.is_expanded() and not sim_env.done:
                valid_moves = sim_env.get_valid_moves()
                if not valid_moves:
                    break
                # 选择 UCB 最高的动作
                best_action = max(valid_moves,
                                  key=lambda a: node.ucb_score(a, self.c_puct)
                                  if a in node.children else float("inf"))
                node = node.children.get(best_action)
                if node is None:
                    node = MCTSNode(sim_env, search_path[-1], best_action)
                    search_path[-1].children[best_action] = node
                sim_env.make_move(best_action)
                search_path.append(node)

            # 2) EXPAND
            if not sim_env.done:
                valid_moves = sim_env.get_valid_moves()
                if valid_moves:
                    action = random.choice(valid_moves)
                    sim_env.make_move(action)
                    child = MCTSNode(sim_env, node, action)
                    node.children[action] = child
                    node = child

            # 3) SIMULATE (随机走子)
            while not sim_env.done:
                valid_moves = sim_env.get_valid_moves()
                if not valid_moves:
                    break
                action = random.choice(valid_moves)
                sim_env.make_move(action)

            # 4) BACKPROPAGATE
            result = sim_env.get_result(env.current_player)
            for n in search_path:
                n.visit_count += 1
                n.total_value += result
                result = -result                     # 对手视角

        # 返回动作概率 (按访问次数)
        total_visits = sum(c.visit_count for c in root.children.values())
        policy = {}
        for action, child in root.children.items():
            policy[action] = child.visit_count / max(total_visits, 1)
        return policy

    def select_action(self, env: Connect4,
                      temperature: float = 1.0) -> int:
        policy = self.search(env)
        valid_moves = env.get_valid_moves()
        if not valid_moves:
            return 0

        if temperature == 0:
            return max(policy, key=policy.get)

        # 玻尔兹曼采样
        actions = list(policy.keys())
        probs = np.array([policy[a] ** (1.0 / temperature) for a in actions])
        probs /= probs.sum()
        return np.random.choice(actions, p=probs)


# ============================================================
# §3  神经网络 (AlphaZero 风格)
# ============================================================

class ResBlock(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return F.relu(out + residual)


class AlphaZeroNet(nn.Module):
    """AlphaZero 风格双头网络 —— Policy + Value。"""

    def __init__(self, input_channels: int = 3,
                 num_actions: int = 7,
                 num_res_blocks: int = 6,
                 channels: int = 64) -> None:
        super().__init__()
        self.conv_input = nn.Sequential(
            nn.Conv2d(input_channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )
        self.res_blocks = nn.Sequential(*[
            ResBlock(channels) for _ in range(num_res_blocks)
        ])

        # Policy Head
        self.policy_conv = nn.Sequential(
            nn.Conv2d(channels, 32, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.policy_fc = nn.Linear(32 * 6 * 7, num_actions)

        # Value Head
        self.value_conv = nn.Sequential(
            nn.Conv2d(channels, 16, 1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(),
        )
        self.value_fc1 = nn.Linear(16 * 6 * 7, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        out = self.conv_input(x)
        out = self.res_blocks(out)

        # Policy
        pol = self.policy_conv(out).flatten(1)
        policy_logits = self.policy_fc(pol)

        # Value
        val = self.value_conv(out).flatten(1)
        val = F.relu(self.value_fc1(val))
        value = torch.tanh(self.value_fc2(val))

        return F.log_softmax(policy_logits, dim=1), value


# ============================================================
# §4  AlphaZero 简化版 MCTS
# ============================================================

class AlphaMCTSNode:
    """AlphaZero MCTS —— 使用神经网络指导搜索。"""

    def __init__(self, prior: float = 0.0) -> None:
        self.visit_count = 0
        self.total_value = 0.0
        self.prior = prior
        self.children: dict[int, AlphaMCTSNode] = {}

    def value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.total_value / self.visit_count


class AlphaMCTS:
    """AlphaZero MCTS 搜索。"""

    def __init__(self, network: AlphaZeroNet, n_simulations: int = 50,
                 c_puct: float = 1.0, device: str = "cpu") -> None:
        self.network = network
        self.n_simulations = n_simulations
        self.c_puct = c_puct
        self.device = torch.device(device)

    @torch.no_grad()
    def _evaluate(self, env: Connect4) -> tuple[np.ndarray, float]:
        state = torch.FloatTensor(env.get_state_tensor()).unsqueeze(0).to(self.device)
        log_probs, value = self.network(state)
        probs = torch.exp(log_probs).cpu().numpy().flatten()
        # Mask invalid moves
        valid = env.get_valid_moves()
        mask = np.zeros(7)
        mask[valid] = probs[valid]
        mask /= mask.sum() if mask.sum() > 0 else 1
        return mask, float(value.item())

    def search(self, env: Connect4) -> dict[int, float]:
        root = AlphaMCTSNode()
        root_policy, root_value = self._evaluate(env)
        root.total_value = root_value
        root.visit_count = 1

        for _ in range(self.n_simulations):
            node = root
            search_path = [node]
            sim_env = env.clone()
            actions_path: list[int] = []

            # SELECT
            while len(node.children) > 0 and not sim_env.done:
                valid_moves = sim_env.get_valid_moves()
                ucb_scores = {}
                for a in valid_moves:
                    child = node.children[a]
                    Q = child.value()
                    U = (self.c_puct * child.prior *
                         math.sqrt(node.visit_count) / (1 + child.visit_count))
                    ucb_scores[a] = Q + U
                best_a = max(ucb_scores, key=ucb_scores.get)

                sim_env.make_move(best_a)
                node = node.children[best_a]
                actions_path.append(best_a)
                search_path.append(node)

            # EXPAND + EVALUATE
            if not sim_env.done:
                policy, value = self._evaluate(sim_env)
                for a in sim_env.get_valid_moves():
                    node.children[a] = AlphaMCTSNode(policy[a])
                node.total_value = value
                node.visit_count = 1
            else:
                value = sim_env.get_result(env.current_player)

            # BACKUP
            for n in reversed(search_path):
                n.visit_count += 1
                n.total_value += value
                value = -value

        # 动作概率
        counts = np.array([
            root.children[a].visit_count if a in root.children else 0
            for a in range(7)
        ])
        counts = counts / counts.sum() if counts.sum() > 0 else counts
        return {i: float(counts[i]) for i in range(7) if counts[i] > 0}


# ============================================================
# §5  自对弈训练
# ============================================================

class TrainingExample:
    def __init__(self, state: np.ndarray, policy: np.ndarray,
                 value: float) -> None:
        self.state = state
        self.policy = policy
        self.value = value


class AlphaZeroTrainer:
    """AlphaZero 训练循环。"""

    def __init__(self, network: AlphaZeroNet, lr: float = 0.001,
                 device: str = "cpu") -> None:
        self.network = network.to(device)
        self.device = torch.device(device)
        self.optimizer = torch.optim.Adam(network.parameters(), lr=lr, weight_decay=1e-4)
        self.buffer: list[TrainingExample] = []
        self.max_buffer_size = 10000

    def self_play(self, mcts: AlphaMCTS, n_games: int = 1) -> list[TrainingExample]:
        examples = []
        for _ in range(n_games):
            env = Connect4()
            game_states: list[np.ndarray] = []
            game_policies: list[np.ndarray] = []
            current_player = 1

            while not env.done:
                state_tensor = env.get_state_tensor()
                policy_dict = mcts.search(env)
                policy = np.zeros(7)
                for a, p in policy_dict.items():
                    policy[a] = p

                game_states.append(state_tensor)
                game_policies.append(policy)

                # 按概率采样动作
                actions = list(policy_dict.keys())
                probs = np.array([policy_dict[a] for a in actions])
                probs /= probs.sum()
                action = np.random.choice(actions, p=probs)
                env.make_move(action)

            result = env.get_result(1)               # 玩家 1 视角
            for i, (s, p) in enumerate(zip(game_states, game_policies)):
                player = 1 if i % 2 == 0 else -1
                examples.append(TrainingExample(s, p, result * player))

        self.buffer.extend(examples)
        if len(self.buffer) > self.max_buffer_size:
            self.buffer = self.buffer[-self.max_buffer_size:]
        return examples

    def train_step(self, batch_size: int = 32) -> dict[str, float]:
        if len(self.buffer) < batch_size:
            return {"policy_loss": 0.0, "value_loss": 0.0}

        batch = random.sample(self.buffer, batch_size)
        states = torch.FloatTensor(np.stack([ex.state for ex in batch])).to(self.device)
        target_policies = torch.FloatTensor(np.stack([ex.policy for ex in batch])).to(self.device)
        target_values = torch.FloatTensor(
            np.array([ex.value for ex in batch])
        ).unsqueeze(1).to(self.device)

        log_probs, values = self.network(states)
        policy_loss = -(target_policies * torch.exp(log_probs)).sum(dim=1).mean()
        value_loss = F.mse_loss(values, target_values)
        total_loss = policy_loss + value_loss

        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        return {"policy_loss": float(policy_loss.item()),
                "value_loss": float(value_loss.item())}

    def train_iteration(self, mcts: AlphaMCTS, n_self_play: int = 5,
                        n_train_steps: int = 20, batch_size: int = 32) -> dict[str, float]:
        self.self_play(mcts, n_self_play)
        total_pl, total_vl = 0.0, 0.0
        for _ in range(n_train_steps):
            info = self.train_step(batch_size)
            total_pl += info["policy_loss"]
            total_vl += info["value_loss"]
        n = max(1, n_train_steps)
        return {"policy_loss": total_pl / n, "value_loss": total_vl / n}


# ============================================================
# §6  演示
# ============================================================

def demo_mcts() -> None:
    print("=" * 60)
    print("MCTS 与 AlphaZero 风格 RL 演示")
    print("=" * 60)

    # ---- 纯 MCTS ----
    print("\n--- 纯 MCTS (Connect 4) ---")
    env = Connect4()
    mcts = PureMCTS(n_simulations=100)

    # 快速对局
    print("MCTS 自对弈 1 局:")
    print(f"初始棋盘:\n{env}")

    moves = 0
    while not env.done and moves < 10:
        policy = mcts.search(env)
        if not policy:
            break
        best = max(policy, key=policy.get)
        env.make_move(best)
        moves += 1
        print(f"\n第 {moves} 步: 落子列 {best}, 策略={dict(sorted(policy.items()))}")

    print(f"\n最终棋盘:\n{env}")
    print(f"胜者: {env.winner}" if env.winner else "平局/未结束")

    # ---- AlphaZero 网络 ----
    print("\n--- AlphaZero 网络结构 ---")
    net = AlphaZeroNet(input_channels=3, num_actions=7,
                       num_res_blocks=4, channels=32)
    n_params = sum(p.numel() for p in net.parameters())
    print(f"参数: {n_params:,}")

    dummy = torch.randn(1, 3, 6, 7)
    with torch.no_grad():
        log_p, val = net(dummy)
    print(f"输入 {dummy.shape} -> Policy {log_p.shape}, Value {val.item():.4f}")

    # ---- AlphaMCTS ----
    print("\n--- AlphaMCTS 对弈 ---")
    alpha_mcts = AlphaMCTS(net, n_simulations=30)
    env2 = Connect4()
    policy = alpha_mcts.search(env2)
    print(f"初始搜索策略: {policy}")

    best_move = max(policy, key=policy.get)
    print(f"推荐落子: 列 {best_move}")

    # 执行几步
    for step in range(5):
        if env2.done:
            break
        policy = alpha_mcts.search(env2)
        if not policy:
            break
        best_move = max(policy, key=policy.get)
        env2.make_move(best_move)
    print(f"\n5步后棋盘:\n{env2}")

    # 简短训练
    print("\n--- AlphaZero 简短训练 ---")
    trainer = AlphaZeroTrainer(net, lr=0.001)
    for i in range(3):
        info = trainer.train_iteration(alpha_mcts, n_self_play=2,
                                        n_train_steps=5, batch_size=8)
        print(f"  Iter {i+1}: policy_loss={info['policy_loss']:.4f}, "
              f"value_loss={info['value_loss']:.4f}, "
              f"buffer={len(trainer.buffer)}")


if __name__ == "__main__":
    demo_mcts()
    print("\n✅ MCTS 篇执行完毕!")
