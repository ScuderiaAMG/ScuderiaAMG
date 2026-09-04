# 自动控制原理II —— 线性离散控制系统（一）

> **来源课件**：discrete-time system_01(1).pdf（共37页）
> **课程信息**：自动控制原理II（Principle of Automatic Control Theory），40学时，闭卷考试；主讲：陈欣星（cxx@hust.edu.cn）

## 参考教材

1. 王永骥、王金城、王敏主编，《自动控制原理》，北京：化学工业出版社，2007
2. 胡寿松主编，《自动控制原理》（第三版），北京：国防工业出版社，1994
3. Benjamin C. Kuo, Farid Golnarghi, *Automatic Control Systems*（第8版），高等教育出版社影印版，2003
4. Richard C. Dorf, Robert H. Bishop, *Modern Control Systems*（第9版），科学出版社影印版，2002

## 第7章 线性离散系统的分析与设计（章节总览）

- 7.1 引言
- 7.2 采样过程与采样定理
- 7.3 信号恢复与零阶保持器
- 7.4 Z变换与Z反变换
- 7.5 离散系统的数学模型
- 7.6 离散系统的动态性能
- 7.7 离散系统的数字控制器设计

---

## 7.1 引言

### 7.1.1 基本概念

- **离散时间系统（Discrete-Time Systems）**：系统中存在一个或多个离散（数字）信号的控制系统。
- **数字系统（Digital System）**：系统中含有一个或多个数字信号。
- 两类离散系统的区分：
  | 类型 | 时间 | 幅值 |
  |------|------|------|
  | 采样数据系统（Sampled data systems） | 离散 | 连续 |
  | 数字系统（Digital systems） | 离散 | 量化 |

- $e^*(t)$：由连续信号 $e(t)$ 经采样得到的采样信号。
- **采样数据系统（Sampled Data System）**：除一个或多个采样操作外，其余部分均为连续的系统。
- 采样数据控制系统的典型结构：

  ```
  e(t) → [采样器 sampler] → e*(t) → [保持器 hold] → [被控对象 plant]
  ```

### 7.1.2 A/D 与 D/A 转换过程

- **A/D（模拟→数字）**：包含两步——
  - **采样（Sampling）**：时间上离散化；
  - **量化（Quantization）**：幅值上量化。
- **D/A（数字→模拟）**：将数字量转换为模拟量输出。

### 7.1.3 计算机控制系统结构

```
          ┌──────────┐    D/A    ┌──────────┐
          │ 数字计算机 │ ───────→ │ 控制对象  │
          └──────────┘          └──────────┘
               ↑                      │
               │                      ↓
              A/D               ┌──────────┐
               └─────────────────│ 测量元件  │
                                 └──────────┘
```

思考题：上述系统中，哪些信号是离散的？哪些是连续的？

### 7.1.4 离散控制系统发展历史

- **DDC**：直接数字控制系统（Direct Digital Control）
- **SCC**：计算机监督控制系统（Surveillance Computer Control System）
- **TDC**：集散控制系统（Total and Distributed Control），如多智能体机器人（multi-agent robots）

### 7.1.5 计算机控制系统的优缺点

**优点**：
1. 计算由软件完成，控制律易于修改；
2. 复杂控制律容易实现；
3. 对噪声的敏感性降低；
4. 一台计算机可完成多任务，利用率高；
5. 可组网实现过程自动化、宏观管理与远程控制。

**缺点**：
1. 采样点之间的信息丢失，同等条件下性能低于连续系统；
2. 需要 A/D、D/A 转换装置。

---

## 7.2 采样过程与采样定理

### 7.2.1 采样过程

- **采样周期**：$T$（相邻两次采样之间的时间间隔）。
- **采样器（Sampler）**：每隔 $T$ 秒闭合一瞬间的开关，将连续信号变为离散信号。
- **采样过程**：连续信号 → 离散信号；
- **保持过程**：离散信号 → 连续信号；
- 采样与保持互为**逆过程**。
- **理想采样条件**：
  1. $\tau \ll T$，采样过程瞬时完成；
  2. 字长足够长，使得 $e^*(kT) = e(kT)$。
- **采样器的分类**：理想采样器、周期采样器、随机采样器等（脉冲调制器 + 载波器）。

### 7.2.2 采样信号的数学模型

**1、理想化假设（5条）**：
1. 采样器可以瞬时接通与断开；
2. 采样器输入/输出信号无误差、无噪声；
3. $\tau \ll T$，即 $\tau \to 0$；
4. 采样器断开期间输出保持恒定；
5. 采样周期 $T$ 为常数。

**2、单位脉冲信号** $\delta(t)$：

$$
\delta(t) =
\begin{cases}
\dfrac{1}{\varepsilon}, & 0 \le t \le \varepsilon \\[4pt]
0, & t < 0 \ \text{或} \ t > \varepsilon
\end{cases}
$$

**3、单位脉冲序列** $\delta_T(t)$：

$$
\delta_T(t) = \sum_{k=-\infty}^{+\infty} \delta(t - kT) = \cdots + \delta(t+T) + \delta(t) + \delta(t-T) + \cdots
$$

**4、采样信号的时域表达式**：

$$
e^*(t) = \sum_{k=-\infty}^{+\infty} e(kT)\,\delta(t - kT)
$$

对实际因果信号（$t \ge 0$）：

$$
e^*(t) = \sum_{k=0}^{+\infty} e(kT)\,\delta(t - kT) = e(t) \cdot \delta_T(t)
$$

> **注意**：$e^*(t) = e(0)\delta(t) + e(T)\delta(t-T) + \cdots$，即采样信号是一串加权的单位脉冲序列；$e^*(t) \ne e(t)$。

### 7.2.3 采样信号的拉氏变换

利用拉氏变换的**实位移定理**（$L[f(t-\tau)] = e^{-\tau s}F(s)$）与**复位移定理**（$L[e^{at}f(t)] = F(s-a)$）：

$$
E^*(s) = L\big[e^*(t)\big] = \sum_{n=0}^{\infty} e(nT)\, e^{-nTs}
$$

**例7-1**：$e(t) = 1(t)$，求 $E^*(s)$。

$$
E^*(s) = \sum_{n=0}^{\infty} 1 \cdot e^{-nTs} = \frac{1}{1 - e^{-Ts}}
$$

**例7-2**：$e(t) = e^{-at}$，求 $E^*(s)$。

$$
E^*(s) = \sum_{n=0}^{\infty} e^{-anT} e^{-nTs} = \frac{1}{1 - e^{-(a+s)T}}
$$

### 7.2.4 采样信号的频谱与香农采样定理

**1、连续信号及其频谱**：设连续信号 $e(t)$ 的幅频特性为 $|E(j\omega)|$，最高频率为 $\omega_{\max}$（有限带宽信号）。

**2、单位脉冲序列的傅里叶级数展开**：

$$
\delta_T(t) = \frac{1}{T}\sum_{k=-\infty}^{+\infty} e^{jk\omega_s t}, \qquad \omega_s = \frac{2\pi}{T}\ \text{（采样角频率）}
$$

**3、采样信号的频谱**：

$$
e^*(t) = e(t) \cdot \delta_T(t) = \frac{1}{T}\sum_{k=-\infty}^{+\infty} e(t)\, e^{jk\omega_s t}
$$

取傅里叶变换（$s \to j\omega$）：

$$
E^*(j\omega) = \frac{1}{T}\sum_{k=-\infty}^{+\infty} E\big[j(\omega + k\omega_s)\big]
$$

即采样信号的频谱是原信号频谱以 $\omega_s$ 为周期、按 $1/T$ 倍幅值**周期延拓**的结果。

**4、频谱不重叠的条件**：若 $\omega_s > 2\omega_{\max}$，则各延拓分量互不重叠，输入信号可以（近似）无失真恢复。

**5、香农采样定理（Shannon's Sampling Theorem）**：

> 设 $x(t)$ 为具有连续傅里叶变换 $X(j\omega) = \int_{-\infty}^{\infty} x(t)e^{-j\omega t}\,dt$ 的连续时间信号，$x^*(t)$ 为其以 $T$ 为周期的等间隔采样。则 $x(t)$ 可以由采样值 $x^*(t)$ **精确重构**，当且仅当
> $$
> X(j\omega) = 0, \qquad \forall\ |\omega| \ge \frac{\pi}{T}
> $$
> 即采样角频率满足 $\ \omega_s \ge 2\omega_{\max}$。

- 若 $\omega_s < 2\omega_{\max}$：频谱发生**混叠（重叠）**，输入信号无法恢复。

**6、非周期信号采样频率的选取**：非周期信号最高频率 $\omega_{\max}$ 为无穷大，工程上按精度定义：

$$
\big|E(j\omega_{\max})\big| = 0.05\,\big|E(0)\big|
$$

**例7-3**：$e(t) = e^{-t}$，按香农采样定理选择采样频率。

- 拉氏变换：$E(s) = \dfrac{1}{s+1}$；
- 傅里叶变换：$E(j\omega) = \dfrac{1}{1 + j\omega}$；
- 幅频特性：$|E(j\omega)| = \dfrac{1}{\sqrt{1 + \omega^2}}$；
- 令 $\dfrac{1}{\sqrt{1+\omega_{\max}^2}} = 0.05 \ \Rightarrow\ \omega_{\max} \approx 20\ \text{rad/s}$；
- 故采样角频率 $\omega_s \ge 2\omega_{\max} = 40\ \text{rad/s}$。

---

## 7.3 信号恢复与零阶保持器

### 7.3.1 信号恢复

- 若满足采样定理，可用**理想滤波器**（图中虚线所示理想低通特性）从采样信号 $x^*(t)$ 中恢复原连续信号 $x(t)$。

### 7.3.2 零阶保持器（Zero-Order Hold, ZOH）

- **定义**：零阶保持器是实际数模转换器（DAC）完成信号重构的数学模型——它把每个采样值**保持一个采样周期**，从而将离散时间信号转换为连续时间信号。
- ZOH 是最常用、最简单的保持滤波器。

```
x*(t) → [ ZOH  Gh(s) ] → xh(t)      （x(t) 为原始信号，xh(t) 为恢复信号）
```

### 7.3.3 ZOH 的传递函数

恢复信号：

$$
x_h(t) = \sum_{k=0}^{\infty} x(kT)\Big[1(t-kT) - 1\big(t-(k+1)T\big)\Big]
$$

两边取拉氏变换：

$$
X_h(s) = \sum_{k=0}^{\infty} x(kT)e^{-kTs} \cdot \frac{1 - e^{-Ts}}{s}
$$

因此 ZOH 的等效传递函数为：

$$
G_h(s) = \frac{X_h(s)}{X^*(s)} = \frac{1 - e^{-Ts}}{s}
$$

对应的时域单位脉冲响应：

$$
g_h(t) = 1(t) - 1(t-T)
$$

### 7.3.4 ZOH 的频率特性分析

令 $s = j\omega$：

$$
G_h(j\omega) = \frac{1 - e^{-j\omega T}}{j\omega}
$$

利用 $e^{jx} - e^{-jx} = 2j\sin x$：

$$
G_h(j\omega) = T \cdot \frac{\sin(\omega T/2)}{\omega T/2} \cdot e^{-j\omega T/2} = T \cdot \mathrm{Sa}\!\left(\frac{\omega T}{2}\right) e^{-j\omega T/2}
$$

令 $\omega_s = \dfrac{2\pi}{T}$，则：

- **幅频特性**：$\big|G_h(j\omega)\big| = T \cdot \left|\mathrm{Sa}\!\left(\dfrac{\omega T}{2}\right)\right| = T \cdot \left|\mathrm{Sa}\!\left(\dfrac{\pi\omega}{\omega_s}\right)\right|$
- **相频特性**：$\angle G_h(j\omega) = -\dfrac{\pi\omega}{\omega_s} = -\dfrac{\omega T}{2}$

### 7.3.5 注意（两个重要结论）

1. **ZOH 不是理想低通滤波器**，滤波后会产生**纹波误差**；
2. 信号经 ZOH 后存在**相位滞后**（滞后角 $\omega T/2$，相当于半个采样周期的延迟）。

---

## 本章知识点小结（考试要点）

1. 离散系统的分类：采样系统（时间离散、幅值连续）与数字系统（时间离散、幅值量化）；A/D = 采样 + 量化。
2. 计算机控制系统的组成（数字计算机、D/A、控制对象、测量元件、A/D）及优缺点。
3. 理想采样条件：$\tau \ll T$（瞬时完成）且字长足够（$e^*(kT)=e(kT)$）。
4. 采样信号的时域表达式：$e^*(t) = \sum_{k=0}^{\infty} e(kT)\delta(t-kT) = e(t)\delta_T(t)$。
5. 采样信号的拉氏变换：$E^*(s) = \sum_{n=0}^{\infty} e(nT)e^{-nTs}$。
6. 采样信号频谱周期延拓：$E^*(j\omega) = \dfrac{1}{T}\sum_{k=-\infty}^{\infty} E[j(\omega+k\omega_s)]$。
7. **香农采样定理**：$\omega_s \ge 2\omega_{\max}$ 时信号可无失真恢复；否则频谱混叠。
8. 非周期信号按工程精度确定 $\omega_{\max}$：$|E(j\omega_{\max})| = 0.05|E(0)|$。
9. ZOH 传递函数：$G_h(s) = \dfrac{1-e^{-Ts}}{s}$；单位脉冲响应 $g_h(t) = 1(t) - 1(t-T)$。
10. ZOH 频率特性：幅频 $T\cdot|\mathrm{Sa}(\omega T/2)|$、相频 $-\omega T/2$；非理想低通（有纹波误差）、有相位滞后。
