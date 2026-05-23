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
