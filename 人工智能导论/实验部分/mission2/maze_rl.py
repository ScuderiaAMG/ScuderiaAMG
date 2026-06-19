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
        self.actions = actions          # 动作空间 [0:上, 1:下, 2:左, 3:右]
        self.lr = learning_rate         # 学习率
        self.gamma = reward_decay       # 折扣因子
        self.epsilon = e_greedy         # 贪婪度 (探索与利用的权衡)
        self.q_table = {}               # Q表，格式 {state: [q_up, q_down, q_left, q_right]}

    def check_state_exist(self, state):
        if state not in self.q_table:
            # 如果状态不在 Q 表中，初始化为 0
            self.q_table[state] = [0.0] * len(self.actions)

    def choose_action(self, state):
        self.check_state_exist(state)
        # 按照 epsilon-greedy 策略选择动作
        if np.random.uniform() < self.epsilon:
            # 选择 Q 值最大的动作 (利用)
            state_action = self.q_table[state]
            max_value = np.max(state_action)
            # 处理多个最大值的情况（随机从中挑一个）
            actions_with_max = [i for i, v in enumerate(state_action) if v == max_value]
            action = random.choice(actions_with_max)
        else:
            # 随机选择动作 (探索)
            action = random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        q_predict = self.q_table[s][a]
        
        if s_ != 'terminal':
            q_target = r + self.gamma * np.max(self.q_table[s_])
        else:
            q_target = r  # 达到终点，没有下一个状态
            
        # 更新 Q 值
        self.q_table[s][a] += self.lr * (q_target - q_predict)


# ==========================================
# 2. 迷宫绘制与环境组件 (PyQt5 Widget)
# ==========================================
class MazeCanvas(QWidget):
    def __init__(self, rows, cols, num_obstacles):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.num_obstacles = num_obstacles
        self.cell_size = 40
        self.setMinimumSize(self.cols * self.cell_size + 20, self.rows * self.cell_size + 20)
        self.reset_env()

    def reset_env(self):
        """重置环境：生成新迷宫尺寸、随机起点、终点和障碍物"""
        self.start_pos = (0, 0)
        self.agent_pos = list(self.start_pos)
        self.goal_pos = (self.rows - 1, self.cols - 1)
        self.obstacles = []
        self.generate_obstacles()
        self.update()

    def generate_obstacles(self):
        """随机生成障碍物，确保不覆盖起点和终点"""
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
        """环境步进逻辑，返回 (下一个状态, 奖励, 是否结束)"""
        s = tuple(self.agent_pos)
        r, c = s

        # 执行动作: 0=Up, 1=Down, 2=Left, 3=Right
        if action == 0 and r > 0: r -= 1
        elif action == 1 and r < self.rows - 1: r += 1
        elif action == 2 and c > 0: c -= 1
        elif action == 3 and c < self.cols - 1: c += 1

        next_state = (r, c)
        
        # 奖励设计
        if next_state == self.goal_pos:
            reward = 100
            done = True
            next_state = 'terminal'
        elif next_state in self.obstacles:
            reward = -10
            done = False
            next_state = s # 撞墙后停留在原地
            self.agent_pos = list(s)
        else:
            reward = -1 # 每走一步扣1分，鼓励找最短路径
            done = False
            self.agent_pos = list(next_state)
            
        self.update() # 触发重绘
        return next_state, reward, done

    def paintEvent(self, event):
        """使用 QPainter 渲染迷宫网格"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制网格和空白单元
        for r in range(self.rows):
            for c in range(self.cols):
                rect = QRect(c * self.cell_size + 10, r * self.cell_size + 10, self.cell_size, self.cell_size)
                pos = (r, c)
                
                if pos == self.start_pos:
                    painter.setBrush(QBrush(QColor(173, 216, 230))) # 浅蓝色起点
                elif pos == self.goal_pos:
                    painter.setBrush(QBrush(QColor(144, 238, 144))) # 浅绿色终点
                elif pos in self.obstacles:
                    painter.setBrush(QBrush(QColor(105, 105, 105))) # 灰色障碍物
                else:
                    painter.setBrush(QBrush(QColor(255, 255, 255))) # 白色通道
                
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.drawRect(rect)

        # 绘制智能体 (红色圆球)
        ar, ac = self.agent_pos[0], self.agent_pos[1]
        agent_rect = QRect(ac * self.cell_size + 15, ar * self.cell_size + 15, self.cell_size - 10, self.cell_size - 10)
        painter.setBrush(QBrush(QColor(255, 69, 0)))
        painter.drawEllipse(agent_rect)


# ==========================================
# 3. 主窗口与训练控制台
# ==========================================
class MazeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("强化学习迷宫系统 (Q-Learning)")
        
        # 默认参数
        self.rows = 6
        self.cols = 6
        self.num_obstacles = 5
        
        # 初始化智能体和界面组件
        self.agent = QLearningAgent(actions=list(range(4)))
        self.episode_count = 0
        self.is_training = False
        
        self.initUI()
        
        # 训练循环定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.train_step)

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        h_layout = QHBoxLayout()

        # 左侧：迷宫画布
        self.canvas = MazeCanvas(self.rows, self.cols, self.num_obstacles)
        h_layout.addWidget(self.canvas)

        # 右侧：控制面板
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)

        # 参数调节
        self.lbl_info = QLabel("<b>迷宫参数设置</b>")
        v_layout.addWidget(self.lbl_info)

        self.spin_rows = self.create_spinbox("行数:", self.rows, 4, 15, v_layout)
        self.spin_cols = self.create_spinbox("列数:", self.cols, 4, 15, v_layout)
        self.spin_obs = self.create_spinbox("障碍物数量:", self.num_obstacles, 0, 40, v_layout)

        # 按钮
        self.btn_generate = QPushButton("生成新迷宫并重置")
        self.btn_generate.clicked.connect(self.generate_new_maze)
        v_layout.addWidget(self.btn_generate)

        self.btn_train = QPushButton("开始/暂停 训练")
        self.btn_train.clicked.connect(self.toggle_training)
        v_layout.addWidget(self.btn_train)
        
        self.lbl_status = QLabel("当前回合数: 0")
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
            
        self.rows = self.spin_rows.value()
        self.cols = self.spin_cols.value()
        self.num_obstacles = self.spin_obs.value()
        
        # 安全检查：防止障碍物过多导致死胡同（简单校验）
        if self.num_obstacles >= (self.rows * self.cols - 2):
            QMessageBox.warning(self, "警告", "障碍物过多，没有通道！")
            return

        self.canvas.rows = self.rows
        self.canvas.cols = self.cols
        self.canvas.num_obstacles = self.num_obstacles
        self.canvas.setMinimumSize(self.cols * self.canvas.cell_size + 20, self.rows * self.canvas.cell_size + 20)
        self.canvas.reset_env()
        
        # 清空重置智能体大脑
        self.agent = QLearningAgent(actions=list(range(4)))
        self.episode_count = 0
        self.lbl_status.setText(f"当前回合数: {self.episode_count}")
        self.adjustSize() # 自适应窗口大小

    def toggle_training(self):
        if not self.is_training:
            self.is_training = True
            self.btn_train.setText("暂停 训练")
            self.timer.start(20) # 20毫秒执行一步，可以调整速度
        else:
            self.is_training = False
            self.btn_train.setText("继续 训练")
            self.timer.stop()

    def train_step(self):
        """RL 单步训练逻辑"""
        state = tuple(self.canvas.agent_pos)
        
        # 1. 选择动作
        action = self.agent.choose_action(state)
        
        # 2. 与环境交互
        next_state, reward, done = self.canvas.step(action)
        
        # 3. 学习更新 Q 表
        self.agent.learn(state, action, reward, next_state)
        
        # 4. 如果到达终点，重置回合
        if done:
            self.episode_count += 1
            self.lbl_status.setText(f"当前回合数: {self.episode_count}")
            self.canvas.agent_pos = list(self.canvas.start_pos)
            self.canvas.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MazeApp()
    ex.show()
    sys.exit(app.exec_())