import sys
import random
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSpinBox, QMessageBox)
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QRect

# ==========================================
# 1. Q-Learning 智能体核心算法
# ==========================================
class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = {}

    def check_state_exist(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)

    def choose_action(self, state, test_mode=False):
        self.check_state_exist(state)
        # 测试模式下完全利用已有经验 (epsilon = 0)
        if test_mode or np.random.uniform() < self.epsilon:
            state_action = self.q_table[state]
            max_value = np.max(state_action)
            actions_with_max = [i for i, v in enumerate(state_action) if v == max_value]
            action = random.choice(actions_with_max)
        else:
            action = random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_table[s][a]
        if s_ != 'terminal':
            q_target = r + self.gamma * np.max(self.q_table[s_])
        else:
            q_target = r
        self.q_table[s][a] += self.lr * (q_target - q_predict)


# ==========================================
# 2. 迷宫绘制与环境组件
# ==========================================
class MazeCanvas(QWidget):
    def __init__(self, rows, cols, num_obstacles):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.num_obstacles = num_obstacles
        self.cell_size = 40
        self.optimal_path = []  # 用于存储收敛后的最优路径
        self.setMinimumSize(self.cols * self.cell_size + 20, self.rows * self.cell_size + 20)
        self.reset_env()

    def reset_env(self):
        self.start_pos = (0, 0)
        self.agent_pos = list(self.start_pos)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.obstacles = []
        self.optimal_path = []
        self.generate_obstacles()
        self.update()

    def generate_obstacles(self):
        self.obstacles.clear()
        count = 0
        while count < self.num_obstacles:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            pos = (r, c)
            if pos != self.start_pos and pos != self.goal_pos and pos not in self.obstacles:
                self.obstacles.append(pos)
                count += 1

    def step(self, action):
        s = tuple(self.agent_pos)
        r, c = s
        if action == 0 and r > 0: r -= 1
        elif action == 1 and r < self.rows - 1: r += 1
        elif action == 2 and c > 0: c -= 1
        elif action == 3 and c < self.cols - 1: c += 1
        next_state = (r, c)
        
        if next_state == self.goal_pos:
            reward = 100
            done = True
            next_state = 'terminal'
        elif next_state in self.obstacles:
            reward = -10
            done = False
            next_state = s
            self.agent_pos = list(s)
        else:
            reward = -1
            done = False
            self.agent_pos = list(next_state)
            
        self.update()
        return next_state, reward, done

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. 绘制网格
        for r in range(self.rows):
            for c in range(self.cols):
                rect = QRect(c * self.cell_size + 10, r * self.cell_size + 10, self.cell_size, self.cell_size)
                pos = (r, c)
                if pos == self.start_pos:
                    painter.setBrush(QBrush(QColor(173, 216, 230)))
                elif pos == self.goal_pos:
                    painter.setBrush(QBrush(QColor(144, 238, 144)))
                elif pos in self.obstacles:
                    painter.setBrush(QBrush(QColor(105, 105, 105)))
                else:
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.drawRect(rect)

        # 2. 绘制最优路径 (如果已收敛)
        if self.optimal_path:
            pen = QPen(QColor(255, 215, 0), 5)  # 金色线条，宽度5
            painter.setPen(pen)
            for i in range(len(self.optimal_path) - 1):
                r1, c1 = self.optimal_path[i]
                r2, c2 = self.optimal_path[i+1]
                x1 = c1 * self.cell_size + 10 + self.cell_size // 2
                y1 = r1 * self.cell_size + 10 + self.cell_size // 2
                x2 = c2 * self.cell_size + 10 + self.cell_size // 2
                y2 = r2 * self.cell_size + 10 + self.cell_size // 2
                painter.drawLine(x1, y1, x2, y2)

        # 3. 绘制智能体
        ar, ac = self.agent_pos[0], self.agent_pos[1]
        agent_rect = QRect(ac * self.cell_size + 15, ar * self.cell_size + 15, self.cell_size - 10, self.cell_size - 10)
        painter.setBrush(QBrush(QColor(255, 69, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(agent_rect)


# ==========================================
# 3. 主窗口与训练控制台
# ==========================================
class MazeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("强化学习迷宫系统 - 自动收敛展示版")
        self.rows, self.cols, self.num_obstacles = 6, 6, 5
        self.init_rl_params()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.train_step)

    def init_rl_params(self):
        self.agent = QLearningAgent(actions=list(range(4)))
        self.episode_count = 0
        self.is_training = False
        
        # --- 新增：收敛判断所需的变量 ---
        self.current_steps = 0       # 当前回合步数
        self.last_episode_steps = -1 # 上一回合步数
        self.stable_count = 0        # 连续相同步数的回合数
        self.convergence_threshold = 3 # 连续3回合步数相同即认为收敛

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        h_layout = QHBoxLayout()

        self.canvas = MazeCanvas(self.rows, self.cols, self.num_obstacles)
        h_layout.addWidget(self.canvas)

        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)

        self.spin_rows = self.create_spinbox("行数:", self.rows, 4, 15, v_layout)
        self.spin_cols = self.create_spinbox("列数:", self.cols, 4, 15, v_layout)
        self.spin_obs = self.create_spinbox("障碍物数量:", self.num_obstacles, 0, 40, v_layout)

        self.btn_generate = QPushButton("生成新迷宫并重置")
        self.btn_generate.clicked.connect(self.generate_new_maze)
        v_layout.addWidget(self.btn_generate)

        self.btn_train = QPushButton("开始/暂停 训练")
        self.btn_train.clicked.connect(self.toggle_training)
        v_layout.addWidget(self.btn_train)
        
        self.lbl_status = QLabel("当前回合数: 0\n连续稳定回合: 0")
        self.lbl_status.setStyleSheet("color: blue; font-weight: bold; margin-top: 20px;")
        v_layout.addWidget(self.lbl_status)

        h_layout.addLayout(v_layout)
        main_widget.setLayout(h_layout)

    def create_spinbox(self, label_text, default_val, min_val, max_val, layout):
        h_box = QHBoxLayout()
        lbl = QLabel(label_text)
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default_val)
        h_box.addWidget(lbl)
        h_box.addWidget(spin)
        layout.addLayout(h_box)
        return spin

    def generate_new_maze(self):
        if self.is_training:
            self.toggle_training()
        self.rows, self.cols, self.num_obstacles = self.spin_rows.value(), self.spin_cols.value(), self.spin_obs.value()
        if self.num_obstacles >= (self.rows * self.cols - 2):
            QMessageBox.warning(self, "警告", "障碍物过多，没有通道！")
            return

        self.canvas.rows, self.canvas.cols, self.canvas.num_obstacles = self.rows, self.cols, self.num_obstacles
        self.canvas.setMinimumSize(self.cols * self.canvas.cell_size + 20, self.rows * self.canvas.cell_size + 20)
        self.canvas.reset_env()
        self.init_rl_params() # 重置强化学习相关参数和记录
        self.update_status_label()
        self.adjustSize()

    def update_status_label(self):
        self.lbl_status.setText(f"当前回合数: {self.episode_count}\n连续稳定回合: {self.stable_count}/{self.convergence_threshold}")

    def toggle_training(self):
        if not self.is_training:
            self.is_training = True
            self.btn_train.setText("暂停 训练")
            self.canvas.optimal_path = [] # 训练时隐藏最优路径
            self.timer.start(10) # 调快速度以更快看到结果
        else:
            self.is_training = False
            self.btn_train.setText("继续 训练")
            self.timer.stop()

    def train_step(self):
        state = tuple(self.canvas.agent_pos)
        action = self.agent.choose_action(state)
        next_state, reward, done = self.canvas.step(action)
        self.agent.learn(state, action, reward, next_state)
        
        self.current_steps += 1 # 累加步数

        if done:
            self.episode_count += 1
            
            # --- 收敛判定逻辑 ---
            if self.current_steps == self.last_episode_steps:
                self.stable_count += 1
            else:
                self.last_episode_steps = self.current_steps
                self.stable_count = 0
            
            self.update_status_label()
            
            # 判断是否达到收敛阈值
            if self.stable_count >= self.convergence_threshold:
                self.toggle_training()
                self.extract_and_draw_optimal_path()
                QMessageBox.information(self, "训练完成", f"智能体已收敛！\n最优路径需要步数: {self.last_episode_steps}")
                
            # 重置回合状态
            self.current_steps = 0
            self.canvas.agent_pos = list(self.canvas.start_pos)
            self.canvas.update()

    def extract_and_draw_optimal_path(self):
        """利用已收敛的Q表，提取无探索(纯贪婪)的最优路径"""
        path = []
        state = self.canvas.start_pos
        visited = set() # 防止极端情况下的死循环
        
        while state != self.canvas.goal_pos:
            if state in visited:
                break
            visited.add(state)
            path.append(state)
            
            # 测试模式提取最佳动作
            action = self.agent.choose_action(state, test_mode=True)
            r, c = state
            if action == 0 and r > 0: r -= 1
            elif action == 1 and r < self.rows - 1: r += 1
            elif action == 2 and c > 0: c -= 1
            elif action == 3 and c < self.cols - 1: c += 1
            
            state = (r, c)
            if state in self.canvas.obstacles: # 理论上收敛后不会撞墙
                break
                
        path.append(self.canvas.goal_pos)
        self.canvas.optimal_path = path
        self.canvas.update() # 触发重绘，画出金色线条

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MazeApp()
    ex.show()
    sys.exit(app.exec_())