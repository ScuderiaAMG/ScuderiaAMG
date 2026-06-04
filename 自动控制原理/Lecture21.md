# 第21讲：相对稳定性（Relative Stability）

---

## 一、相对稳定性的定义

### 1.1 什么是相对稳定性

系统稳定只是"能不能用"的最低要求，但一个稳定的系统如果"差一点就不稳定了"，工程上也是不可接受的。**相对稳定性**衡量的就是系统"离不稳定的边缘有多远"。

| 分析方法 | 衡量方式 |
|---------|---------|
| 时域分析 | 特征根靠近虚轴的远近 |
| 频域分析 | 开环 Nyquist 曲线与 $(-1, j0)$ 点的**接近程度** |

> 通俗理解：稳定只是"及格"，相对稳定性是看你"考了多少分"。离 $(-1, j0)$ 越远，系统越"安全"。

### 1.2 相角裕度 $\gamma$

**剪切频率**（幅值穿越频率）$\omega_c$：开环幅相曲线与**单位圆**的交点对应的频率，即开环幅值等于 1 的频率：

$$|G(j\omega_c)H(j\omega_c)| = 1,\quad 0 \leq \omega_c \leq +\infty$$

**相角裕度**：剪切频率处的相角与 $-180°$ 的差值：

$$\boxed{\gamma = 180° + \varphi(\omega_c)}$$

其中 $\varphi(\omega_c) = \angle G(j\omega_c)H(j\omega_c)$。

> 几何含义：在奈氏曲线上，从 $\omega_c$ 对应的点沿单位圆**顺时针**旋转到负实轴的角度。

**最小相位系统中 $\gamma$ 的含义**：

| $\gamma$ 值 | 含义 |
|:---:|------|
| $\gamma > 0°$ | 系统**可能**稳定（还需进一步判断） |
| $\gamma = 0°$ | 曲线穿过 $(-1, j0)$ 点，**临界稳定** |
| $\gamma < 0°$ | 系统**不稳定** |

> 通俗理解：相角裕度就是"相角还需要再多滞后多少度，系统就会跑到 $(-1, j0)$ 点而变得不稳定"。$\gamma$ 越大，离不稳定越远。

### 1.3 幅值裕度 $K_g$

**相位穿越频率** $\omega_g$：开环幅相曲线与**负实轴**的交点对应的频率，即开环相角等于 $-180°$ 的频率：

$$\angle G(j\omega_g)H(j\omega_g) = -180°,\quad 0 \leq \omega_g \leq +\infty$$

**幅值裕度**：相位穿越频率处开环频率特性幅值的**倒数**：

$$\boxed{K_g = \frac{1}{|G(j\omega_g)H(j\omega_g)|}}$$

用分贝表示：

$$K_g(\text{dB}) = -20\lg|G(j\omega_g)H(j\omega_g)| = -L(\omega_g)$$

> 几何含义：奈氏曲线与负实轴的交点到原点的距离为 $1/K_g$。$K_g$ 表示"开环增益还可以再增大多少倍，才会使曲线刚好经过 $(-1, j0)$ 点"。

**最小相位系统中 $K_g$ 的含义**：

| $K_g$ 值 | 含义 |
|:---:|------|
| $K_g > 1$（$>0$ dB） | 系统**可能**稳定 |
| $K_g = 1$（$=0$ dB） | 曲线穿过 $(-1, j0)$，**临界稳定** |
| $K_g < 1$（$<0$ dB） | 系统**不稳定** |

### 1.4 两个裕度必须同时满足

| 情况 | 稳定？ |
|------|:---:|
| $K_g > 1$ **且** $\gamma > 0°$ | **稳定** |
| $K_g > 1$ 但 $\gamma < 0°$ | 不稳定 |
| $K_g < 1$ 但 $\gamma > 0°$ | 不稳定 |
| $K_g < 1$ **且** $\gamma < 0°$ | 不稳定 |

> **不能仅凭一个裕度判断！** 可能出现 $K_g$ 较大但 $\gamma$ 较小（或反之）的情况。

**工程设计要求**：

$$\gamma = 30° \sim 60°,\quad K_g \geq 2 \text{（即 } K_g \geq 6 \text{ dB）}$$

> 通俗理解：相角裕度和幅值裕度就像两道"保险"——必须两道保险都足够大，系统才算"够安全"。工程上通常要求相角裕度在 30°~60° 之间，幅值裕度至少为 2 倍（6 dB）。

**若有多个交点**：以**最小的**裕度值作为性能指标。

---

## 二、相对稳定性的计算

### 2.1 三种计算方法

| 方法 | 特点 |
|------|------|
| **解析法** | 根据定义直接求解，最精确，但计算复杂 |
| **极坐标图法** | 在幅相曲线上图解，直观简便，但有误差 |
| **Bode 图法** | 在 Bode 图上直接读取，作图方便，应用最广 |

### 2.2 解析法求解步骤

```
① 求剪切频率 ω_c：令 |G(jω_c)H(jω_c)| = 1，解方程
        ↓
② 求相角裕度：γ = 180° + ∠G(jω_c)H(jω_c)
        ↓
③ 求相位穿越频率 ω_g：令 ∠G(jω_g)H(jω_g) = -180°，解方程
        ↓
④ 求幅值裕度：K_g = 1/|G(jω_g)H(jω_g)|
        ↓
⑤ 判断：K_g > 1 且 γ > 0° → 稳定
```

### 2.3 Bode 图法求解

**相角裕度 $\gamma$**：
1. 在对数幅频特性上找到 $L(\omega) = 0$ dB 的频率 $\omega_c$
2. 在对数相频特性上读取 $\varphi(\omega_c)$
3. $\gamma = 180° + \varphi(\omega_c)$

| 相频位置 | $\gamma$ |
|---------|:---:|
| 在 $-180°$ 线**上方** | $\gamma > 0$ |
| 在 $-180°$ 线**下方** | $\gamma < 0$ |

**幅值裕度 $K_g$**：
1. 在对数相频特性上找到 $\varphi(\omega) = -180°$ 的频率 $\omega_g$
2. 在对数幅频特性上读取 $L(\omega_g)$
3. $K_g(\text{dB}) = -L(\omega_g)$

| 幅频位置 | $K_g$ |
|---------|:---:|
| 在 $0$ dB 线**下方** | $K_g > 0$ dB（$K_g > 1$） |
| 在 $0$ dB 线**上方** | $K_g < 0$ dB（$K_g < 1$） |

### 2.4 例1：解析法求裕度

**题目**：已知最小相位系统 $G(s) = \frac{40}{s(s^2+2s+25)}$，求相角裕度和幅值裕度。

**解**：

$$G(j\omega) = \frac{40}{j\omega[(25-\omega^2)+j2\omega]}$$

$$|G(j\omega)| = \frac{40}{\omega\sqrt{(25-\omega^2)^2+4\omega^2}}$$

$$\angle G(j\omega) = \begin{cases} -90° - \arctan\frac{2\omega}{25-\omega^2}, & \omega \leq 5 \\[6pt] -90° - \left(180° - \arctan\frac{2\omega}{\omega^2-25}\right), & \omega > 5 \end{cases}$$

**(1) 求 $\omega_c$**：令 $|G(j\omega_c)| = 1$

$$\frac{40}{\omega_c\sqrt{(25-\omega_c^2)^2+4\omega_c^2}} = 1$$

解得 $\omega_c = 1.82$。

**(2) 求 $\gamma$**：

$$\gamma = 180° + \angle G(j\omega_c) = 180° - 90° - \arctan\frac{2 \times 1.82}{25 - 1.82^2} = 80.5°$$

**(3) 求 $\omega_g$**：令 $\angle G(j\omega_g) = -180°$

$$-90° - \arctan\frac{2\omega_g}{25-\omega_g^2} = -180° \implies \arctan\frac{2\omega_g}{25-\omega_g^2} = 90°$$

$\arctan$ 等于 $90°$ 时分母为零：$25 - \omega_g^2 = 0 \implies \omega_g = 5$。

**(4) 求 $K_g$**：

$$|G(j5)| = \frac{40}{5 \times \sqrt{0 + 100}} = \frac{40}{50} = 0.8$$

$$K_g = \frac{1}{0.8} = 1.25$$

$$K_g(\text{dB}) = -20\lg 0.8 = 1.94 \text{ dB}$$

> **系统稳定**（$K_g = 1.25 > 1$，$\gamma = 80.5° > 0°$），但裕度偏小。

---

### 2.5 例2：Bode 图法求裕度（不同增益对比）

**题目**：已知最小相位系统 $G(s) = \frac{K}{s(s+1)(0.1s+1)}$，分别求 $K=5$ 和 $K=20$ 时的稳定裕度。

**解**：

**Bode 图绘制**：
- 转折频率：$\omega_1 = 1$（惯性），$\omega_2 = 10$（惯性）
- 1 个积分环节，起始段斜率 $-20$ dB/dec

**(1) 求 $\omega_c$**：

$$20\lg K - 20\lg\omega_c - 20\lg\sqrt{1+\omega_c^2} - 20\lg\sqrt{1+0.01\omega_c^2} = 0$$

近似求解（设 $\omega_c$ 在转折频率 1 和 10 之间，该段斜率 $-40$ dB/dec）：

$$20\lg K - 40\lg\omega_c = 0 \implies \omega_c = \sqrt{K}$$

- $K = 5$：$\omega_c \approx \sqrt{5} = 2.24$
- $K = 20$：$\omega_c \approx \sqrt{20} = 4.47$

**(2) 求 $\gamma$**：

$$\gamma = 180° - 90° - \arctan\omega_c - \arctan(0.1\omega_c)$$

- $K = 5$：$\gamma = 90° - \arctan 2.24 - \arctan 0.224 = 90° - 65.9° - 12.7° = 11.4°$
- $K = 20$：$\gamma = 90° - \arctan 4.47 - \arctan 0.447 = 90° - 77.4° - 24.1° = -11.5°$

**(3) 求 $\omega_g$**：

$$\angle G(j\omega_g) = -90° - \arctan\omega_g - \arctan(0.1\omega_g) = -180°$$

$$\arctan\omega_g + \arctan(0.1\omega_g) = 90°$$

利用 $\arctan a + \arctan b = 90°$ 当 $ab = 1$：$\omega_g \times 0.1\omega_g = 1 \implies \omega_g^2 = 10 \implies \omega_g = \sqrt{10} \approx 3.16$

**(4) 求 $K_g$**：

$$|G(j\omega_g)| = \frac{K}{\omega_g\sqrt{1+\omega_g^2}\sqrt{1+0.01\omega_g^2}} = \frac{K}{3.16 \times \sqrt{11} \times \sqrt{1.1}} = \frac{K}{11}$$

- $K = 5$：$K_g = 11/5 = 2.2$，$K_g(\text{dB}) = 6.8$ dB → **稳定**
- $K = 20$：$K_g = 11/20 = 0.55$，$K_g(\text{dB}) = -5.2$ dB → **不稳定**

**精确 $K_g$ 表达式**：

$$K_g(\text{dB}) = -20\lg K + 20\lg\omega_g + 20\lg\sqrt{1+\omega_g^2} + 20\lg\sqrt{1+0.01\omega_g^2}$$

> 用渐近线近似求 $\omega_g$ 时，如果 $\omega_g$ 离转折频率很近，忽略的项会引入误差。

> 通俗理解：$K$ 越大，剪切频率越高（响应越快），但相角裕度越小（越不稳定）。这就是控制系统设计中"快"和"稳"的矛盾。

---

### 2.6 例3：由相角裕度反求 $K$

**题目**：已知 $G(s) = \frac{K}{s(0.5s+1)(0.1s+1)}$，求使相角裕度 $\gamma = 60°$ 的 $K$ 值。

**解**：

$$\varphi(\omega_c) = -90° - \arctan(0.5\omega_c) - \arctan(0.1\omega_c) = \gamma - 180° = -120°$$

即：

$$\arctan(0.5\omega_c) + \arctan(0.1\omega_c) = 30°$$

利用 $\arctan a + \arctan b = \arctan\frac{a+b}{1-ab}$：

$$\arctan\frac{0.6\omega_c}{1-0.05\omega_c^2} = 30° \implies \frac{0.6\omega_c}{1-0.05\omega_c^2} = \tan 30° = \frac{1}{\sqrt{3}}$$

解得 $\omega_c = 0.9214$。

代入幅频条件 $|G(j\omega_c)| = 1$：

$$\frac{K}{\omega_c\sqrt{(0.5\omega_c)^2+1}\sqrt{(0.1\omega_c)^2+1}} = 1$$

$$K = \omega_c\sqrt{1+0.25\omega_c^2}\sqrt{1+0.01\omega_c^2} = 0.9214 \times \sqrt{1.212} \times \sqrt{1.0085} \approx 1.02$$

> **$K = 1.02$ 时，$\gamma = 60°$。**

**对比**：若用渐近线近似求 $\omega_c$：$20\lg K - 20\lg\omega_c = 0 \implies \omega_c = K$，精度较低。

---

### 2.7 例4：含不稳定极点的稳定裕度

**题目**：$G(s) = \frac{K(\tau s+1)}{s(Ts-1)}$，用奈氏判据判断稳定性，并考察与稳定裕度的关系。

**解**：

$$G(j\omega) = \frac{K(1+j\omega\tau)}{j\omega(j\omega T-1)}$$

$$|G(j\omega)| = \frac{K\sqrt{1+\omega^2\tau^2}}{\omega\sqrt{1+\omega^2 T^2}}$$

$$\angle G(j\omega) = -90° + \arctan(\omega\tau) - (180° - \arctan(\omega T)) = -270° + \arctan(\omega\tau) + \arctan(\omega T)$$

**变化趋势**：

| $\omega$ | $\|G\|$ | $\angle G$ |
|:---:|:---:|:---:|
| $0$ | $\infty$ | $-270°$ |
| $\to +\infty$ | $K\tau/T$ | $-90°$ |

**起点渐近线**（实部）：$u(0) = -(T+\tau)$。

**与负实轴交点**：令 $\angle G(j\omega_g) = -180°$

$$\arctan(\omega_g\tau) + \arctan(\omega_g T) = 90° \implies \omega_g\tau \cdot \omega_g T = 1 \implies \omega_g = \frac{1}{\sqrt{\tau T}}$$

代入幅值：

$$|G(j\omega_g)| = \frac{K\sqrt{1+\tau/T}}{(1/\sqrt{\tau T})\sqrt{1+T/\tau}} = K\tau$$

**稳定性判断**（$P = 1$，需 $N = 1$）：

| 条件 | 奈氏曲线行为 | 穿越 | 稳定性 |
|------|------------|------|:---:|
| $K\tau > 1$ | 不包围 $(-1, j0)$ | 1 次正穿越 + 半次负穿越 | **稳定** |
| $K\tau = 1$ | 穿过 $(-1, j0)$ | — | **临界稳定** |
| $K\tau < 1$ | 顺时针包围 | 半次负穿越 | **不稳定** |

**幅值裕度**：

$$K_g = \frac{1}{|G(j\omega_g)|} = \frac{1}{K\tau}$$

> **注意**：这个系统稳定时 $K_g = 1/(K\tau) < 1$（即 $K_g < 0$ dB）！

> 这是一个**反直觉**的例子：对于含不稳定极点的非最小相位系统，**稳定时幅值裕度反而小于 1**。传统的"$K_g > 1$ 且 $\gamma > 0$ 则稳定"的结论只对**最小相位系统**成立。非最小相位系统必须直接由奈氏判据判断。

---

### 2.8 例5：含延迟环节的系统

**题目**：$G(s) = \frac{e^{-\tau s}}{Ts}$，求相角裕度和幅值裕度。

**解**：

$$G(j\omega) = \frac{e^{-j\omega\tau}}{j\omega T}$$

$$|G(j\omega)| = \frac{1}{\omega T},\quad \angle G(j\omega) = -90° - 57.3° \times \omega\tau$$

**(1) 求 $\omega_c$**：令 $|G(j\omega_c)| = 1$

$$\frac{1}{\omega_c T} = 1 \implies \omega_c = \frac{1}{T}$$

**(2) 求 $\gamma$**：

$$\gamma = 180° + \angle G(j\omega_c) = 180° - 90° - 57.3° \times \frac{\tau}{T} = 90° - 57.3° \times \frac{\tau}{T}$$

**(3) 求 $\omega_g$**：令 $\angle G(j\omega_g) = -180°$

$$-90° - 57.3° \times \omega_g\tau = -180° \implies \omega_g = \frac{90°}{57.3° \times \tau} = \frac{\pi}{2\tau} \approx \frac{1.57}{\tau}$$

**(4) 求 $K_g$**：

$$K_g = \frac{1}{|G(j\omega_g)|} = \omega_g T = \frac{1.57T}{\tau}$$

> **$\tau$ 越小，相角裕度和幅值裕度都越大，相对稳定性越好。** 延迟环节只影响相角（使相角更滞后），不影响幅值。

---

## 三、小结

### 3.1 稳定裕度三种解法比较

| 方法 | 优点 | 缺点 |
|------|------|------|
| **解析法** | 最精确 | 计算复杂，需解方程 |
| **Bode 图法** | 直接在图上读取 $\omega_c$ 和 $\omega_g$，作图方便，**应用最广** | 若 $\omega_c$/$\omega_g$ 离转折频率很近，渐近线近似有较大误差 |
| **幅相曲线法** | 图解简便、直观，高阶系统尤为方便 | 有一定误差 |

### 3.2 关键公式速查

| 量 | 定义 | 求解方程 |
|---|------|---------|
| 剪切频率 $\omega_c$ | 开环幅值等于 1 的频率 | $\|G(j\omega_c)H(j\omega_c)\| = 1$ |
| 相角裕度 $\gamma$ | $\omega_c$ 处相角与 $-180°$ 的差 | $\gamma = 180° + \varphi(\omega_c)$ |
| 相位穿越频率 $\omega_g$ | 开环相角等于 $-180°$ 的频率 | $\angle G(j\omega_g)H(j\omega_g) = -180°$ |
| 幅值裕度 $K_g$ | $\omega_g$ 处幅值的倒数 | $K_g = 1/\|G(j\omega_g)H(j\omega_g)\|$ |
| 幅值裕度（dB） | — | $K_g(\text{dB}) = -L(\omega_g)$ |

### 3.3 Bode 图上读取裕度

```
对数幅频特性
│
│  ──────── 0dB ──────────────
│          ↕ ω_c（穿越频率）
│
│  ──────── L(ω_g) ───────────
│                     ↕ ω_g
对数相频特性          ↕ γ = 180° + φ(ω_c)
│
│  ──────── -180° ────────────
│          ↕ ω_c
│                     ↕ ω_g
```

| 在 Bode 图上 | 读取方式 |
|------------|---------|
| $\gamma$ | $\omega_c$ 处相频曲线到 $-180°$ 线的距离 |
| $K_g$（dB） | $\omega_g$ 处幅频曲线到 $0$ dB 线的距离（取反号） |

### 3.4 最小相位系统 vs 非最小相位系统

| 性质 | 最小相位系统 | 非最小相位系统 |
|------|------------|--------------|
| $\gamma > 0°$ 且 $K_g > 1$ | **稳定** | **不一定**（如例4中稳定时 $K_g < 1$） |
| 裕度含义 | 直观可靠 | 需结合奈氏判据具体分析 |
| 设计准则 | $\gamma = 30° \sim 60°$，$K_g \geq 2$ | 不直接适用 |

### 3.5 稳定裕度与系统性能的关系

| 裕度指标 | 对性能的影响 |
|---------|------------|
| $\gamma$ 增大 | 超调量 $\sigma_p$ 减小，响应更平稳 |
| $\gamma$ 过大 | 系统响应过慢（过度保守） |
| $K_g$ 增大 | 系统对增益变化更鲁棒 |
| $\omega_c$ 增大 | 系统响应更快（带宽更大） |

> 工程设计的核心矛盾：**快速性**（$\omega_c$ 大）与**稳定性**（$\gamma$ 大）的权衡。
