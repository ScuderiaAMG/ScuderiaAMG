# 第10讲：控制系统的动态性能 Part 2

---

## 一、欠阻尼二阶系统的性能指标

### 1.0 预备知识（第9讲回顾）

**动态性能分析**：在零初始条件下，对系统的**单位阶跃响应**进行动态过程分析。

**二阶系统标准形式**（闭环传递函数）：

$$\frac{C(s)}{R(s)} = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

对应微分方程：$\ddot{c}(t) + 2\zeta\omega_n \dot{c}(t) + \omega_n^2 c(t) = \omega_n^2 r(t)$

**特征根**：$s_{1,2} = -\zeta\omega_n \pm \omega_n\sqrt{\zeta^2 - 1}$

| 阻尼比 $\zeta$ | 特征根 | 稳定性 |
|---------------|--------|--------|
| $\zeta < 0$ | 正实部 | 不稳定 |
| $\zeta = 0$ | $\pm j\omega_n$（纯虚根） | 临界稳定（无阻尼） |
| $0 < \zeta < 1$ | $-\zeta\omega_n \pm j\omega_d$（共轭复根，负实部） | **稳定（欠阻尼）** |
| $\zeta = 1$ | $-\omega_n$（重实根） | 稳定（临界阻尼） |
| $\zeta > 1$ | 两负实根 | 稳定（过阻尼） |

**工程首选**：$\zeta = 0.4 \sim 0.8$ 的欠阻尼状态（兼顾快速性与平稳性），常取 $\zeta = 1/\sqrt{2} \approx 0.707$。

---

### 1.1 欠阻尼二阶系统的单位阶跃响应

当 $0 < \zeta < 1$ 时，单位阶跃响应：

$$c(t) = 1 - \frac{1}{\sqrt{1 - \zeta^2}} e^{-\zeta\omega_n t} \sin(\omega_d t + \theta), \quad t \geq 0$$

其中：
- $\omega_d = \omega_n\sqrt{1 - \zeta^2}$ —— **阻尼振荡角频率**
- $\theta = \arccos \zeta$ —— 初相角
- S 平面上的几何关系：$\sin\theta = \sqrt{1-\zeta^2},\ \cos\theta = \zeta$

```
      Im
       │
  jωd  ●
       │  θ
───────┼──── Re
  -ζωn │
       │
 -jωd  ●
```

---

### 1.2 七个动态性能指标

```
  c(t)
   ↑
 σp%│    ┌─ 峰值
    │   / \
  1 │  /   \___ 稳态值
    │ /       \_______
0.5 │/
    │
  0 └──┬──┬──┬────────→ t
       td  tr tp     ts
```

| 指标 | 符号 | 定义 |
|------|------|------|
| 延迟时间 | $t_d$ | 响应第一次达到稳态值 50% 的时间 |
| 上升时间 | $t_r$ | 响应从稳态值 10% 上升到 90% 的时间（或从 0 第一次到达稳态值的时间） |
| 峰值时间 | $t_p$ | 响应到达第一个峰值的时间 |
| 最大超调量 | $\sigma_p$ | 响应峰值超过稳态值的百分比 |
| 调整时间（调节时间） | $t_s$ | 响应进入并保持在稳态值 ±Δ 误差带内所需的最短时间 |
| 振荡次数 | $N$ | 在调整时间内响应曲线穿越稳态值次数的一半 |
| 衰减比 | — | 相邻两个同方向峰值之比 |

---

### 1.3 欠阻尼二阶系统性能指标公式推导

#### （1）上升时间 $t_r$

定义：$c(t)$ 第一次到达 1（稳态值）的时间。

$$c(t_r) = 1 - \frac{1}{\sqrt{1-\zeta^2}} e^{-\zeta\omega_n t_r} \sin(\omega_d t_r + \theta) = 1$$

$$\Rightarrow \sin(\omega_d t_r + \theta) = 0$$

$$\Rightarrow \omega_d t_r + \theta = \pi \quad (\text{第一次到达，不能取 } k\pi \text{ 中的 } 0 \text{ 或 } 2\pi)$$

$$\boxed{t_r = \frac{\pi - \theta}{\omega_d} = \frac{\pi - \arccos\zeta}{\omega_n\sqrt{1-\zeta^2}}}$$

**结论**：要使 $t_r$ 减小（响应快），须**减小 $\zeta$**、**增大 $\omega_n$**。

---

#### （2）峰值时间 $t_p$

定义：$c(t)$ 第一次到达极大值的时间，即 $dc(t)/dt = 0$。

$$\frac{dc(t)}{dt} = \frac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}\left[\zeta\omega_n\sin(\omega_d t + \theta) - \omega_d\cos(\omega_d t + \theta)\right] = 0$$

$$\zeta\sin(\omega_d t + \theta) - \sqrt{1-\zeta^2}\cos(\omega_d t + \theta) = 0$$

$$\Rightarrow \sin(\omega_d t) = 0$$

第一个峰值对应 $\omega_d t_p = \pi$：

$$\boxed{t_p = \frac{\pi}{\omega_d} = \frac{\pi}{\omega_n\sqrt{1-\zeta^2}}}$$

**结论**：要使 $t_p$ 减小，须**减小 $\zeta$**、**增大 $\omega_n$**。

---

#### （3）最大超调量 $\sigma_p$

定义：$\sigma_p = \frac{c(t_p) - c(\infty)}{c(\infty)} \times 100\%$，其中 $c(\infty) = 1$。

代 $t_p = \pi/\omega_d$ 入 $c(t)$：

$$c(t_p) = 1 - \frac{1}{\sqrt{1-\zeta^2}} e^{-\frac{\zeta\omega_n\pi}{\omega_d}} \sin(\pi + \theta)$$

由 $\sin(\pi + \theta) = -\sin\theta = -\sqrt{1-\zeta^2}$：

$$c(t_p) = 1 + e^{-\frac{\zeta\pi}{\sqrt{1-\zeta^2}}}$$

$$\boxed{\sigma_p = e^{-\frac{\pi\zeta}{\sqrt{1-\zeta^2}}} \times 100\%}$$

**结论**：超调量**只与阻尼比 $\zeta$ 有关**！$\zeta$ 越大，$\sigma_p$ 越小。

| $\zeta$ | 0.2 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 |
|---------|-----|-----|-----|-----|-----|-----|
| $\sigma_p$ | 52.7% | 25.4% | 16.3% | 9.5% | 4.6% | 1.5% |

---

#### （4）调整时间 $t_s$

利用**包络线**法。定义上下包络线：

$$c_1(t) = 1 + \frac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}, \quad c_2(t) = 1 - \frac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}$$

$c(t)$ 始终在两条包络线之间（因为 $|\sin(\omega_d t + \theta)| \leq 1$）。

令 $c_1(t_s) - 1 = \Delta$：

$$\frac{e^{-\zeta\omega_n t_s}}{\sqrt{1-\zeta^2}} = \Delta$$

$$t_s = \frac{1}{\zeta\omega_n} \ln\frac{1}{\Delta\sqrt{1-\zeta^2}}$$

**工程近似公式**（常用，$\zeta = 0.4 \sim 0.8$）：

$$\boxed{t_s \approx \begin{cases} \dfrac{4}{\zeta\omega_n}, & \Delta = 2\% \\[8pt] \dfrac{3}{\zeta\omega_n}, & \Delta = 5\% \end{cases}}$$

**结论**：要使 $t_s$ 减小，须**增大 $\zeta$**（在 0.69 处 $t_s$ 最小，之后单调增加）、**增大 $\omega_n$**。

---

#### （5）振荡次数 $N$

响应曲线振荡周期 $T_d = \dfrac{2\pi}{\omega_d} = \dfrac{2\pi}{\omega_n\sqrt{1-\zeta^2}}$：

$$N = \frac{t_s}{T_d} \approx \begin{cases} \dfrac{4\sqrt{1-\zeta^2}}{2\pi\zeta}, & \Delta = 2\% \\[10pt] \dfrac{3\sqrt{1-\zeta^2}}{2\pi\zeta}, & \Delta = 5\% \end{cases}$$

**结论**：振荡次数 $N$ 只与 $\zeta$ 有关，$\zeta$ 越大振荡次数越少。

---

### 1.4 各性能指标与 $\zeta$、$\omega_n$ 的关系总结

| 性能指标 | 与 $\zeta$ 的关系 | 与 $\omega_n$ 的关系 | 只由 $\zeta$ 决定？ |
|----------|-------------------|----------------------|--------------------|
| $t_r$（上升时间） | $\zeta \downarrow \to t_r \downarrow$ | $\omega_n \uparrow \to t_r \downarrow$ | 否 |
| $t_p$（峰值时间） | $\zeta \downarrow \to t_p \downarrow$ | $\omega_n \uparrow \to t_p \downarrow$ | 否 |
| $\sigma_p$（超调量） | $\zeta \uparrow \to \sigma_p \downarrow$ | **无关** | **是** |
| $t_s$（调整时间） | $\zeta \uparrow$（至 0.69）$\to t_s \downarrow$ | $\omega_n \uparrow \to t_s \downarrow$ | 否 |
| $N$（振荡次数） | $\zeta \uparrow \to N \downarrow$ | **无关** | **是** |

### 1.5 工程设计方法

**设计矛盾**：
- 响应初期速度（$t_r$, $t_p$）要求 $\zeta$ 小
- 总体响应品质（$t_s$, $\sigma_p$, $N$）要求 $\zeta$ 大

**设计步骤**：
1. **先**根据 $\sigma_p$ 的要求选择 $\zeta$（一般 $\zeta = 0.4 \sim 0.8$）
2. **再**根据 $t_s$ 的要求确定 $\zeta\omega_n$，从而确定 $\omega_n$
3. **验算** $t_r$、$t_p$ 等其他指标

---

## 二、案例：车辆跟驰控制

### 2.1 问题描述

- 后车初始速度 $v^*$ m/s，与前车初始相对位移 10 m
- 前车以 $v^*$ m/s 匀速行驶
- 可测量：后车速度 $v(t)$、与前车的相对距离 $p(t)$
- **控制目标**：实现跟驰，保持相对距离约 5 m
- **约束**：
  - 动态过程中相对距离**不得小于 4.5 m**
  - 调节时间 $t_s \leq 2$ s（$\Delta = 2\%$）

### 2.2 数学建模

**定义状态变量**：
$$y(t) = 10 - p(t), \quad x(t) = v(t) - v^*$$

初始条件：$y(0) = 0,\ x(0) = 0$

**状态方程**：
$$\begin{cases} \dot{y}(t) = -\dot{p}(t) = v(t) - v^* = x(t) \\ \dot{x}(t) = \dot{v}(t) = u(t) \end{cases}$$

拉氏变换：
$$\begin{cases} sY(s) = X(s) \\ sX(s) = U(s) \end{cases}$$

**控制结构图**：
```
R(s) → [K₁] → [+] → [1/s] → [1/s] → Y(s)
          ↑      |
          [K₂] ←──┘
```

其中 $G_1(s) = K_1$（比例），$G_2(s) = K_2$（速度反馈）。

### 2.3 性能指标转化

- 期望输出：$y_{\text{ref}} = 10 - 5 = 5$，即 $R(s) = \frac{5}{s}$
- 最大超调量约束：$\sigma_p \leq \frac{10 - 4.5 - 5}{5} \times 100\% = 10\%$
- 调节时间约束：$t_s \leq 2$ s（$\Delta = 2\%$）

### 2.4 控制器参数设计

**闭环传递函数**：

$$G_B(s) = \frac{Y(s)}{R(s)} = \frac{K_1 K_2}{s^2 + K_2 s + K_1 K_2}$$

与标准二阶系统 $\dfrac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$ 对比：

$$\begin{cases} K_1 K_2 = \omega_n^2 \\ K_2 = 2\zeta\omega_n \end{cases}$$

**由 $\sigma_p \leq 10\%$**：

$$\sigma_p = e^{-\frac{\pi\zeta}{\sqrt{1-\zeta^2}}} \leq 0.1 \quad \Rightarrow \quad \zeta \geq 0.59$$

**由 $t_s \leq 2$ s（$\Delta = 2\%$）**：

$$t_s = \frac{4}{\zeta\omega_n} \leq 2 \quad \Rightarrow \quad \zeta\omega_n \geq 2$$

**选择**：$\zeta = 0.7,\ \omega_n = 3$（留有一定裕度）

$$\begin{cases} K_2 = 2\zeta\omega_n = 2 \times 0.7 \times 3 = 4.2 \\ K_1 = \dfrac{\omega_n^2}{K_2} = \dfrac{9}{4.2} \approx 2.2 \end{cases}$$

**控制器（时域）**：

$$u(t) = 4.2\left[2.2(5 - y(t)) - x(t)\right]$$

其中 $y(t) = 10 - p(t)$，$x(t) = v(t) - v^*$。

### 2.5 仿真对比

| 参数 | 算例1（不当参数） | 算例2（设计参数） |
|------|-------------------|-------------------|
| 参数值 | $K_1 = 4$, $K_2 = 3$ | $K_1 = 2.2$, $K_2 = 4.2$ |
| 相对距离 | **超过警戒线**（< 4.5 m） | 未超过警戒线 |
| 调节时间 | **超过 2 秒** | 在 2 秒内 |
| 结论 | 不满足要求 | 满足要求 |

### 2.6 延展思考

如果后车的初始速度不为 $v^*$，则 $x(0) \neq 0$，需考虑**非零初始条件**，此时：
- 全响应 = 零状态响应 + 零输入响应
- 零输入响应由初始速度差产生，可能导致更大的初始超调
- 可通过调整 $\zeta$ 预留更大的安全裕度

---

## 三、解题通法总结

### 3.1 欠阻尼二阶系统性能指标公式速查

| 指标 | 公式 | 依赖关系 |
|------|------|----------|
| 阻尼振荡频率 | $\omega_d = \omega_n\sqrt{1-\zeta^2}$ | — |
| 初相角 | $\theta = \arccos\zeta$ | — |
| 上升时间 | $t_r = \dfrac{\pi - \theta}{\omega_d}$ | $\zeta \downarrow, \omega_n \uparrow \to t_r \downarrow$ |
| 峰值时间 | $t_p = \dfrac{\pi}{\omega_d}$ | $\zeta \downarrow, \omega_n \uparrow \to t_p \downarrow$ |
| 超调量 | $\sigma_p = e^{-\frac{\pi\zeta}{\sqrt{1-\zeta^2}}} \times 100\%$ | **只与 $\zeta$ 有关**，$\zeta \uparrow \to \sigma_p \downarrow$ |
| 调整时间 | $t_s \approx \begin{cases} \frac{4}{\zeta\omega_n}, & \Delta = 2\% \\ \frac{3}{\zeta\omega_n}, & \Delta = 5\% \end{cases}$ | $\zeta \uparrow, \omega_n \uparrow \to t_s \downarrow$ |
| 振荡次数 | $N \approx \begin{cases} \frac{4\sqrt{1-\zeta^2}}{2\pi\zeta} \\ \frac{3\sqrt{1-\zeta^2}}{2\pi\zeta} \end{cases}$ | **只与 $\zeta$ 有关**，$\zeta \uparrow \to N \downarrow$ |
| 振荡周期 | $T_d = \dfrac{2\pi}{\omega_d}$ | — |

### 3.2 根据性能指标设计控制器参数的通法（四步法）

```
已知：被控对象传函 + 性能指标要求（σ_p, t_s, ...）

① 写出含待定参数的闭环传递函数 G_B(s)
        ↓
② 与标准二阶系统对比：
   G_B(s) = ω_n² / (s² + 2ζω_n s + ω_n²)
   列出待定参数与 ζ, ω_n 的关系式
        ↓
③ 根据性能指标解出 ζ, ω_n：
   • 由 σ_p = e^(-πζ/√(1-ζ²)) → ζ_min
   • 由 t_s = 3/(ζω_n) 或 4/(ζω_n) → ζω_n_min
   • 选取满足约束的 ζ, ω_n（留裕度）
        ↓
④ 代回 → 求控制器参数 → 验算其他指标
```

### 3.3 性能指标互求通法

**已知 $\zeta, \omega_n$ → 求性能指标**：直接代入公式。

**已知 $t_p$ 和 $\sigma_p$ → 求 $\zeta, \omega_n$**：

由 $\sigma_p = e^{-\frac{\pi\zeta}{\sqrt{1-\zeta^2}}}$ 解得：

$$\zeta = \frac{|\ln\sigma_p|}{\sqrt{\pi^2 + (\ln\sigma_p)^2}}$$

再由 $t_p = \dfrac{\pi}{\omega_n\sqrt{1-\zeta^2}}$ 解得：

$$\omega_n = \frac{\pi}{t_p\sqrt{1-\zeta^2}}$$

**已知 $t_r$ 和 $\sigma_p$ → 求 $\zeta, \omega_n$**：

先由 $\sigma_p$ 求 $\zeta$（同上），再代入 $t_r$ 公式求 $\omega_n$。

### 3.4 S 平面极点位置与性能指标的关系

```
  Im                   极点位置 → 性能：
   │ jωd               
   │  ● ← 极点        • 实部 -ζω_n  → t_s = 4/(ζω_n)
   │  │               • 虚部 jω_d    → t_p = π/ω_d
   │  │ ω_n           • 极径 ω_n    → 快速性
   │  │               • 角度 θ      → ζ = cosθ → σ_p
   │θ │               
───┼──┼─── Re          σ_p 只与 θ 有关！
   │ -ζω_n
   │
```

**极点运动规律**：
- 极点沿**同一角度线**（$\zeta$ = 常数）：$\sigma_p$ 不变，仅 $\omega_n$ 变化
- 极点沿**同一实部线**（$-\zeta\omega_n$ = 常数）：$t_s$ 不变
- 极点沿**同一极径**（$\omega_n$ = 常数）：$t_p$ 和 $t_r$ 的趋势不变

---

## 四、大作业提示

> 设计控制器，使轮式机器人俯仰角在 0.2 rad 的偏置下，1 秒内稳定到平衡点 ±0.01 rad 附近。

**分析思路**：
1. 被控对象：$J\ddot{\theta} = \frac{1}{2}mgh \cdot \theta + \tau$
2. 偏置 0.2 rad 相当于初始条件 $\theta(0) = 0.2$
3. 要求 1 秒内进入 ±0.01 rad 的误差带 → 相当于 $t_s \leq 1$ s（$\Delta = 0.01/0.2 = 5\%$）
4. 使用 PD 控制，将闭环系统设计为欠阻尼二阶系统
5. 由 $t_s = 3/(\zeta\omega_n) \leq 1 \Rightarrow \zeta\omega_n \geq 3$
6. 选择合适 $\zeta$（如 0.707），确定 $\omega_n$，反求 PD 参数


# Lecture 10 — 控制系统动态性能 Part 2：车辆跟驰控制案例详解

> 对应课件：02_Lecture10_控制系统动态性能_Part2.pdf 第 17–19 页

---

## 一、物理背景与问题陈述

### 场景设定

| 变量 | 含义 |
|---|---|
| 后车（自车） | 需要设计控制器的车辆 |
| 前车 | 以恒定速度 $v^*$ (m/s) 匀速行驶 |
| $p(t)$ | 两车之间的**相对距离** (m)，初始值 $p(0) = 10$ m |
| $v(t)$ | 后车速度 (m/s)，初始 $v(0) = v^*$ |
| $u(t)$ | 后车加速度 (m/s²)，**这是我们要设计的控制量** |

**控制目标**：让后车从前车后方 10 m 处逐渐靠近，最终稳定在 **5 m** 的跟车距离，并且过程中不能靠得太近（最近不能低于 4.5 m，否则有碰撞风险）。

---

## 二、第一步：建立状态空间模型（第 17 页）

### 2.1 定义状态变量

为了将「跟车问题」转化为「调节问题」，定义两个误差状态：

$$\boxed{y(t) = 10 - p(t)} \qquad \boxed{x(t) = v(t) - v^*}$$

- **$y(t)$**：距离误差。当 $p=10$ 时 $y=0$（初始状态）；当 $p=5$ 时 $y=5$（目标状态）
- **$x(t)$**：速度误差。当后车速等于前车速时 $x=0$
- 初始条件：$y(0) = 0,\ x(0) = 0$

### 2.2 推导动力学方程

相对距离的变化率 = 前车速度 − 后车速度：

$$\dot{p}(t) = v^* - v(t)$$

因此：

$$\dot{y}(t) = \frac{d}{dt}[10 - p(t)] = -\dot{p}(t) = -(v^* - v(t)) = v(t) - v^* = x(t)$$

$$\dot{x}(t) = \frac{d}{dt}[v(t) - v^*] = \dot{v}(t) - 0 = u(t)$$

得到**状态方程**：

$$\boxed{\begin{cases} \dot{y}(t) = x(t) \\ \dot{x}(t) = u(t) \end{cases}}$$

这是一个**双积分系统**（从加速度 $u$ 到位置 $y$ 经过两次积分）。

### 2.3 拉普拉斯变换

在零初始条件下（$y(0)=0,\ x(0)=0$）取拉普拉斯变换：

$$\boxed{sY(s) = X(s)} \qquad \boxed{sX(s) = U(s)}$$

等价地：$Y(s) = \dfrac{1}{s^2} U(s)$，即被控对象为一对串联的积分器。

---

## 三、第二步：控制结构与方块图（第 18 页）

### 3.1 控制器结构

采用**串级/全状态反馈**控制结构（内环 + 外环）：

- **外环（位置环）**：$R(s) - Y(s)$ → 比例增益 $K_1$ → 生成内环的参考
- **内环（速度环）**：将 $K_1(R-Y)$ 与 $-X(s)$ 叠加 → 比例增益 $K_2$ → 生成控制量 $U(s)$

对应的 S 域控制律：

$$\boxed{U(s) = K_2\big[K_1(R(s) - Y(s)) - X(s)\big]}$$

其中 $G_1(s) = K_1$，$G_2(s) = K_2$，均为比例控制器。

### 3.2 方块图结构

```
          ┌──┐     ┌─────┐     ┌───┐     ┌───┐
R(s) ──→ ⊕ ──→│K₁│──→  ⊕  ──→│1/s│──→│1/s│──→ Y(s)
         ↑-    └──┘     ↑-     └───┘     └───┘
         │              │                  │
         │   Y(s)       │   K₂ ←── X(s) ←─┘
         └──────────────┘
```

信号流向：
1. 参考输入 $R(s)$ 与输出 $Y(s)$ 比较，产生位置误差
2. 位置误差经 $K_1$ 放大
3. 减去速度状态 $X(s)$ 经 $K_2$ 的反馈量
4. 经 $K_2$ 放大后得到 $U(s)$
5. $U(s)$ 经过两个积分器 $\frac{1}{s^2}$ 得到 $Y(s)$

---

## 四、第三步：闭环传递函数推导（第 19 页）

从方块图出发：

$$Y(s) = \frac{1}{s^2}U(s)$$

$$U(s) = K_2\big[K_1(R(s) - Y(s)) - X(s)\big]$$

$$X(s) = sY(s)$$

代入：

$$s^2Y(s) = K_2\big[K_1(R(s) - Y(s)) - sY(s)\big]$$

$$s^2Y(s) = K_1K_2R(s) - K_1K_2Y(s) - K_2sY(s)$$

$$s^2Y(s) + K_2sY(s) + K_1K_2Y(s) = K_1K_2R(s)$$

$$\boxed{\Phi(s) = \frac{Y(s)}{R(s)} = \frac{K_1K_2}{s^2 + K_2s + K_1K_2}}$$

这是标准的**二阶系统**形式：

$$\Phi(s) = \frac{\omega_n^2}{s^2 + 2\xi\omega_n s + \omega_n^2}$$

**参数对应关系**：

$$\boxed{\omega_n^2 = K_1K_2} \qquad \boxed{2\xi\omega_n = K_2}$$

---

## 五、第四步：性能指标转化（关键！）

### 5.1 确定参考输入与期望输出

期望跟车距离为 5m → $y_{ref} = 10 - 5 = 5$

参考输入取阶跃信号：$r(t) = 5 \cdot 1(t)$

### 5.2 最大超调量约束的由来

$$\sigma_p \leq \frac{10 - 4.5 - 5}{5} \times 100\% = \frac{0.5}{5} \times 100\% = 10\%$$

这个约束的**物理含义**是：
- 期望稳态距离 $p_{ss} = 5$ m
- **最小安全距离** $p_{min} = 4.5$ m（再近就有碰撞风险）
- $y_{max} = 10 - p_{min} = 5.5$
- 超调量 = $(y_{max} - y_{ss})/y_{ss} = (5.5-5)/5 = 10\%$

→ **超调不能超过 10%，否则会撞车！**

### 5.3 调节时间约束

$$\boxed{t_s \leq 2\text{ s}}$$

系统须在 2 秒内收敛到稳态（2% 误差带）。

---

## 六、第五步：从性能指标反推 $\xi$ 和 $\omega_n$

### 6.1 超调量 → $\xi$

欠阻尼二阶系统超调量公式：

$$\sigma_p = e^{-\frac{\pi\xi}{\sqrt{1-\xi^2}}} \leq 0.1$$

$$-\frac{\pi\xi}{\sqrt{1-\xi^2}} \leq \ln(0.1) = -2.3026$$

$$\frac{\pi\xi}{\sqrt{1-\xi^2}} \geq 2.3026$$

$$\frac{\xi}{\sqrt{1-\xi^2}} \geq \frac{2.3026}{\pi} = 0.733$$

两边平方：

$$\frac{\xi^2}{1-\xi^2} \geq 0.537, \quad \xi^2 \geq 0.537 - 0.537\xi^2$$

$$1.537\xi^2 \geq 0.537, \quad \xi^2 \geq 0.349$$

$$\boxed{\xi \geq 0.591}$$

### 6.2 调节时间 → $\xi\omega_n$

采用 2% 误差带公式：

$$t_s = \frac{4}{\xi\omega_n} \leq 2 \quad\Rightarrow\quad \boxed{\xi\omega_n \geq 2}$$

### 6.3 综合两个约束

$$\begin{cases} \xi \geq 0.591 \\ \xi\omega_n \geq 2 \end{cases}$$

工程上选取有裕量的值（课件取 $\xi = 0.7$）：

$$\boxed{\xi = 0.7} \qquad \Rightarrow \qquad \omega_n \geq \frac{2}{0.7} = 2.857 \quad \text{取} \quad \boxed{\omega_n = 3}$$

**验证**：
- $\sigma_p = e^{-\pi \cdot 0.7/\sqrt{1-0.49}} = e^{-3.143} = 4.3\% < 10\%$ ✓
- $t_s = 4/(0.7 \times 3) = 1.9\text{ s} < 2\text{ s}$ ✓

---

## 七、第六步：计算控制器增益

从参数对应关系：

$$\begin{cases} K_2 = 2\xi\omega_n = 2 \times 0.7 \times 3 = \boxed{4.2} \\[6pt] K_1K_2 = \omega_n^2 = 9 \quad\Rightarrow\quad K_1 = \dfrac{9}{4.2} = \boxed{2.14 \approx 2.2} \end{cases}$$

---

## 八、第七步：控制器实现

### S 域（频域）：

$$U(s) = K_2\big[K_1(R(s) - Y(s)) - X(s)\big] = 4.2\big[2.2(R(s) - Y(s)) - X(s)\big]$$

### 时域控制律：

代入 $r(t) = 5$（阶跃后），$y(t) = 10 - p(t)$，$x(t) = v(t) - v^*$：

$$\boxed{u(t) = 4.2 \times \big[2.2 \times (5 - (10 - p(t))) - (v(t) - v^*)\big]}$$

化简：

$$\boxed{u(t) = 4.2 \times \big[2.2 \times (p(t) - 5) - (v(t) - v^*)\big]}$$

### 物理含义：

| 项 | 含义 | 增益 |
|---|---|---|
| $p(t) - 5$ | 距离误差（实际距离 − 期望距离） | $K_1K_2 = 9.24$ |
| $v(t) - v^*$ | 速度误差（自车速度 − 前车速度） | $K_2 = 4.2$ |

这本质是一个 **PD 控制器**：
- **P 项**：根据距离误差调整加速度（距离太远→加速靠近，太近→减速）
- **D 项**：根据相对速度提供阻尼（靠近太快→减速抑制超调）

---

## 九、完整解题脉络总结

```
物理场景 → 状态方程     → 拉氏变换    → 方块图建模
          ẏ=x, ẋ=u       sY=X, sX=U     G₁=K₁, G₂=K₂

  ↓

闭环传函推导           → 性能指标确定     → ξ, ωₙ 反解
K₁K₂/(s²+K₂s+K₁K₂)      σ≤10%, t_s≤2s     ξ≥0.59, ξωₙ≥2

  ↓

选取设计参数           → 计算增益        → 实现控制律
ξ=0.7, ωₙ=3            K₂=4.2, K₁=2.2    u = K₂[K₁(r−y)−x]
```

### 核心思想

> 将物理约束（安全距离、响应速度）转化为二阶系统的时域性能指标（超调量、调节时间），再利用欠阻尼二阶系统的标准公式反解出阻尼比和自然频率，最后匹配闭环传递函数确定控制器参数。

---

## 十、补充：如何从两个微分方程画出控制方块图？

核心思想：**每一个方程对应方块图中的一个"积木块"，逐一画出后按信号关系连接即可。**

---

### 10.1 第 1 步：先画被控对象（两个积分器串联）

两个微分方程经过拉氏变换（零初始条件）为：

$$sY(s) = X(s) \qquad sX(s) = U(s)$$

分别改写为「输出 = 传递函数 × 输入」的形式：

$$X(s) = \frac{1}{s} \cdot U(s) \qquad Y(s) = \frac{1}{s} \cdot X(s)$$

这意味着：
- 第一个方程：$U(s)$ 经过一个积分器 $\frac{1}{s}$ 产生 $X(s)$
- 第二个方程：$X(s)$ 经过一个积分器 $\frac{1}{s}$ 产生 $Y(s)$

画成方块图就是**两个积分器首尾相连**：

```
U(s) ──→ [ 1/s ] ──→ X(s) ──→ [ 1/s ] ──→ Y(s)
```

> 物理含义也很直观：加速度 $U$ 积分一次得速度误差 $X$，再积分一次得距离误差 $Y$。

---

### 10.2 第 2 步：画出控制律

控制律为：

$$U(s) = K_2\big[K_1(R(s) - Y(s)) - X(s)\big]$$

从内到外拆解：

1. **比较点**：$R(s) - Y(s)$ → 画一个求和点 ⊕，$R$ 进正端，$Y$ 进负端
2. **比例放大**：乘 $K_1$ → 画一个 $K_1$ 方块
3. **内环比较点**：$K_1(R-Y)$ 减去 $X(s)$ → 再画一个求和点 ⊕
4. **比例放大**：乘 $K_2$ → 画一个 $K_2$ 方块，输出即为 $U(s)$

单独画出控制器部分：

```
                    ┌──┐
R(s) ──→ ⊕ ──→ [K₁] ──→ ⊕ ──→ [K₂] ──→ U(s)
         ↑-              ↑-
         │               │
         │ Y(s)          │ X(s)
```

---

### 10.3 第 3 步：合二为一

把第 10.1 步的「被控对象」接到第 10.2 步控制器的输出 $U(s)$ 上：

```
                     控制器部分                          被控对象
          ┌──┐     ┌─────┐              ┌───┐     ┌───┐
R(s) ──→ ⊕ ──→│K₁│──→  ⊕  ──→[K₂]──→│1/s│──→│1/s│──→ Y(s)
         ↑-    └──┘     ↑-    (已合并)  └───┘     └───┘
         │              │                  │
         │   Y(s)       │   X(s) ←─────────┘
         └──────────────┘
```

注意两个反馈信号：
- **外环反馈 $Y(s)$**：从最右端引回最左端，构成闭环
- **内环反馈 $X(s)$**：从第一个积分器输出端引出，送到控制器内部的比较点（速度阻尼）

---

### 10.4 总结规律：从方程到方块图的通用方法

| 方程 | 对应方块图元素 |
|------|---------------|
| $sX = U$ → $X = \frac{1}{s}U$ | 一个积分器 $1/s$，输入 $U$，输出 $X$ |
| $sY = X$ → $Y = \frac{1}{s}X$ | 一个积分器 $1/s$，输入 $X$，输出 $Y$ |
| $U = K_2[K_1(R-Y) - X]$ | 两个比例增益 + 两个求和点 + 两条反馈线 |

**通用画图步骤**：

1. 把每个微分方程写成「输出 = 传递函数 × 输入」
2. 为每个传递函数画一个方块
3. 按信号流向把它们串联起来
4. 最后把控制律中的代数运算（比较、求和、放大）加上去
5. 闭环反馈线从输出引回输入
