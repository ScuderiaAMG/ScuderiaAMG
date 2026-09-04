# 自动控制原理II —— 线性离散控制系统（二）：Z变换与Z反变换

> **来源课件**：discrete-time system_02.pdf（共28页）
> **所属章节**：第7章 线性离散系统的分析与设计（Sampled-data System）——7.4节

## 7.4 Z变换与Z反变换

### 7.4.1 Z变换的定义

由采样信号的拉氏变换

$$
E^*(s) = \sum_{k=0}^{+\infty} e(kT)\, e^{-kTs}
$$

令

$$
z = e^{Ts}, \qquad s = \frac{1}{T}\ln z
$$

则得到 **Z变换** 的定义：

$$
E(z) = \sum_{k=0}^{\infty} e(kT)\, z^{-k}
$$

且

$$
E(z) = E^*(s)\Big|_{e^{Ts} = z}
$$

记法：

$$
E(z) = \mathcal{Z}\big[e(t)\big] = \mathcal{Z}\big[e^*(t)\big] = \mathcal{Z}\big[E^*(s)\big] = \mathcal{Z}\big[E(s)\big]
$$

> **重要说明（Rmk）**：
> 1. **Z变换只适用于离散信号**（$e(t)$ 必须先采样为 $e^*(t)$ 后才能求 Z 变换）；
> 2. $E(z)$ 只对应**唯一的** $e^*(t)$，但**不对应唯一的** $e(t)$（不同连续信号采样后可得到相同的 Z 变换）。

### 7.4.2 求 Z 变换的方法

两种基本方法：
1. **按定义法**（级数求和法）：$E(z) = \sum_{k=0}^{\infty} e(kT) z^{-k}$；
2. **部分分式展开法**：先求拉氏变换 $E(s)$，部分分式展开后逐项查表求 Z 变换。

**例1（定义法）**：$x_1(t) = 1(t)$ 与 $x_2(t) = \delta_T(t) = \sum_{k=0}^{\infty}\delta(t-kT)$，求 $X_1(z)$、$X_2(z)$。

$$
X_1(z) = X_2(z) = 1 + z^{-1} + z^{-2} + \cdots = \frac{1}{1-z^{-1}} = \frac{z}{z-1}
$$

> **提示（Tips）**：虽然 $x_1(t)$ 与 $x_2(t)$ 不是同一信号，但它们可以具有**相同的 Z 变换**。

**例2（定义法）**：$e(t) = \sin\omega t$，求 $E(z)$。

利用欧拉公式 $e^{j\omega t} = \cos\omega t + j\sin\omega t$：

$$
E(z) = \frac{1}{2j}\left[\frac{1}{1 - e^{j\omega T}z^{-1}} - \frac{1}{1 - e^{-j\omega T}z^{-1}}\right] = \frac{z\sin\omega T}{z^2 - 2z\cos\omega T + 1}
$$

> **提示**：$e^{j\omega t} = \cos\omega t + j\sin\omega t$。

**例3（定义法）**：$e(t) = t$，求 $E(z)$。

$$
E(z) = \sum_{k=0}^{\infty} kT\, z^{-k} = -Tz\,\frac{d}{dz}\!\left(\sum_{k=0}^{\infty} z^{-k}\right) = -Tz\,\frac{d}{dz}\!\left(\frac{z}{z-1}\right) = \frac{Tz}{(z-1)^2}
$$

**例4（部分分式法）**：$E(s) = \dfrac{1}{(s+a)(s+b)}$，求 $E(z)$。

$$
E(s) = \frac{1}{b-a}\left(\frac{1}{s+a} - \frac{1}{s+b}\right) \ \Rightarrow\ e(t) = \frac{1}{b-a}\left(e^{-at} - e^{-bt}\right)
$$

$$
E(z) = \frac{1}{b-a}\left(\frac{z}{z - e^{-aT}} - \frac{z}{z - e^{-bT}}\right)
$$

#### 常用函数的 Z 变换表（重点记忆）

| 时域函数 $e(t)$ | Z 变换 $E(z)$ |
|---|---|
| $\delta(t)$ | $1$ |
| $1(t)$ | $\dfrac{z}{z-1}$ |
| $t$ | $\dfrac{Tz}{(z-1)^2}$ |
| $e^{-at}$ | $\dfrac{z}{z-e^{-aT}}$ |
| $te^{-at}$ | $\dfrac{Tz\,e^{-aT}}{(z-e^{-aT})^2}$ |
| $\sin\omega t$ | $\dfrac{z\sin\omega T}{z^2 - 2z\cos\omega T + 1}$ |
| $\cos\omega t$ | $\dfrac{z(z-\cos\omega T)}{z^2 - 2z\cos\omega T + 1}$ |

### 7.4.3 Z 变换的性质

**1. 线性性质**

$$
\mathcal{Z}\big[a\,e_1^*(t) \pm b\,e_2^*(t)\big] = aE_1(z) \pm bE_2(z)
$$

**2. 实位移定理**

① **延时定理（Lag）**：

$$
\mathcal{Z}\big[e(t - nT)\big] = z^{-n}E(z)
$$

证明：令 $j = k - n$，

$$
\text{LHS} = \sum_{k=0}^{\infty} e(kT - nT) z^{-k} = z^{-n}\sum_{j=0}^{\infty} e(jT)z^{-j} = z^{-n}E(z) = \text{RHS}
$$

② **超前定理（Lead）**：

$$
\mathcal{Z}\big[e(t + nT)\big] = z^{n}\left[E(z) - \sum_{k=0}^{n-1} e(kT)\,z^{-k}\right]
$$

**例5/例6（实位移定理应用）**：
- 已知 $\mathcal{Z}[t] = \dfrac{Tz}{(z-1)^2}$，则 $\mathcal{Z}[t - T] = z^{-1}\cdot\dfrac{Tz}{(z-1)^2} = \dfrac{T}{(z-1)^2}$；
- $e(t) = t + 2T$：由超前定理，$\mathcal{Z}[t + 2T] = z^2\left[\dfrac{Tz}{(z-1)^2} - e(0) - e(T)z^{-1}\right]$，其中 $e(0)=0$，$e(T)=T$。

**3. 复位移定理**

$$
\mathcal{Z}\big[e^{\mp at}\, e(t)\big] = E(z \cdot e^{\pm aT})
$$

证明（以 $e(t)e^{-at}$ 为例）：

$$
\text{LHS} = \sum_{k=0}^{\infty} e(kT)\, e^{-akT} z^{-k} = \sum_{k=0}^{\infty} e(kT)\big(z e^{aT}\big)^{-k} = E(z e^{aT}) = \text{RHS}
$$

**例7（复位移定理应用）**：已知 $\mathcal{Z}[t] = \dfrac{Tz}{(z-1)^2}$，则

$$
\mathcal{Z}\big[te^{-at}\big] = E_1(z e^{aT}) = \frac{T z e^{aT}}{(z e^{aT} - 1)^2} = \frac{Tz\,e^{-aT}}{(z - e^{-aT})^2}
$$

**4. 初值定理**

$$
e(0) = \lim_{z\to\infty} E(z)
$$

证明：$E(z) = e(0) + e(T)z^{-1} + e(2T)z^{-2} + \cdots$，令 $z \to \infty$ 即得 $e(0)$。

**例8（初值定理应用）**：$E(z) = \dfrac{0.792z^2}{(z-1)(z^2 - 0.416z + 0.208)}$，则 $e(0) = \lim_{z\to\infty}E(z) = 0$。

**5. 终值定理**

$$
\lim_{n\to\infty} e(nT) = \lim_{z\to 1} (z-1)\,E(z)
$$

（要求 $(z-1)E(z)$ 的极点均位于 z 平面单位圆内，即终值存在。）

**6. 卷积定理**

$$
c^*(t) = e^*(t) * g^*(t) \quad \Longrightarrow \quad C(z) = E(z)\cdot G(z)
$$

> 时域卷积对应 z 域相乘——这是求离散系统闭环响应的重要工具。

### 7.4.4 Z 反变换

- **目的**：由 $E(z)$ 求采样信号 $e^*(t)$。
- **注意**：Z 反变换只能得到离散时间信号 $x^*(t)$，**不能**得到连续信号 $x(t)$。

$$
x(nT) = \mathcal{Z}^{-1}\big[X(z)\big]
$$

三种方法：

1. **长除法**（幂级数展开法）
2. **部分分式展开法**
3. **留数法**（Residue）

#### 1. 长除法

设

$$
E(z) = \frac{b_m z^m + b_{m-1}z^{m-1} + \cdots + b_0}{a_n z^n + a_{n-1}z^{n-1} + \cdots + a_0}
$$

分子除以分母得：

$$
E(z) = c_0 + c_1 z^{-1} + c_2 z^{-2} + \cdots = \sum_{k=0}^{\infty} c_k z^{-k}
$$

则

$$
e^*(t) = c_0\delta(t) + c_1\delta(t-T) + c_2\delta(t-2T) + \cdots
$$

**例题**：$E(z) = \dfrac{10z}{z^2 - 3z + 2} = \dfrac{10z}{(z-1)(z-2)}$，求 $e^*(t)$。

长除得：

$$
E(z) = 10z^{-1} + 30z^{-2} + 70z^{-3} + 150z^{-4} + \cdots
$$

$$
e^*(t) = 10\delta(t-T) + 30\delta(t-2T) + 70\delta(t-3T) + 150\delta(t-4T) + \cdots
$$

**例题**：$F(z) = \dfrac{z}{z^2 - 5z + 6} = \dfrac{z}{(z-2)(z-3)}$，求 $f^*(t)$。

$$
F(z) = z^{-1} + 5z^{-2} + 19z^{-3} + 65z^{-4} + \cdots
$$

$$
f(0) = 0,\quad f(T) = 1,\quad f(2T) = 5,\quad f(3T) = 19,\quad f(4T) = 65,\ \cdots
$$

#### 2. 部分分式展开法

> **注意**：这里展开的是 $\dfrac{X(z)}{z}$，而不是 $X(z)$！

$$
\frac{X(z)}{z} = \sum_{i=1}^{n} \frac{A_i}{z - z_i}
$$

其中系数由下式决定：

$$
A_i = \left[(z - z_i)\frac{X(z)}{z}\right]\Bigg|_{z = z_i}
$$

从而

$$
X(z) = \sum_{i=1}^{n} \frac{A_i\, z}{z - z_i} \quad \overset{\text{查表}}{\Longrightarrow}\quad x(nT) = \sum_{i=1}^{n} A_i\, z_i^{n}
$$

**例题**：$F(z) = \dfrac{z}{(z-1)(z-e^{-T})}$，求 $f^*(t)$。

$$
\frac{F(z)}{z} = \frac{K_1}{z-1} + \frac{K_2}{z-e^{-T}}
$$

$$
K_1 = \lim_{z\to 1}\left[(z-1)\frac{F(z)}{z}\right] = \frac{1}{1-e^{-T}}, \qquad
K_2 = \lim_{z\to e^{-T}}\left[(z-e^{-T})\frac{F(z)}{z}\right] = -\frac{1}{1-e^{-T}}
$$

$$
F(z) = \frac{1}{1-e^{-T}}\left(\frac{z}{z-1} - \frac{z}{z-e^{-T}}\right)
$$

$$
f(nT) = \frac{1 - e^{-nT}}{1 - e^{-T}}
$$

$$
f^*(t) = \sum_{k=0}^{\infty} \frac{1 - e^{-kT}}{1 - e^{-T}}\,\delta(t-kT)
$$

#### 3. 留数法（Residue）

$$
f(kT) = \sum_{i=1}^{n} \text{Res}\big[F(z)\,z^{k-1},\ z_i\big]
$$

其中 $z_i\ (i = 1, 2, \cdots, n)$ 为 $F(z)z^{k-1}$ 的全部极点，$\Gamma$ 为包含全部极点的围线。

- **一阶极点** $z_i$：

$$
\text{Res}\big[F(z)z^{k-1}, z_i\big] = \lim_{z\to z_i}\left[(z - z_i)\,F(z)\,z^{k-1}\right]
$$

- **r 阶极点** $z_i$：

$$
\text{Res}\big[F(z)z^{k-1}, z_i\big] = \frac{1}{(r-1)!}\lim_{z\to z_i} \frac{d^{r-1}}{dz^{r-1}}\Big[(z - z_i)^r F(z)\,z^{k-1}\Big]
$$

**例题**：$F(z) = \dfrac{10z}{(z-1)(z-2)}$，用留数法求 $f(kT)$。

极点为 $z_1 = 1$、$z_2 = 2$：

$$
\text{Res}\big[F(z)z^{k-1}, 1\big] = \lim_{z\to 1}\frac{10z^k}{z-2} = -10
$$

$$
\text{Res}\big[F(z)z^{k-1}, 2\big] = \lim_{z\to 2}\frac{10z^k}{z-1} = 10\cdot 2^k
$$

$$
f(kT) = 10\big(2^k - 1\big), \qquad k = 0, 1, 2, \cdots
$$

**例11（部分分式法与留数法）**：$E(z) = \dfrac{z^2}{(z-0.8)(z-0.1)}$，求 $e^*(t)$。

部分分式展开：

$$
\frac{E(z)}{z} = \frac{C_1}{z-0.8} + \frac{C_2}{z-0.1}, \qquad
C_1 = \lim_{z\to 0.8}\frac{z}{z-0.1} = \frac{8}{7}, \qquad
C_2 = \lim_{z\to 0.1}\frac{z}{z-0.8} = -\frac{1}{7}
$$

$$
E(z) = \frac{8}{7}\cdot\frac{z}{z-0.8} - \frac{1}{7}\cdot\frac{z}{z-0.1}
$$

$$
e(nT) = \frac{8}{7}(0.8)^n - \frac{1}{7}(0.1)^n = \frac{8 \times 0.8^n - 0.1^n}{7}
$$

$$
e^*(t) = \sum_{n=0}^{\infty} \frac{8 \times 0.8^n - 0.1^n}{7}\,\delta(t - nT)
$$

**例12（留数法·二重极点）**：$E(z) = \dfrac{5z}{(z-a)^2}$，求 $e^*(t)$。

极点为二阶极点 $z = a$：

$$
e(nT) = \text{Res}\left[\frac{5z}{(z-a)^2}\cdot z^{n-1},\, a\right] = \frac{1}{(2-1)!}\lim_{z\to a}\frac{d}{dz}\big[5z^{n}\big] = \lim_{z\to a} 5n\, z^{n-1} = 5n\,a^{n-1}
$$

$$
e^*(t) = \sum_{n=0}^{\infty} 5n\,a^{n-1}\,\delta(t - nT)
$$

### 7.4.5 Z 变换的局限性

1. Z 变换**只能反映采样点上的信息**（采样点之间的信息丢失）；
2. 在某些情况下，连续信号在采样点处**可能发生跳变**（z 变换无法反映采样点间的跳变行为）。

---

## 本章知识点小结（考试要点）

1. **Z 变换定义**：$E(z) = \sum_{k=0}^{\infty} e(kT)z^{-k}$，$z = e^{Ts}$；Z 变换只适用于离散信号，且 $E(z)$ 对应唯一的 $e^*(t)$ 但不对应唯一的 $e(t)$。
2. **求 Z 变换的两种方法**：定义法（级数求和）、部分分式展开法（先展 $E(s)$ 再查表）。
3. **必须掌握的常用 Z 变换对**：$\delta(t)\to 1$；$1(t)\to z/(z-1)$；$t \to Tz/(z-1)^2$；$e^{-at}\to z/(z-e^{-aT})$；$\sin\omega t \to \dfrac{z\sin\omega T}{z^2-2z\cos\omega T+1}$。
4. **六大性质**：
   - 线性；
   - 实位移（延时 $z^{-n}E(z)$；超前 $z^n\big[E(z)-\sum_{k=0}^{n-1}e(kT)z^{-k}\big]$）；
   - 复位移（$E(ze^{\pm aT})$）；
   - 初值定理 $e(0)=\lim_{z\to\infty}E(z)$；
   - 终值定理 $e(\infty)=\lim_{z\to1}(z-1)E(z)$；
   - 卷积定理 $C(z)=E(z)G(z)$。
5. **Z 反变换三种方法**：
   - 长除法（得幂级数，逐项对应 $c_k\delta(t-kT)$）；
   - 部分分式展开法（**展开 $X(z)/z$**，系数 $A_i = [(z-z_i)X(z)/z]|_{z=z_i}$）；
   - 留数法：$f(kT) = \sum \text{Res}[F(z)z^{k-1}]$；r 阶极点留数公式 $ \dfrac{1}{(r-1)!}\lim_{z\to z_i}\dfrac{d^{r-1}}{dz^{r-1}}\big[(z-z_i)^rF(z)z^{k-1}\big]$。
6. Z 反变换只能得到离散信号 $x^*(t)$，得不到连续信号 $x(t)$。
7. Z 变换的局限性：只反映采样点信息；采样点处跳变无法反映。
