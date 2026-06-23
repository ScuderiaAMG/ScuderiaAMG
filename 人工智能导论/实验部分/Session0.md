# 五分钟实验演示讲稿（零基础版）

---

## 🛠 演示前 2 分钟准备（老师来之前做好）

打开两个终端窗口，分别运行：

**终端1（放屏幕左边）：**
```bash
cd "D:\Repositories\Escherichia30636\人工智能导论\实验部分\mission2"
python maze_rl2.py
```

**终端2（放屏幕右边）：**
```bash
cd "D:\Repositories\Escherichia30636\人工智能导论\实验部分\mission3"
python animal_expert2.py
```

同时打开代码编辑器（VS Code），左侧打开 `maze_rl2.py`，右侧打开 `animal_expert2.py` 和 `knowledge.json`，提前排好标签页。

**最终屏幕布局：左边任务二窗口，右边任务三窗口，编辑器在后台。老师一来，先看桌面上的两个运行窗口。**

---

## ⏱ 时间分配

| 时间段 | 内容 | 累计 |
|--------|------|------|
| 0:00-0:10 | 开场：两个任务一句话 | 0:10 |
| 0:10-0:20 | 任务二：程序已经在跑，指一下界面就切代码 | 0:20 |
| 0:20-2:20 | 任务二：逐行讲代码（QLearningAgent → MazeCanvas → MazeApp） | 2:20 |
| 2:20-2:30 | 任务三：切换到窗口指一下，立刻切代码 | 2:30 |
| 2:30-4:30 | 任务三：逐行讲代码（Rule → KnowledgeBase → InferenceEngine → UI） | 4:30 |
| 4:30-5:00 | 收尾总结 | 5:00 |

---

## 📖 完整讲稿

---

### 【0:00 — 开场白】（10秒）

> "老师好。我选了实验二和实验三。任务二是 **Q-Learning 走迷宫**，让智能体自己试错学会最优路径。任务三是**产生式动物识别系统**，15 条 IF-THEN 规则正向推理。程序已经在跑了，我直接讲代码。"

---

### 【0:10 — 任务二：Q-Learning 迷宫，指一下界面即切代码】（10秒）

> *（指一下左边 maze_rl2.py 窗口——迷宫已经在训练中或已收敛、金色路径可见）*
>
> "左边这个窗口：6×6 网格，红色小球是智能体，灰色是障碍物，金色线是收敛后提取的最优路径。内部是一个 Q 表驱动它走。切到代码。"

---

### 【0:20 — 任务二：逐行讲代码】（120秒）

> *（切到 VS Code，打开 maze_rl2.py，从头快速滚一遍展示整体结构，然后定位到核心代码逐段讲）*

> "整个文件 300 行，从上往下三大块：
>
> **第 10-43 行 QLearningAgent**——管 Q 表的读写和更新，四个方法：init、check_state_exist、choose_action、learn。
> **第 45-146 行 MazeCanvas**——管地图环境，三个方法：generate_obstacles 随机生成障碍物、step 执行动作返回奖励、paintEvent 画界面（这个不讲了，就是 Qt 的 drawRect + drawEllipse）。
> **第 148-296 行 MazeApp**——管训练总控，核心是 train_step 训练循环、收敛判定、最优路径提取。
>
> 图形界面代码（initUI、create_spinbox、toggle_training 这些）全是 PyQt5 样板，直接跳过。下面讲核心算法。
>
> ---
>
> **第一块：QLearningAgent。**
>
> `__init__`，第 11-16 行。四个参数：`actions` 四个方向 0 1 2 3 对应上下左右。`lr=0.1` 学习率 α，`gamma=0.9` 折扣因子 γ，`epsilon=0.9` 贪心率。第 16 行 `q_table = {}`——**Q 表用 Python 字典**，键是状态 `(r,c)` 元组，值是长为 4 的列表 `[上,下,左,右]`。
>
> `check_state_exist`，第 18-20 行：没见过的格子初始化为 `[0.0, 0.0, 0.0, 0.0]`，四个方向一视同仁，防 KeyError。
>
> `choose_action`，第 22-32 行。**ε-greedy 策略**。第 25 行 `if test_mode or random < 0.9`：test_mode 短路——只在最后提取路径时用，训练时走下面。90% 走第 26-29 行：`np.max` 找最大值，`actions_with_max` 处理平局，`random.choice` 随机挑。10% 走第 31 行纯随机。**利用和探索：90% 走已知最好的，10% 乱走试新路。**
>
> `learn`，第 34-41 行。**Q-Learning 核心。** 第 36 行 `q_predict = Q[s][a]` 取老分数。第 37-40 行算 `q_target`：非终点 = `r + γ × max(Q[s'])`（TD 目标），终点 = `r`（无未来）。第 41 行 `Q += α × (q_target - q_predict)`——**往 TD 目标方向挪 α=0.1 的一小步**。
>
> ---
>
> **第二块：MazeCanvas，只讲 step 方法，第 77-103 行。** 这是环境交互接口，输入动作编号，返回 `(next_state, reward, done)`。
>
> 第 82-86 行边界检查：四个方向各自判断不越界。超出边界 `r` 不变——留在原地。
>
> 三种奖励分支：第 88-91 行到终点 → `reward=+100, done=True`，next_state 设为字符串 `'terminal'`（用字符串而非坐标元组，learn 里 `!= 'terminal'` 就能区分）。第 92-96 行撞障碍物 → `reward=-10, done=False`，退回原地。第 97-100 行走空地 → `reward=-1`。**每步扣 1 分逼智能体走最短路径——绕路就多扣分。**
>
> generate_obstacles 和 paintEvent 跳过不讲。
>
> ---
>
> **第三块：MazeApp，三个核心设计。**
>
> **训练主循环 train_step，第 240-268 行。** 每步四步走：`choose_action` → `step` → `learn` → `current_steps += 1`。回合结束（done）时：计数 +1 → 收敛判定 → 重置回起点。QTimer 每 10ms 调一次。
>
> **收敛判定，第 252-256 行。** 这回合步数 == 上回合 → `stable_count += 1`；不等 → 归零。达到 `convergence_threshold=3` 自动停训练。**工程启发式：连续 3 回合步数不变即认为 Q 表稳定。** 不是严格 Q 值 δ 收敛判据，但对 6×6 迷宫够用。
>
> **最优路径提取，第 270-295 行。** 从起点出发，第 282 行 `choose_action(state, test_mode=True)` 纯贪婪——不再有 10% 随机。第 274 行 `visited = set()` 防环路。第 290 行防撞墙的防御代码。最后赋给 `canvas.optimal_path` 触发重绘。
>
> 迷宫重置的数量检查（第 215 行）跳过不讲。"

---

### 【2:20 — 任务三：产生式动物识别，指一下界面即切代码】（10秒）

> *（切换到右边 animal_expert2.py 窗口，界面上已有虎的推理结果）*
>
> "右边这个：左边勾特征，右边出推理步骤。刚才勾了有毛发、吃肉、黄褐色、黑色条纹，系统三步推出虎：R1 有毛发→哺乳动物，R5 吃肉→食肉动物，R9 哺乳动物+食肉动物+黄褐色+黑色条纹→虎。界面很简单，核心在推理引擎。切代码。"

---

### 【2:30 — 任务三：逐行讲代码】（120秒）

> *（切到 VS Code，先打开 knowledge.json 瞄一眼结构，再打开 animal_expert2.py 从头快速滚一遍展示整体划分，然后定位到核心代码逐段讲）*

> "任务三也是从上往下三层划分：
>
> **第 10-16 行 Rule 类**——JSON 规则到 Python 对象的桥梁，四个字段。
> **第 17-71 行 KnowledgeBase**——加载 JSON、自动推导 targets、提取基础特征。
> **第 74-124 行 InferenceEngine**——正向链接推理引擎，核心是 forward_chaining 的三阶段循环。
> **第 127-291 行 AnimalExpertSystem**——PyQt5 界面，initUI 画复选框、run_inference 调引擎并展示结果。
>
> 界面层 initUI 全是 Qt 布局样板代码，直接跳过。下面讲数据层和引擎层。
>
> ---
>
> **第零层：Rule 类，第 10-16 行。**
>
> 四个字段：`rule_id` 如 'R1'，`premise`——注意第 13 行 `set(premise)`，**把列表转成 set**，`conclusion` 结论，`priority` 数字越小越优先。为什么用 set？后面匹配只需要一行 `premise.issubset(working_memory)`——集合子集判断 O(n)，一行判断所有前提是否被满足。
>
> ---
>
> **第一层：KnowledgeBase + knowledge.json。**
>
> 先看 JSON（切过去）。两个顶层字段：`targets` 7 种目标动物，`rules` 15 条 R1-R15。每条四个字段。R9 举例：`priority: 3`, `premise: ["哺乳动物","食肉动物","黄褐色","黑色条纹"]`, `conclusion: "虎"`。就是 **IF 哺乳动物 AND 食肉动物 AND 黄褐色 AND 黑色条纹 THEN 虎**。R1 有毛发→哺乳动物，R5 吃肉→食肉动物。**R5 前提只有"吃肉"，不依赖"哺乳动物"——和 R1 是并行规则链。** R14 鸟类+会游泳+不会飞+黑白二色→企鹅。
>
> `load_from_json`，第 36-61 行。第 44-46 行遍历 rules 数组，每条包装成 Rule 对象。第 50-59 行 targets 自动推导的兜底逻辑：JSON 没写 targets 就扫描所有规则，找"作为结论但从未作为前提"的概念——就是最终目标动物。当前 JSON 显式声明了所以不走这个分支。
>
> `get_all_premises`，第 64-71 行。遍历所有规则的 premise，**排除中间结论和目标**，只留用户能直接观察的特征。返回值直接驱动 UI 生成复选框，改 JSON 加特征自动出现。
>
> ---
>
> **第二层：InferenceEngine.forward_chaining，第 79-124 行。核心。**
>
> 第 80 行 `working_memory = set(initial_facts)`——工作内存也用 set，和 Rule.premise 类型一致。第 87 行 `used_rules = set()`——**防死循环的关键**，已触发规则不再匹配。
>
> 推理是三阶段循环，第 91-122 行：
>
> **匹配，第 96-98 行。** 遍历 `self.kb.rules`，条件：`rule_id not in used_rules` **且** `premise.issubset(working_memory)`。第一个条件防重复触发——R1 触发后"哺乳动物"还在 WM 里，不用 used_rules 下轮 R1 又会匹配，无限循环。第二个 `issubset` 就是 set 的威力——一行判断所有前提。
>
> **冲突消解，第 104 行。** `conflict_set.sort(key=lambda r: (r.priority, -len(r.premise)))`。**priority 升序——数字越小越优先**，R1(priority=1) 在 R5(priority=2) 前触发。同 priority 下 `-len(premise)`——条件越多越优先。这保证了推理自然顺序：先推中间类别，再匹配最终动物。
>
> **执行，第 107-122 行。** 取排序后第一条：`used_rules` 登记，`working_memory` 加入结论，拼日志。第 120-122 行：结论在 targets 中立刻 break——找到目标不用继续。
>
> 拿虎走一遍：初始 WM={"有毛发","吃肉","黄褐色","黑色条纹"}。第一轮 R1 和 R5 都匹配，priority 排序 R1(1) 先触发，WM 加入"哺乳动物"。第二轮只剩 R5，触发，WM 加入"食肉动物"。第三轮 R9 四个前提全满足，触发，"虎"在 targets 中 break。三步，三行日志。
>
> ---
>
> **第三层：界面层只讲 run_inference 的推理调用和部分匹配，第 228-286 行。initUI 跳过。**
>
> 第 237 行调 `forward_chaining` 正常推理。第 244 行精确匹配成功就直接输出。关键是第 247 行的 else 分支——**部分匹配推荐**。
>
> `get_all_dependencies`，第 251-264 行。**递归展开某个目标动物的完整特征依赖树。** 比如"虎"递归下去：有毛发+产奶→哺乳动物，吃肉→食肉动物，加上黄褐色、黑色条纹，五个底层特征全挖出来。第 252-256 行 `visited` 集合防环——规则 A→B 且 B→A 形成环的话，普通递归直接爆栈，visited 就是安全网。
>
> 第 266-275 行遍历每个目标动物算交集：`intersect = target_deps ∩ final_memory`，交集非空就加入候选。第 282 行按命中数降序排——匹配特征越多越靠前。"

---

### 【4:30 — 收尾总结】（30秒）

> "总结一下。
>
> 任务二核心就一行公式：`Q += α × (r + γ×max Q[s'] - Q[s][a])`。围绕它建了三块代码：QLearningAgent 管 Q 表读写和 ε-greedy，MazeCanvas 的 step 管环境奖励，MazeApp 管训练循环加连续三步不变的收敛判定。
>
> 任务三核心是一个三阶段循环：匹配→冲突消解→执行。匹配用 set 的 issubset 一行搞定，冲突消解按 priority 升序保证先推中间结论再推目标，执行完检查是否命中 targets。知识库放 JSON 里和推理引擎解耦，部分匹配用递归展开依赖树做特征推荐。
>
> 两个任务都满足实验指导书要求。我的演示完毕，谢谢老师！"

---

## 📋 快速参考卡

### 代码结构速查

**maze_rl2.py（300行，三大块）**

| 行号 | 模块 | 职责 | 讲/跳 |
|------|------|------|-------|
| 10-43 | QLearningAgent | Q 表读写、ε-greedy、TD 更新 | **讲** |
| 45-146 | MazeCanvas | step() 环境反馈、paintEvent 绘制 | 只讲 step |
| 148-296 | MazeApp | train_step、收敛判定、路径提取 | **讲** |

**animal_expert2.py（297行，四层）**

| 行号 | 模块 | 职责 | 讲/跳 |
|------|------|------|-------|
| 10-16 | Rule | JSON→Python，premise 转 set | **讲** |
| 17-71 | KnowledgeBase | 加载 JSON、自动推导 targets | **讲** |
| 74-124 | InferenceEngine | forward_chaining 三阶段循环 | **讲** |
| 127-291 | AnimalExpertSystem | initUI（跳）、run_inference（讲）| 只讲推理调用 |

### Q-Learning 核心（maze_rl2.py 第 34-41 行）

```
36: q_predict = Q[s][a]
38: q_target = r + γ·max Q[s']       # 非终点
40: q_target = r                     # 终点
41: Q[s][a] += α·(q_target - q_predict)
```
即：`新Q = 旧Q + 学习率×(即时奖励 + 折扣×未来最优 - 旧Q)`

### 产生式推理核心（animal_expert2.py 第 91-122 行）

```
while 有新规则可触发:
  匹配    → issubset() 筛出前提全满足的未用规则
  冲突消解 → sort by (priority, -len(premise))，越小越优先
  执行    → 结论加入工作内存，命中 target 则 break
```

### 追问应对

- **收敛为什么是全局最优？** → "严格说不是，连续三步相同只是启发式判据。没有做 Q 值 δ 收敛检测。对演示迷宫有效，是工程权衡。"
- **迷宫堵死怎么办？** → "目前只检查了数量，没做 BFS 连通性校验。后续可以加，但随机生成实测中基本不会堵死。"
- **为什么不用数据库存规则？** → "15 条规则的小系统用 JSON 足够，可读性好、零依赖、直接用 Python json 库。规则量大了再迁数据库。"
- **YOLO 文件是什么？** → "之前尝试过图像识别+产生式推理的结合方向，最终二选一提交的是纯产生式系统。那个文件不在本次验收范围。"
- **set 为什么比 list 好？** → "issubset 是 C 实现的哈希查找，O(n)。如果用 list 得自己写双重循环逐个比对，而且 set 自动去重。"
