# 第17讲：开环系统频率特性

---

## 一、频率特性的基本概念

### 1.1 核心思想

在零初始条件下，给系统输入正弦信号 $r(t) = A\sin\omega t$，当频率 $\omega$ 从 $0$ 到 $+\infty$ 连续变化时，考察系统**稳态正弦输出**与正弦输入的**幅值比**和**相位差**随频率变化的规律。

> 通俗理解：给系统"喂"不同频率的正弦波，看输出正弦波的振幅被放大/缩小了多少、相位超前/滞后了多少，把这种关系画成图——这就是频率分析。

### 1.2 稳态输出的推导

设系统传递函数为 $G(s) = \frac{B(s)}{(s-\lambda_1)(s-\lambda_2)\cdots(s-\lambda_n)}$，输入 $r(t) = A\sin\omega t$，则 $R(s) = \frac{A\omega}{s^2+\omega^2}$。

输出为：

$$Y(s) = G(s)R(s) = \frac{B(s)}{(s-\lambda_1)\cdots(s-\lambda_n)} \cdot \frac{A\omega}{s^2+\omega^2}$$

部分分式展开后：

$$Y(s) = \sum_{i=1}^{n}\frac{c_i}{s-\lambda_i} + \frac{d_1}{s+j\omega} + \frac{d_2}{s-j\omega}$$

时域响应：

$$y(t) = \underbrace{\sum_{i=1}^{n} c_i e^{\lambda_i t}}_{\text{瞬态分量}} + \underbrace{d_1 e^{-j\omega t} + d_2 e^{j\omega t}}_{\text{稳态分量}}$$

**如果系统稳定**，所有极点 $\lambda_i$ 均有负实部，当 $t \to \infty$ 时瞬态分量衰减为零，只剩稳态分量：

$$y_{ss}(t) = d_1 e^{-j\omega t} + d_2 e^{j\omega t}$$

### 1.3 求稳态系数 $d_1$、$d_2$

$$d_1 = \left.G(s)\frac{A\omega}{s^2+\omega^2}(s+j\omega)\right|_{s=-j\omega} = \frac{A}{2j}G(-j\omega) \cdot (-1) = -\frac{A}{2j}G(-j\omega)$$

$$d_2 = \left.G(s)\frac{A\omega}{s^2+\omega^2}(s-j\omega)\right|_{s=j\omega} = \frac{A}{2j}G(j\omega)$$

设 $G(j\omega) = |G(j\omega)|e^{j\varphi}$，则 $G(-j\omega) = |G(j\omega)|e^{-j\varphi}$，代入得：

$$y_{ss}(t) = |G(j\omega)| \cdot A \cdot \sin(\omega t + \varphi)$$

### 1.4 核心结论

> **稳定的线性定常系统**在正弦输入作用下，稳态输出是**同频率**的正弦信号，但幅值和相角都发生了改变，这一改变完全由 $G(j\omega)$ 决定。

| 量 | 含义 |
|---|------|
| 幅频特性 $\|G(j\omega)\|$ | 输出与输入的幅值比，随 $\omega$ 变化 |
| 相频特性 $\varphi(\omega) = \angle G(j\omega)$ | 输出相对输入的相位移，随 $\omega$ 变化 |
| 频率特性 $G(j\omega) = \|G(j\omega)\|e^{j\varphi(\omega)}$ | 又称**频率传递函数** |

$$\varphi(\omega) = \angle G(j\omega) = \arctan\frac{\text{Im}[G(j\omega)]}{\text{Re}[G(j\omega)]}$$

> 频率特性也可以理解为：输出的 Fourier 变换与输入的 Fourier 变换之比。

### 1.5 频率特性与传递函数的关系

$$G(j\omega) = G(s)\Big|_{s=j\omega}$$

三者之间的对应关系：

| 微分方程 | 传递函数 | 频率特性 |
|---------|---------|---------|
| $d/dt \to s$ | $G(s)$ | $G(j\omega)$ |
| | $s = j\omega$ | |
| | $d/dt = j\omega$ | |

> 注意：不稳定的系统也可以计算频率特性（数学上存在），但物理上无法通过实验测量。求频率特性**不要求**零初始条件（零初始条件是推导时使用的假设）。

### 1.6 例题：一阶系统的稳态响应

**题目**：求一阶系统 $G(s) = \frac{K}{Ts+1}$（$T>0$）在正弦输入 $r(t) = X\sin\omega t$ 作用下的稳态响应。

**解**：

**(1) 判断稳定性**：极点 $s = -1/T < 0$（$T>0$），系统稳定。

**(2) 求频率特性**：

$$G(j\omega) = \frac{K}{j\omega T + 1}$$

**(3) 求幅频和相频**：

$$|G(j\omega)| = \frac{K}{\sqrt{1+\omega^2 T^2}}$$

$$\varphi(\omega) = \angle G(j\omega) = -\arctan(\omega T)$$

**(4) 稳态响应**：

$$y_{ss}(t) = X \cdot |G(j\omega)| \cdot \sin[\omega t + \varphi(\omega)] = \frac{KX}{\sqrt{1+\omega^2 T^2}} \sin[\omega t - \arctan(\omega T)]$$

> 通俗理解：一阶系统对正弦信号的稳态响应就是把输入振幅乘以一个随频率衰减的系数 $\frac{K}{\sqrt{1+\omega^2 T^2}}$，同时相位滞后 $\arctan(\omega T)$。频率越高，振幅越小，滞后越大。

---

## 二、频率特性法

### 2.1 频率特性法的优势

| 优势 | 说明 |
|------|------|
| 计算量小 | 利用图形分析，避免复杂代数运算 |
| 直观 | 借助图形（幅相曲线、Bode 图）一目了然 |
| 物理意义鲜明 | 直接对应实际系统的频率响应 |
| 适用范围广 | 稳定/不稳定、二阶/高阶/线性系统，可推广到非线性和多变量系统 |
| 工程实用 | 稳定系统可通过实验测出频率特性 |

### 2.2 频率特性的表示方法

#### 2.2.1 解析表达式

**实频特性 $u(\omega)$ 与虚频特性 $v(\omega)$**：

$$G(j\omega) = u(\omega) + jv(\omega)$$

将 $G(j\omega)$ 的分子分母中 $j\omega$ 的偶数次幂构成实部，奇数次幂构成虚部：

$$G(j\omega) = \frac{R_m(\omega) + jI_m(\omega)}{R_d(\omega) + jI_d(\omega)}$$

有理化后：

$$u(\omega) = \frac{R_m R_d + I_m I_d}{R_d^2 + I_d^2},\quad v(\omega) = \frac{I_m R_d - R_m I_d}{R_d^2 + I_d^2}$$

**性质**：
- $u(\omega)$ 是 $\omega$ 的**偶函数**
- $v(\omega)$ 是 $\omega$ 的**奇函数**

**幅频与相频**：

$$|G(j\omega)| = \sqrt{u^2(\omega) + v^2(\omega)}$$

$$\varphi(\omega) = \arctan\frac{v(\omega)}{u(\omega)}$$

#### 2.2.2 几何表示法

**(1) 幅相特性曲线（极坐标图 / Nyquist 图）**

以角频率 $\omega$ 为自变量（$\omega: 0 \to +\infty$），把频率特性的幅值和相角同时表示在复平面上，用箭头表示 $\omega$ 增大方向。

> 因为 $\omega: 0 \to +\infty$ 与 $\omega: -\infty \to 0$ 的幅相曲线关于**实轴对称**，所以只需绘制 $\omega \geq 0$ 的部分。

**串联性质**：多个环节串联时——**幅频相乘，相频相加**：

$$G(j\omega) = G_1(j\omega) \cdot G_2(j\omega)$$

$$|G(j\omega)| = |G_1| \cdot |G_2|,\quad \angle G(j\omega) = \angle G_1 + \angle G_2$$

**(2) 对数频率特性图（Bode 图）**

由两张图组成：

| 图 | 纵坐标 | 横坐标 |
|---|--------|--------|
| 对数幅频特性 | $L(\omega) = 20\lg|G(j\omega)|$（单位 dB，线性分度） | $\omega$（对数分度，单位 rad/s） |
| 对数相频特性 | $\varphi(\omega)$（单位：度） | $\omega$（对数分度） |

> **对数分度**（十倍频程）：频率每扩大 10 倍，横轴变化一个单位长度。因此对 $\omega$ 坐标分度不均匀，对 $\lg\omega$ 是均匀的。

**Bode 图的优势**：
- 横坐标对数分度，**扩宽了低频段**的显示
- 多个环节**串联**时，对数幅频、相频**曲线相加**（变乘法为加法，绘图方便）
- 互为倒数的两个频率特性，Bode 图的幅频和相频**关于横轴对称**（反号）

串联时：

$$L(\omega) = 20\lg|G_1| + 20\lg|G_2|$$

$$\varphi(\omega) = \varphi_1 + \varphi_2$$

互为倒数时（$G_2 = 1/G_1$）：

$$L_2(\omega) = -L_1(\omega),\quad \varphi_2(\omega) = -\varphi_1(\omega)$$

---

## 三、典型环节的频率特性

> 任何传递函数都可以分解为若干**典型环节**的乘积。掌握每个环节的频率特性，就能快速分析任意系统。

### 3.1 典型环节一览

| 序号 | 环节名称 | 传递函数 |
|:---:|---------|---------|
| 1 | 比例环节 | $G(s) = K$ |
| 2 | 积分环节 | $G(s) = 1/s$ |
| 3 | 微分环节 | $G(s) = s$ |
| 4 | 惯性环节 | $G(s) = 1/(Ts+1)$ |
| 5 | 一阶微分环节 | $G(s) = Ts+1$ |
| 6 | 振荡环节 | $G(s) = 1/(T^2s^2+2\zeta Ts+1)$ |
| 7 | 二阶微分环节 | $G(s) = T^2s^2+2\zeta Ts+1$ |
| 8 | 延迟环节 | $G(s) = e^{-\tau s}$ |
| 9 | 不稳定环节 | 极点在右半平面的各类环节 |

### 3.2 比例环节

$G(s) = K$（$K>0$）

| 特性 | 表达式 |
|------|--------|
| 频率特性 | $G(j\omega) = K$ |
| 幅频特性 | $\|G(j\omega)\| = K$ |
| 相频特性 | $\angle G(j\omega) = 0°$ |

**幅相曲线**：复平面上的一个点 $(K, j0)$。

**Bode 图**：
- $L(\omega) = 20\lg K$，水平直线
- $\varphi(\omega) = 0°$

### 3.3 积分环节

$G(s) = \frac{1}{s}$

| 特性 | 表达式 |
|------|--------|
| 频率特性 | $G(j\omega) = \frac{1}{j\omega} = \frac{1}{\omega}e^{-j90°}$ |
| 幅频特性 | $\|G(j\omega)\| = 1/\omega$ |
| 相频特性 | $\varphi(\omega) = -90°$（恒定滞后 90°） |

**幅相曲线**：沿负虚轴，$\omega=0$ 时在无穷远处，$\omega \to +\infty$ 时趋向原点。

**Bode 图**：
- $L(\omega) = -20\lg\omega$，斜率 **$-20$ dB/dec** 的直线，过 $\omega=1$ 时 $L=0$
- $\varphi(\omega) = -90°$，恒定值

> 积分环节是**相角滞后环节**，对正弦输入恒定滞后 90°。

**$v$ 个积分环节串联**：

$$G(s) = \frac{1}{s^v}$$

$$L(\omega) = -20v \cdot \lg\omega,\quad \varphi(\omega) = -90° \times v$$

斜率：$-20v$ dB/dec。

### 3.4 微分环节

$G(s) = s$

| 特性 | 表达式 |
|------|--------|
| 频率特性 | $G(j\omega) = j\omega$ |
| 幅频特性 | $\|G(j\omega)\| = \omega$ |
| 相频特性 | $\varphi(\omega) = +90°$（恒定超前 90°） |

**幅相曲线**：沿正虚轴。

**Bode 图**：
- $L(\omega) = 20\lg\omega$，斜率 **$+20$ dB/dec**
- $\varphi(\omega) = +90°$

> 微分环节与积分环节**互为倒数**，Bode 图关于横轴对称。

### 3.5 惯性环节（一阶滞后环节）

$G(s) = \frac{1}{Ts+1}$

#### 3.5.1 幅相曲线

$$G(j\omega) = \frac{1}{1+j\omega T} = \frac{1-j\omega T}{1+\omega^2 T^2} = \underbrace{\frac{1}{1+\omega^2 T^2}}_{u(\omega)} + j\underbrace{\frac{-\omega T}{1+\omega^2 T^2}}_{v(\omega)}$$

设 $x = u(\omega)$，$y = v(\omega)$，可以证明：

$$\left(x - \frac{1}{2}\right)^2 + y^2 = \left(\frac{1}{2}\right)^2$$

> **幅相曲线是以 $(1/2, j0)$ 为圆心、$1/2$ 为半径的下半圆。**

> 若分子为常数 $K$，则圆心为 $(K/2, j0)$，半径为 $K/2$。

| $\omega$ | $\|G(j\omega)\|$ | $\angle G(j\omega)$ |
|:---:|:---:|:---:|
| $0$ | $1$ | $0°$ |
| $\to +\infty$ | $0$ | $-90°$ |

**相角滞后环节**：相角从 $0°$ 单调减小到 $-90°$。

#### 3.5.2 Bode 图

**对数幅频特性**：

$$L(\omega) = 20\lg|G(j\omega)| = -20\lg\sqrt{1+\omega^2 T^2} = -10\lg(1+\omega^2 T^2)$$

**渐近线近似**：

| 频段 | 条件 | 渐近线 | 斜率 |
|------|------|--------|------|
| 低频 | $\omega \ll 1/T$ | $L(\omega) \approx 0$ dB | 0 |
| 高频 | $\omega \gg 1/T$ | $L(\omega) \approx -20\lg(\omega T)$ | $-20$ dB/dec |

**转折频率**：$\omega = 1/T$，两条渐近线在此相交。

**渐近线误差**：

| 位置 | 误差 |
|------|------|
| $\omega = 1/T$（转折频率处） | $-20\lg\sqrt{2} \approx -3$ dB（最大误差） |
| 距 $1/T$ 等距离处 | 误差相同（误差曲线关于转折频率**对称**） |

**对数相频特性**：

$$\varphi(\omega) = -\arctan(\omega T)$$

| 频段 | $\varphi(\omega)$ |
|------|:---:|
| $\omega \ll 1/T$ | $\to 0°$ |
| $\omega = 1/T$ | $-45°$ |
| $\omega \gg 1/T$ | $\to -90°$ |

**特点**：
- 相频曲线关于点 $(\omega=1/T,\ \varphi=-45°)$ **斜对称**
- 离 $1/T$ 左右等距离的频率，相频之和为 $-90°$：$\varphi(\omega_1) + \varphi(\omega_2) = -90°$
- $T$ 变化时，曲线**形状不变**，只左右平移
- 惯性环节相当于**低通滤波器**：低频信号通过，高频信号被衰减

### 3.6 一阶微分环节（比例微分环节）

$G(s) = Ts + 1$

| 特性 | 表达式 |
|------|--------|
| 幅频特性 | $\|G(j\omega)\| = \sqrt{1+\omega^2 T^2}$ |
| 相频特性 | $\varphi(\omega) = \arctan(\omega T)$ |

**Bode 图**：
- 低频渐近线：$L(\omega) = 0$ dB
- 高频渐近线：$L(\omega) = 20\lg(\omega T)$，斜率 $+20$ dB/dec
- 转折频率：$\omega = 1/T$
- 相频：从 $0°$ 增大到 $+90°$，关于 $(1/T, +45°)$ 斜对称

> **整个对数频率特性曲线与惯性环节关于横轴对称**（因为两者互为倒数）。在转折频率处误差同样为 3 dB。

### 3.7 振荡环节（二阶滞后环节）

$G(s) = \frac{1}{T^2 s^2 + 2\zeta Ts + 1} = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$，其中 $T = 1/\omega_n$

$$G(j\omega) = \frac{1}{(1-\omega^2 T^2) + j2\zeta\omega T}$$

#### 3.7.1 幅相曲线

$$|G(j\omega)| = \frac{1}{\sqrt{(1-\omega^2 T^2)^2 + 4\zeta^2\omega^2 T^2}}$$

$$\angle G(j\omega) = \begin{cases} -\arctan\dfrac{2\zeta\omega T}{1-\omega^2 T^2}, & \omega T \leq 1 \\[8pt] -\left(180° - \arctan\dfrac{2\zeta\omega T}{\omega^2 T^2 - 1}\right), & \omega T > 1 \end{cases}$$

| $\omega$ | $\|G(j\omega)\|$ | $\angle G(j\omega)$ |
|:---:|:---:|:---:|
| $0$ | $1$ | $0°$ |
| $1/T$ | $1/(2\zeta)$ | $-90°$ |
| $\to +\infty$ | $0$ | $-180°$ |

> **相角变化是单调递减的**（可通过求导证明 $\frac{d}{d\omega}\angle G(j\omega) < 0$）。

#### 3.7.2 谐振现象

对 $|G(j\omega)|$ 求导令其为零，当 $0 < \zeta < \frac{1}{\sqrt{2}}$ 时出现谐振：

| 量 | 公式 | 条件 |
|---|------|------|
| **谐振频率** $\omega_r$ | $\omega_r = \frac{1}{T}\sqrt{1-2\zeta^2}$ | $0 < \zeta < \frac{1}{\sqrt{2}}$ |
| **谐振峰值** $M_r$ | $M_r = \frac{1}{2\zeta\sqrt{1-\zeta^2}} > 1$ | $0 < \zeta < \frac{1}{\sqrt{2}}$ |
| **谐振相移** $\varphi_r$ | $\varphi_r = -\arctan\frac{\sqrt{1-2\zeta^2}}{\zeta}$ | |

> 通俗理解：当阻尼比 $\zeta$ 很小时，系统在某个频率 $\omega_r$ 处会产生"共振"——输出振幅被放大到输入的 $M_r$ 倍。$\zeta$ 越小，谐振越剧烈。当 $\zeta \geq 1/\sqrt{2} \approx 0.707$ 时，不产生谐振，幅值单调递减。

#### 3.7.3 Bode 图

**对数幅频特性**：

$$L(\omega) = -20\lg\sqrt{(1-\omega^2 T^2)^2 + 4\zeta^2\omega^2 T^2} = -10\lg[(1-\omega^2 T^2)^2 + 4\zeta^2\omega^2 T^2]$$

**渐近线**：

| 频段 | 条件 | 渐近线 | 斜率 |
|------|------|--------|------|
| 低频 | $\omega \ll 1/T$ | $L(\omega) \approx 0$ dB | 0 |
| 高频 | $\omega \gg 1/T$ | $L(\omega) \approx -40\lg(\omega T)$ | $-40$ dB/dec |

转折频率：$\omega = 1/T$。

**渐近线误差**（精确值减去近似值）：

| 位置 | 误差 |
|------|------|
| $\omega = 1/T$ | $e_L = -20\lg(2\zeta)$ |
| $\zeta = 1$ | $e_L = -6$ dB |
| $\zeta = 0.5$ | $e_L = 0$ dB |
| $\zeta = 0.05$ | $e_L = +20$ dB |

> 误差是阻尼比 $\zeta$ 的函数，且关于转折频率 $1/T$ **对称**。距 $1/T$ 十倍频程以外，误差通常可忽略。

**对数相频特性**：

$$\varphi(\omega) = \begin{cases} -\arctan\dfrac{2\zeta\omega T}{1-\omega^2 T^2}, & \omega T \leq 1 \\[8pt] -\left(180° - \arctan\dfrac{2\zeta\omega T}{\omega^2 T^2 - 1}\right), & \omega T > 1 \end{cases}$$

| 频段 | $\varphi(\omega)$ |
|------|:---:|
| $\omega \ll 1/T$ | $\to 0°$ |
| $\omega = 1/T$ | $-90°$ |
| $\omega \gg 1/T$ | $\to -180°$ |

**相频曲线特点**：
- 关于点 $(\omega=1/T,\ \varphi=-90°)$ **斜对称**
- 离 $1/T$ 左右等距离的频率，相频之和为 $-180°$：$\varphi(\omega_1) + \varphi(\omega_2) = -180°$
- $\zeta$ 越小，曲线在 $1/T$ 处变化速率越大（越陡）
- $T$ 变化时，曲线**形状不变**，只左右平移

### 3.8 二阶微分环节

$G(s) = T^2 s^2 + 2\zeta Ts + 1$

$$G(j\omega) = (1-\omega^2 T^2) + j2\zeta\omega T$$

| $\omega$ | $\|G(j\omega)\|$ | $\angle G(j\omega)$ |
|:---:|:---:|:---:|
| $0$ | $1$ | $0°$ |
| $1/T$ | $2\zeta$ | $+90°$ |
| $\to +\infty$ | $\to +\infty$ | $+180°$ |

**Bode 图**：
- 低频渐近线：$L(\omega) = 0$ dB
- 高频渐近线：$L(\omega) = 40\lg(\omega T)$，斜率 $+40$ dB/dec
- 相频：从 $0°$ 增大到 $+180°$

> **与振荡环节的对数频率特性关于横轴完全对称**（两者互为倒数）。

### 3.9 延迟环节

$G(s) = e^{-\tau s}$

$$G(j\omega) = e^{-j\omega\tau} = \cos(\omega\tau) - j\sin(\omega\tau)$$

| 特性 | 表达式 |
|------|--------|
| 幅频特性 | $\|G(j\omega)\| = 1$（所有频率下幅值不变） |
| 相频特性 | $\varphi(\omega) = -\omega\tau$（弧度）$= -57.3° \times \omega\tau$ |

**幅相曲线**：以原点为圆心、半径为 1 的**单位圆**。

**Bode 图**：
- $L(\omega) = 0$ dB（水平直线）
- $\varphi(\omega) = -\omega\tau$（线性下降，无界）

> 通俗理解：延迟环节不改变振幅，但让相位随频率线性滞后。频率越高，滞后越严重。

### 3.10 不稳定环节

包括不稳定惯性环节、不稳定振荡环节、不稳定一阶微分环节、不稳定二阶微分环节：

| 不稳定环节 | 传递函数 |
|-----------|---------|
| 不稳定惯性 | $G(s) = \frac{1}{-Ts+1}$ 或 $\frac{1}{Ts-1}$ |
| 不稳定振荡 | $G(s) = \frac{1}{T^2s^2-2\zeta Ts+1}$ |
| 不稳定一阶微分 | $G(s) = -Ts+1$ 或 $Ts-1$ |
| 不稳定二阶微分 | $G(s) = T^2s^2-2\zeta Ts+1$ |

> **核心规律**：不稳定环节与对应的稳定环节相比，**幅频特性不变，相频特性不同**。

具体对比（以惯性类为例）：

| 传递函数 | $\|G(j\omega)\|$ | $\angle G(j\omega)$ |
|---------|:---:|------|
| $G_1(s) = \frac{1}{-Ts+1}$ | $\frac{1}{\sqrt{1+\omega^2T^2}}$ | $+\arctan(\omega T)$ |
| $G_2(s) = \frac{1}{Ts-1}$ | $\frac{1}{\sqrt{1+\omega^2T^2}}$ | $-180° + \arctan(\omega T)$ |
| $G_3(s) = \frac{-1}{Ts+1}$ | $\frac{1}{\sqrt{1+\omega^2T^2}}$ | $-180° - \arctan(\omega T)$ |

> $G_1$ 与稳定惯性环节 $\frac{1}{Ts+1}$ 的幅相曲线**关于实轴对称**（相频反号），对数幅频特性相同，相频特性关于横轴对称。

**不稳定振荡环节相频**：

$$G(s) = \frac{1}{T^2s^2-2\zeta Ts+1}$$

$$\angle G(j\omega) = \begin{cases} \arctan\dfrac{2\zeta\omega T}{1-\omega^2 T^2}, & \omega T \leq 1 \\[8pt] 180° - \arctan\dfrac{2\zeta\omega T}{\omega^2 T^2 - 1}, & \omega T > 1 \end{cases}$$

> 原则：单个环节的相角取值范围为 $-180° \sim 180°$。

---

## 四、解题方法总结

### 4.1 求稳态输出的标准步骤

```
① 判断系统稳定性（极点均在左半平面 → 稳定）
      ↓
② 求频率特性 G(jω)：将 s = jω 代入传函
      ↓
③ 求幅频 |G(jω)| 和相频 ∠G(jω)
      ↓
④ 写出稳态输出：
   y_ss(t) = |G(jω)| · A · sin[ωt + ∠G(jω)]
```

### 4.2 绘制典型环节 Bode 图的速查表

| 环节 | 低频渐近线 | 高频渐近线斜率 | 转折频率 | 相频范围 |
|------|-----------|:---:|:---:|------|
| 比例 $K$ | $20\lg K$ dB | 0 | 无 | $0°$ |
| 积分 $1/s^v$ | 过 $\omega=1$ 的直线 | $-20v$ dB/dec | 无 | $-90° \times v$ |
| 微分 $s$ | 过 $\omega=1$ 的直线 | $+20$ dB/dec | 无 | $+90°$ |
| 惯性 $\frac{1}{Ts+1}$ | $0$ dB | $-20$ dB/dec | $1/T$ | $0° \to -90°$ |
| 一阶微分 $Ts+1$ | $0$ dB | $+20$ dB/dec | $1/T$ | $0° \to +90°$ |
| 振荡 $\frac{1}{T^2s^2+2\zeta Ts+1}$ | $0$ dB | $-40$ dB/dec | $1/T$ | $0° \to -180°$ |
| 二阶微分 $T^2s^2+2\zeta Ts+1$ | $0$ dB | $+40$ dB/dec | $1/T$ | $0° \to +180°$ |
| 延迟 $e^{-\tau s}$ | $0$ dB | 0 | 无 | $-\omega\tau$（线性下降） |

### 4.3 振荡环节关键公式速查

| 量 | 公式 | 条件 |
|---|------|------|
| 谐振频率 $\omega_r$ | $\frac{1}{T}\sqrt{1-2\zeta^2}$ | $0 < \zeta < \frac{1}{\sqrt{2}}$ |
| 谐振峰值 $M_r$ | $\frac{1}{2\zeta\sqrt{1-\zeta^2}}$ | $0 < \zeta < \frac{1}{\sqrt{2}}$ |
| 转折频率处误差 | $-20\lg(2\zeta)$ dB | — |
| 转折频率处幅值 | $\frac{1}{2\zeta}$ | — |

### 4.4 对称性规律速查

| 对称关系 | 说明 |
|---------|------|
| 惯性 ↔ 一阶微分 | Bode 图关于**横轴**对称（互为倒数） |
| 振荡 ↔ 二阶微分 | Bode 图关于**横轴**对称（互为倒数） |
| 积分 ↔ 微分 | Bode 图关于**横轴**对称（互为倒数） |
| 稳定环节 ↔ 不稳定环节 | **幅频相同**，相频不同 |
| 惯性环节幅相曲线 | 以 $(1/2, j0)$ 为圆心、$1/2$ 为半径的**下半圆** |
| 延迟环节幅相曲线 | **单位圆** |

### 4.5 相频对称性规律

| 环节 | 对称中心 | 性质 |
|------|---------|------|
| 惯性 | $(1/T,\ -45°)$ | 离 $1/T$ 等距的频率，$\varphi_1 + \varphi_2 = -90°$ |
| 振荡 | $(1/T,\ -90°)$ | 离 $1/T$ 等距的频率，$\varphi_1 + \varphi_2 = -180°$ |

### 4.6 串联环节的频率特性

$$G(j\omega) = \prod_{i=1}^{N} G_i(j\omega)$$

| 域 | 运算 |
|---|------|
| 幅值 | $\|G\| = \prod \|G_i\|$（相乘） |
| 相角 | $\angle G = \sum \angle G_i$（相加） |
| 对数幅频 | $L(\omega) = \sum L_i(\omega)$（相加，dB） |
| 对数相频 | $\varphi(\omega) = \sum \varphi_i(\omega)$（相加） |

> 这就是 Bode 图最大的优势：把乘法变成加法，绘图时只需把各环节的曲线叠加即可。
