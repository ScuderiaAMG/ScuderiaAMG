# 第27讲：期望频率特性法校正

---

## 四、期望频率特性法校正

### 4.1 校正思想

期望频率特性法的核心思路：**将性能指标要求转化为期望的对数幅频特性，再与原系统的频率特性进行比较，从而得出校正装置的形式和参数。**

> 通俗语言：前面讲的超前/滞后/超前-滞后校正，都是先选定一种固定结构的校正装置，再去调参数。期望频率特性法反过来——先不管校正装置长什么样，直接根据性能要求"画"出一条理想的开环 Bode 图，然后用这条理想曲线减去原系统的 Bode 图，差值就是校正装置应该提供的。最后再根据差值去实现校正装置。

**优缺点：**

| 优点 | 缺点 |
|------|------|
| 方法简单、直观 | **仅适用于最小相位系统** |
| 适合**任何形式**的校正装置 | 只有最小相位系统的幅频和相频之间有确定关系 |
| 可直接从 Bode 图上"读"出校正装置 | — |

> 为什么只适用于最小相位系统？因为对于最小相位系统，对数幅频特性 $L(\omega)$ 和对数相频特性 $\varphi(\omega)$ 之间存在**唯一对应关系**（通过 Hilbert 变换联系），知道了幅频特性就能确定相频特性。非最小相位系统则不具备这一性质。

---

### 4.2 基本原理

设希望开环频率特性为 $G_K(j\omega)$，原系统的开环频率特性为 $G_0(j\omega)$，串联校正装置的频率特性为 $G_c(j\omega)$。

串联校正的结构：

$$R(s) \xrightarrow{\quad} G_c(s) \xrightarrow{\quad} G_0(s) \xrightarrow{\quad} C(s)$$

则有：

$$G_K(j\omega) = G_0(j\omega) \cdot G_c(j\omega)$$

$$G_c(j\omega) = \frac{G_K(j\omega)}{G_0(j\omega)}$$

对应的对数幅频特性：

$$\boxed{L_c(\omega) = L_K(\omega) - L_0(\omega)}$$

> 通俗语言：在 Bode 图上，校正装置的对数幅频特性 = 期望的对数幅频特性 - 原系统的对数幅频特性。这就是"做减法"的思想——画好期望曲线，减去原系统曲线，差值就是校正装置需要提供的增益变化。

**求解思路：**

1. 根据性能指标画出**期望开环对数幅频特性** $L_K(\omega)$
2. 在同一张图上画出**原系统对数幅频特性** $L_0(\omega)$
3. 两条曲线**相减**，得到 $L_c(\omega)$
4. 由 $L_c(\omega)$ 的形状确定校正装置的**传递函数** $G_c(s)$

---

### 4.3 典型的期望频率特性 — 2-1-2 型

通常具有较好性能时，期望频率特性呈现 **"2-1-2"型**，即 Bode 图的斜率依次为：

$$-40 \text{ dB/dec} \xrightarrow{\omega_2} -20 \text{ dB/dec} \xrightarrow{\omega_3} -40 \text{ dB/dec}$$

其中：
- **$-40$**：低频段斜率（由系统型别决定，II 型系统为 $-40$）
- **$-20$**：中频段斜率（保证足够的相角裕度）
- **$-40$**：高频段斜率（保证高频衰减，抑制噪声）

**期望开环传递函数（2-1-2 型）：**

$$\boxed{G(s) = \frac{K\left(\dfrac{1}{\omega_2}s + 1\right)}{s^2\left(\dfrac{1}{\omega_3}s + 1\right)}}$$

其中 $\omega_2 < \omega_3$，剪切频率为 $\omega_c^*$。

**相角裕度：**

$$\gamma(\omega_c^*) = 180^\circ + \varphi(\omega)\Big|_{\omega = \omega_c^*} = \arctan\frac{\omega_c^*}{\omega_2} - \arctan\frac{\omega_c^*}{\omega_3}$$

---

### 4.4 由 $\omega_c^*$、$\gamma^*$ 确定参数 $\omega_2$、$\omega_3$

#### 4.4.1 最大相角裕度

对 $\gamma$ 求极值，令 $\dfrac{d\gamma}{d\omega} = 0$，可求出达到**最大相角裕度**时的角频率：

$$\boxed{\omega_m = \sqrt{\omega_2 \cdot \omega_3}}$$

> 通俗语言：$\omega_m$ 是两个转折频率 $\omega_2$ 和 $\omega_3$ 的**几何中心**（在对数坐标下正好是中频段 $-20$ dB/dec 线段的正中间位置）。

此时最大相角裕度满足：

$$\tan\gamma(\omega_m) = \frac{\omega_3 - \omega_2}{2\sqrt{\omega_2 \omega_3}}$$

$$\boxed{\sin\gamma(\omega_m) = \frac{\omega_3 - \omega_2}{\omega_3 + \omega_2}}$$

#### 4.4.2 引入中频段宽度 $H$

令斜率为 $-20$ dB/dec 的中频段宽度为 $H$：

$$\boxed{H = \frac{\omega_3}{\omega_2}}$$

则最大相角裕度可表示为：

$$\boxed{\sin\gamma(\omega_m) = \frac{H - 1}{H + 1}}$$

> 通俗语言：$H$ 越大（即中频段越宽），相角裕度 $\gamma$ 越大。但 $H$ 不能无限大，否则校正装置会过于复杂。

**近似关系**：通常在极大值附近相角变化较小，因此近似有：

$$\gamma(\omega_m) \approx \gamma(\omega_c^*)$$

结合谐振峰值 $M_r$ 与相角裕度之间的近似关系 $M_r \approx \dfrac{1}{\sin\gamma}$，可得：

$$\boxed{M_r = \frac{H + 1}{H - 1}} \quad \Longleftrightarrow \quad \boxed{H = \frac{M_r + 1}{M_r - 1}}$$

---

### 4.5 由 $\omega_c^*$、$M_r$ 确定参数 $\omega_2$、$\omega_3$

#### 4.5.1 利用等 $M$ 圆确定 $|G(j\omega_m)|$

在开环幅相曲线（Nyquist 图）上做等 $M$ 圆：

- 等 $M$ 圆的半径：$\dfrac{M}{M^2 - 1}$
- 等 $M$ 圆的圆心：$\left(-\dfrac{M^2}{M^2 - 1},\ j0\right)$

与 $G(j\omega)$ 幅相曲线**相切**的等 $M$ 圆的 $M$ 值即为闭环幅频特性的最大值 $M_r$（$M > 1$ 时）。

由勾股定理得：

$$|G(j\omega_m)| = \sqrt{\frac{M_r^4}{(M_r^2 - 1)^2} - \frac{M_r^2}{(M_r^2 - 1)^2}} = \frac{M_r}{\sqrt{M_r^2 - 1}}$$

#### 4.5.2 建立 $\omega_c^*$ 与 $\omega_m$ 的关系

由 Bode 图几何关系（$-20$ dB/dec 线段过 $\omega_c^*$ 时幅值为 0 dB）：

$$0 - 20\lg\frac{\omega_m}{\omega_c^*} = 20\lg|G(j\omega_m)|$$

$$\frac{\omega_c^*}{\omega_m} = |G(j\omega_m)| = \frac{M_r}{\sqrt{M_r^2 - 1}}$$

即：

$$\boxed{\omega_c^* = \omega_m \cdot \frac{M_r}{\sqrt{M_r^2 - 1}} = \sqrt{\omega_2 \omega_3} \cdot \frac{M_r}{\sqrt{M_r^2 - 1}}}$$

#### 4.5.3 最终公式

联立 $\omega_m = \sqrt{\omega_2 \omega_3}$、$H = \dfrac{\omega_3}{\omega_2}$ 和上式，解出：

$$\boxed{\omega_2 \leq \omega_c^* \cdot \frac{M_r - 1}{M_r}}$$

$$\boxed{\omega_3 \geq \omega_c^* \cdot \frac{M_r + 1}{M_r}}$$

> **注意**：这里取 "$\leq$" 和 "$\geq$"，是因为 $H$ 越大 $\gamma$ 越大，为了**保证**相角裕度不低于要求值，需要中频段**足够宽**。

**等价形式**（用 $H$ 表示）：

$$\omega_2 = \frac{{\omega_c^*}^2}{H + 1}, \quad \omega_3 = \frac{{\omega_c^*}^2 \cdot H}{H + 1}$$

---

### 4.6 关键公式汇总

| 符号 | 公式 | 含义 |
|------|------|------|
| $\omega_m$ | $\sqrt{\omega_2 \omega_3}$ | 最大相角裕度对应的频率 |
| $H$ | $\dfrac{\omega_3}{\omega_2}$ | 中频段宽度 |
| $\sin\gamma(\omega_m)$ | $\dfrac{H-1}{H+1}$ | 最大相角裕度 |
| $M_r$ | $\dfrac{H+1}{H-1}$ | 谐振峰值 |
| $\omega_2$ 上限 | $\omega_c^* \cdot \dfrac{M_r - 1}{M_r}$ | 保证 $M_r$ 要求 |
| $\omega_3$ 下限 | $\omega_c^* \cdot \dfrac{M_r + 1}{M_r}$ | 保证 $M_r$ 要求 |

---

### 4.7 期望频率特性法的完整设计步骤

```
步骤 1：确定开环增益 K（低频段）
   ↓  根据稳态误差要求确定 K，绘制起始段
步骤 2：确定中频段参数
   ↓  由 ωc*、γ*（或 Mr）确定 H、ω2、ω3
   ↓  在 ωc* 处作斜率为 -20 dB/dec 的直线
步骤 3：连接低频段
   ↓  中频段向左延伸，与起始段连接
   ↓  若不能直接相连，增加过渡直线（斜率尽量接近相邻线段）
步骤 4：确定高频段
   ↓  中频段向右延伸，根据幅值裕度及抗干扰要求确定
   ↓  斜率尽量与原系统高频段保持一致，或完全重合
步骤 5：求校正装置
   ↓  Lc(ω) = LK(ω) - L0(ω)
   ↓  由 Lc(ω) 的形状确定 Gc(s)
步骤 6：验算
   ↓  计算校正后系统的各项性能指标，确认满足要求
```

> **重要说明**：上述步骤得到的期望频率特性曲线**不一定**是标准的 2-1-2 型。根据原系统的不同，可能是 2-1-3 型、1-2-1-2 型等。

---

### 4.8 典型例题

---

#### 例4.1：I 型系统串联校正设计（2-1-2 型期望特性）

**题目**：已知单位反馈系统开环传递函数 $G_0(s) = \dfrac{K}{s(0.12s + 1)(0.02s + 1)}$，设计串联校正装置，使系统满足：

1. 稳态速度误差系数 $K_v^* \geq 70 \text{ s}^{-1}$
2. 调整时间 $t_s^* \leq 1 \text{ s}$
3. 超调量 $\sigma_p^* \leq 40\%$

---

**【解】**

**第 1 步：确定开环增益 $K$，绘制原系统 Bode 图**

由 $K_v^* \geq 70$，取 $K = 70$。

原系统 $G_0(s) = \dfrac{70}{s(0.12s + 1)(0.02s + 1)}$

转折频率：
- $\omega_{a} = \dfrac{1}{0.12} = 8.33$ rad/s
- $\omega_{b} = \dfrac{1}{0.02} = 50$ rad/s

求原系统剪切频率 $\omega_{c0}$：

在 $\omega_{a} < \omega < \omega_{b}$ 段（斜率 $-40$ dB/dec）：

$$20\lg K - 20\lg\frac{1}{0.12} - 40\lg\frac{\omega_{c0}}{1/0.12} = 0$$

$$20\lg 70 - 20\lg 8.33 - 40\lg\frac{\omega_{c0}}{8.33} = 0$$

$$36.9 - 18.4 - 40\lg\frac{\omega_{c0}}{8.33} = 0$$

$$40\lg\frac{\omega_{c0}}{8.33} = 18.5 \implies \lg\frac{\omega_{c0}}{8.33} = 0.4625 \implies \frac{\omega_{c0}}{8.33} = 2.90$$

$$\omega_{c0} = 24.15 \text{ rad/s}$$

> 原系统剪切频率太高，相角裕度不足（甚至为负），需要校正。

**第 2 步：时域指标转换为频域指标**

利用经验公式：

$$\sigma_p^* = 0.16 + 0.4(M_r - 1) \implies 0.40 \geq 0.16 + 0.4(M_r - 1)$$

$$M_r - 1 \leq 0.6 \implies M_r \leq 1.6$$

$$t_s^* = \frac{\pi}{\omega_c^*}\left[2 + 1.5(M_r - 1) + 2.5(M_r - 1)^2\right] \leq 1$$

取 $M_r = 1.6$，代入：

$$\frac{\pi}{\omega_c^*}\left[2 + 1.5 \times 0.6 + 2.5 \times 0.36\right] \leq 1$$

$$\frac{\pi}{\omega_c^*} \times 3.8 \leq 1 \implies \omega_c^* \geq \frac{3.8\pi}{1} = 11.94$$

取 $M_r = 1.6$，$\omega_c^* = 13$ rad/s。

**第 3 步：确定中频段参数 $\omega_2$、$\omega_3$**

由公式：

$$\omega_2 \leq \omega_c^* \cdot \frac{M_r - 1}{M_r} = 13 \times \frac{0.6}{1.6} = 4.88 \text{ rad/s}$$

$$\omega_3 \geq \omega_c^* \cdot \frac{M_r + 1}{M_r} = 13 \times \frac{2.6}{1.6} = 21.13 \text{ rad/s}$$

在 $\omega_c^* = 13$ 处作斜率为 $-20$ dB/dec 的直线，求与原系统 $20\lg|G_0|$ 的交点。

交点在 $\omega_{a} = 8.33$ 和 $\omega_{b} = 50$ 之间（原系统斜率 $-40$ dB/dec），由：

$$0 - 40\lg\frac{\omega}{\omega_{c0}} = 0 - 20\lg\frac{\omega}{\omega_c^*}$$

$$-40\lg\frac{\omega}{24.15} = -20\lg\frac{\omega}{13}$$

$$2\lg\frac{\omega}{24.15} = \lg\frac{\omega}{13}$$

$$\left(\frac{\omega}{24.15}\right)^2 = \frac{\omega}{13}$$

$$\omega = \frac{24.15^2}{13} = \frac{583.2}{13} = 44.9 \approx 45 \text{ rad/s}$$

为使期望频率特性尽量简单，取 $\omega_3 = 45$（满足 $\omega_3 \geq 21.13$）。

取 $\omega_2 = 4$（满足 $\omega_2 \leq 4.88$）。

此时：

$$H = \frac{\omega_3}{\omega_2} = \frac{45}{4} = 11.25$$

$$\gamma = \arcsin\frac{H - 1}{H + 1} = \arcsin\frac{10.25}{12.25} = \arcsin 0.837 = 56.8^\circ$$

**第 4 步：连接低频段**

为连接中频段（$\omega_2 = 4$）和低频段，在 $\omega_2 = 4$ 的对数幅频值处，作斜率为 $-40$ dB/dec 的直线，求与低频段（斜率 $-20$ dB/dec）的交点。

在 $\omega_2 = 4$ 处的期望幅频值（沿 $-20$ dB/dec 从 $\omega_c^*$ 回推）：

$$L(\omega_2) = 0 - 20\lg\frac{\omega_2}{\omega_c^*} = -20\lg\frac{4}{13} = 20\lg\frac{13}{4} = 10.2 \text{ dB}$$

从 $\omega_2 = 4$ 以 $-40$ dB/dec 向左延伸，与低频段（$-20$ dB/dec，经过 $\omega = 1$ 时幅值为 $20\lg K = 36.9$ dB）的交点：

$$20\lg K - 20\lg\omega_1 = 0 - 20\lg\frac{\omega_2}{\omega_c^*} - 40\lg\frac{\omega_1}{\omega_2}$$

$$36.9 - 20\lg\omega_1 = 10.2 - 40\lg\frac{\omega_1}{4}$$

$$36.9 - 20\lg\omega_1 = 10.2 - 40\lg\omega_1 + 40\lg 4$$

$$36.9 - 20\lg\omega_1 = 10.2 - 40\lg\omega_1 + 24.1$$

$$20\lg\omega_1 = -2.8 \implies \omega_1 = 10^{-0.14} = 0.75 \text{ rad/s}$$

> 交点 $\omega_1 = 0.75$ rad/s，即在 $\omega_1$ 处斜率从 $-20$ dB/dec 变为 $-40$ dB/dec。

**第 5 步：确定高频段**

在中频段 $\omega_3 = 45$ 的对数幅频值处，作斜率为 $-40$ dB/dec 的直线。

$\omega > \omega_3$ 时，取期望特性高频段与原系统高频特性一致（斜率均为 $-40$ dB/dec，到 $\omega_4 = 50$ 变为 $-60$ dB/dec）。

**第 6 步：确定期望频率特性参数**

综合以上结果，期望频率特性 $20\lg|G_K|$ 的转折频率为：

| 转折频率 | 值 (rad/s) | 斜率变化 |
|----------|-----------|---------|
| $\omega_1$ | 0.75 | $-20 \to -40$ dB/dec |
| $\omega_2$ | 4 | $-40 \to -20$ dB/dec |
| $\omega_3$ | 45 | $-20 \to -40$ dB/dec |
| $\omega_4$ | 50 | $-40 \to -60$ dB/dec |

剪切频率 $\omega_c^* = 13$ rad/s。

期望特性为 **2-1-2 型**（低频段与原系统重合，高频段与原系统重合）。

**第 7 步：求校正装置 $G_c(s)$**

期望开环传递函数：

$$G_K(s) = \frac{70\left(\dfrac{1}{4}s + 1\right)\left(\dfrac{1}{8.33}s + 1\right)}{s^2\left(\dfrac{1}{0.75}s + 1\right)\left(\dfrac{1}{45}s + 1\right)\left(\dfrac{1}{50}s + 1\right)}$$

> 说明：分子中加入 $\left(\dfrac{1}{8.33}s + 1\right)$ 是因为原系统在此处有一个极点，期望特性在低频段与原系统重合，因此保留了此极点。

原系统开环传递函数：

$$G_0(s) = \frac{70}{s\left(\dfrac{1}{8.33}s + 1\right)\left(\dfrac{1}{50}s + 1\right)}$$

校正装置：

$$G_c(s) = \frac{G_K(s)}{G_0(s)}$$

将 $G_0(s)$ 改写为与 $G_K(s)$ 相同的形式：

$$G_0(s) = \frac{70 \cdot s \cdot \left(\dfrac{1}{0.75}s + 1\right)\left(\dfrac{1}{45}s + 1\right)\left(\dfrac{1}{50}s + 1\right)}{s^2\left(\dfrac{1}{0.75}s + 1\right)\left(\dfrac{1}{45}s + 1\right)\left(\dfrac{1}{50}s + 1\right)\left(\dfrac{1}{8.33}s + 1\right)\left(\dfrac{1}{50}s + 1\right)} \times G_0$$

更直接地，逐项相除：

- $G_K$ 有零点：$\omega_2 = 4$、$\omega_a = 8.33$（保留原系统极点为期望特性零点）
- $G_K$ 有极点：$\omega_1 = 0.75$、$\omega_3 = 45$、$\omega_4 = 50$
- $G_0$ 有极点：$\omega_a = 8.33$、$\omega_b = 50$

$$G_c(s) = \frac{\left(\dfrac{s}{4} + 1\right)\left(\dfrac{s}{8.33} + 1\right)}{\left(\dfrac{s}{0.75} + 1\right)\left(\dfrac{s}{45} + 1\right)} \cdot \frac{1}{\left(\dfrac{s}{8.33} + 1\right)} \cdot \frac{\dfrac{s}{50} + 1}{\dfrac{s}{50} + 1} \cdot \frac{1}{1}$$

化简（注意 $\omega_a = 8.33$ 处原系统的极点既出现在期望特性的分子也出现在分母中，校正装置需要"消除"它）：

$$G_c(s) = \frac{\left(\dfrac{s}{4} + 1\right)\left(\dfrac{s}{8.33} + 1\right)}{\left(\dfrac{s}{0.75} + 1\right)\left(\dfrac{s}{45} + 1\right)}$$

代入具体数值：$\dfrac{1}{4} = 0.25$，$\dfrac{1}{8.33} = 0.12$，$\dfrac{1}{0.75} = 1.33$，$\dfrac{1}{45} = 0.022$。

$$\boxed{G_c(s) = \frac{(0.25s + 1)(0.12s + 1)}{(1.33s + 1)(0.022s + 1)}}$$

> 校正装置是一个**滞后-超前**网络：$(0.25s+1)/(1.33s+1)$ 为滞后部分（低频提升），$(0.12s+1)/(0.022s+1)$ 为超前部分（高频补偿）。

**第 8 步：验算**

校正后系统的开环传递函数：

$$G_K(s) = G_c(s) \cdot G_0(s) = \frac{70(0.25s + 1)}{s(1.33s + 1)(0.02s + 1)(0.022s + 1)}$$

计算校正后性能指标：

- $\omega_{c1} = 13$ rad/s（满足设计要求）
- $\gamma_1 = 45.6^\circ$
- $M_{r1} = 1.4$
- $\sigma_{p1} = 32\% < 40\%$ ✓
- $t_{s1} = 0.73 \text{ s} < 1 \text{ s}$ ✓

**所有性能指标均满足设计要求。**

---

#### 例4.2：II 型系统串联校正设计（2-1-3 型期望特性）

**题目**：已知单位反馈系统的开环传递函数 $G_0(s) = \dfrac{25}{s^2(0.025s + 1)}$，设计串联校正装置，使系统满足：

1. 稳态加速度误差系数 $K_a^* = 25 \text{ s}^{-2}$（保持不变）
2. 超调量 $\sigma_p^* \leq 30\%$
3. 调整时间 $t_s^* \leq 0.9$ s

---

**【解】**

**第 1 步：绘制原系统 Bode 图**

原系统 $G_0(s) = \dfrac{25}{s^2(0.025s + 1)}$

- 系统为 **II 型**，低频段斜率 $-40$ dB/dec
- 转折频率：$\omega_a = \dfrac{1}{0.025} = 40$ rad/s
- $\omega = 1$ 时幅值：$20\lg 25 = 28$ dB
- 低频段（$-40$ dB/dec）：$L_0(\omega) = 28 - 40\lg\omega$

求原系统剪切频率：

在 $\omega < 40$ 段：$28 - 40\lg\omega_{c0} = 0 \implies \lg\omega_{c0} = 0.7 \implies \omega_{c0} = 5.01$ rad/s

**第 2 步：时域指标转换为频域指标**

由 $\sigma_p^* \leq 30\%$：

$$0.16 + 0.4(M_r - 1) \leq 0.30 \implies M_r \leq 1.35$$

取 $M_r = 1.35$。

由 $t_s^* \leq 0.9$ s：

$$\frac{\pi}{\omega_c^*}\left[2 + 1.5(M_r - 1) + 2.5(M_r - 1)^2\right] \leq 0.9$$

$$\frac{\pi}{\omega_c^*}\left[2 + 1.5 \times 0.35 + 2.5 \times 0.1225\right] \leq 0.9$$

$$\frac{\pi}{\omega_c^*} \times 2.831 \leq 0.9 \implies \omega_c^* \geq \frac{2.831\pi}{0.9} = 9.87$$

取 $\omega_c^* = 9.9$ rad/s。

**第 3 步：确定中频段参数**

$$\omega_2 \leq \omega_c^* \cdot \frac{M_r - 1}{M_r} = 9.9 \times \frac{0.35}{1.35} = 2.55 \text{ rad/s}$$

$$\omega_3 \geq \omega_c^* \cdot \frac{M_r + 1}{M_r} = 9.9 \times \frac{2.35}{1.35} = 17.23 \text{ rad/s}$$

在 $\omega_c^* = 9.9$ 处作斜率为 $-20$ dB/dec 的直线，向左延伸，与 $20\lg|G_0|$ 相交：

$$20\lg\frac{\omega_c^*}{\omega} = L_0(\omega) = 28 - 40\lg\omega$$

$$20\lg 9.9 - 20\lg\omega = 28 - 40\lg\omega$$

$$20\lg\omega = 28 - 20\lg 9.9 = 28 - 19.91 = 8.09$$

$$\omega = 10^{0.4045} = 2.54 \approx 2.5 \text{ rad/s}$$

取 $\omega_2 = 2.5$（满足 $\omega_2 \leq 2.55$ ✓）。

> 中频段与原系统低频段的交点频率恰好满足 $\omega_2$ 的要求。这是因为 $\omega_c^*$ 选择得当。

**第 4 步：确定高频段**

中频段向右延伸，原系统对数幅频特性的转折频率为 $\omega_a = 40$ rad/s。

若取 $\omega_3 = 40$（满足 $\omega_3 \geq 17.23$ ✓），过 $\omega_3$ 后斜率由 $-20$ dB/dec 变为 $-60$ dB/dec。

> 说明：过 $\omega_3$ 后，斜率由 $-20$ 变为 $-60$ dB/dec，意味着有**两个**时间常数为 $\dfrac{1}{\omega_3} = 0.025$ 的惯性环节。一个是原系统本身就有的 $(0.025s + 1)$，另一个由校正装置提供。

期望频率特性为 **2-1-3 型**（与典型的 2-1-2 型有区别）：

$$-40 \xrightarrow{\omega_2 = 2.5} -20 \xrightarrow{\omega_3 = 40} -60 \text{ dB/dec}$$

**第 5 步：确定低频段**

为保持稳态性能（$K_a = 25$ 不变），低频段与原系统**完全重合**。

由于 $\omega_2 = 2.5$ 处期望特性与原系统自然相交，无需额外连接段。

**第 6 步：求校正装置 $G_c(s)$**

期望开环传递函数：

$$G_K(s) = \frac{25\left(\dfrac{s}{2.5} + 1\right)}{s^2\left(\dfrac{s}{40}\right)^2 + \cdots}$$

更准确地：

$$G_K(s) = \frac{25\left(\dfrac{1}{2.5}s + 1\right)}{s^2\left(\dfrac{1}{40}s + 1\right)^2} = \frac{25(0.4s + 1)}{s^2(0.025s + 1)^2}$$

原系统：

$$G_0(s) = \frac{25}{s^2(0.025s + 1)}$$

校正装置：

$$G_c(s) = \frac{G_K(s)}{G_0(s)} = \frac{25(0.4s + 1)}{s^2(0.025s + 1)^2} \cdot \frac{s^2(0.025s + 1)}{25} = \frac{0.4s + 1}{0.025s + 1}$$

$$\boxed{G_c(s) = \frac{0.4s + 1}{0.025s + 1}}$$

> 这是一个**超前校正装置**：零点 $\omega_z = 1/0.4 = 2.5$，极点 $\omega_p = 1/0.025 = 40$。超前比 $\alpha = 40/2.5 = 16$。

**第 7 步：验算**

校正后系统的开环传递函数：

$$G_K(s) = \frac{25(0.4s + 1)}{s^2(0.025s + 1)^2}$$

校正后 $\omega_{c1} = 9.9$，计算相角裕度：

$$\gamma_1 = 180^\circ + \varphi(\omega_{c1})$$

$$\varphi(\omega_{c1}) = -180^\circ + \arctan(0.4 \times 9.9) - 2\arctan(0.025 \times 9.9)$$

$$= -180^\circ + \arctan 3.96 - 2\arctan 0.2475$$

$$= -180^\circ + 75.83^\circ - 2 \times 13.90^\circ = -180^\circ + 75.83^\circ - 27.80^\circ = -131.97^\circ$$

$$\gamma_1 = 180^\circ - 131.97^\circ = 48.03^\circ$$

谐振峰值：

$$M_{r1} = \frac{1}{\sin\gamma_1} = \frac{1}{\sin 48.03^\circ} = \frac{1}{0.7435} = 1.345$$

超调量：

$$\sigma_{p1} = 0.16 + 0.4(M_r - 1) = 0.16 + 0.4 \times 0.345 = 0.16 + 0.138 = 29.8\% < 30\% \quad \checkmark$$

调整时间系数：

$$k_0 = 2 + 1.5(M_r - 1) + 2.5(M_r - 1)^2 = 2 + 1.5 \times 0.345 + 2.5 \times 0.119 = 2.831$$

调整时间：

$$t_{s1} = \frac{k_0 \pi}{\omega_{c1}} = \frac{2.831 \times \pi}{9.9} = 0.899 \text{ s} < 0.9 \text{ s} \quad \checkmark$$

（课件中取 $k_0 = 2.815$，$t_{s1} = 0.893$ s。）

**所有性能指标均满足设计要求。**

---

### 4.9 如何选择 $\omega_c^*$ 使校正装置尽量简单

在上述两个例子中，直接选定了 $\omega_c^*$，并未分析为何这样选，但从设计效果来看，校正装置结构相对简单。其原因在于：

- **例 1**：中频段与原系统高频段的交点频率符合 $\omega_3 \geq \omega_c^* \dfrac{M_r + 1}{M_r}$ 的要求，使得**高频段可以设计为与原系统重叠**。
- **例 2**：中频段与原系统低频段的交点频率符合 $\omega_2 \leq \omega_c^* \dfrac{M_r - 1}{M_r}$ 的要求，使得**低频段可以设计为与原系统重叠**。

> **关键原则**：低频段重叠往往是**必须的**（保证稳态性能），高频段只要斜率与原系统相同，校正装置就会相对简单（不一定要求完全重叠）。

下面给出两种系统化的选择策略：

---

#### 4.9.1 思路一：优先使低频段与原系统重叠

**核心思想**：为保持稳态性能，低频段需与原系统重叠。因此，优先选择 $\omega_c^*$ 使得与原系统低频段的交点频率符合 $\omega_2 \leq \omega_c^* \dfrac{M_r - 1}{M_r}$。

**具体步骤：**

1. **选定 $M_r$**。判断期望频率特性曲线是否可能在 $\omega_c^*$ 左侧与原系统相交。如果可能，进入下一步。需兼顾高频段，尽量不让 $\omega_c^*$ 大于原系统高频段转折频率。

2. **设** $\omega_2 = h \cdot \omega_c^*$ 为满足条件 $\omega_2 \leq \omega_c^* \dfrac{M_r - 1}{M_r}$ 的表达式，即 $h = \dfrac{M_r - 1}{M_r}$。

3. **求解** $L_0(h\omega_c^*) = 0 - 20\lg\dfrac{h\omega_c^*}{\omega_c^*} = -20\lg h$。若有解且满足 $\omega_c^*$ 的要求，则选为 $\omega_c^*$。选择此时与原系统低频段的交点频率为 $\omega_2$。

4. 从 $\omega_2$ 向左绘制与原系统重叠的曲线，作为低频段。

**例 1 的尝试（思路一）：**

$M_r \leq 1.6$，$\omega_c^* \geq 12$，取 $M_r = 1.6$。

$h = \dfrac{M_r - 1}{M_r} = \dfrac{0.6}{1.6} = 0.375$，即 $\omega_2 = 0.375\omega_c^*$。

若要与低频段的交点满足 $\omega_2$ 的要求：

$$20\lg K - 20\lg\frac{1}{0.12} - 40\lg\frac{0.375\omega_c^*}{1/0.12} = -20\lg\frac{0.375\omega_c^*}{\omega_c^*}$$

$$36.9 - 18.4 - 40\lg\frac{0.375\omega_c^*}{8.33} = -20\lg 0.375$$

$$18.5 - 40\lg(0.045\omega_c^*) = 8.52$$

$$40\lg(0.045\omega_c^*) = 9.98 \implies \lg(0.045\omega_c^*) = 0.2495 \implies 0.045\omega_c^* = 1.776$$

$$\omega_c^* = 39.5 \approx 40 \text{ rad/s}$$

取 $\omega_c^* = 40$，则 $\omega_2 = 0.375 \times 40 = 15$。

但此时原系统高频段转折频率 $50$ 离 $\omega_2 = 15$ 太近，中频段宽度不够：

$$\gamma = \arcsin\frac{50 - \omega_2}{50 + \omega_2} = \arcsin\frac{35}{65} = \arcsin 0.538 = 32.6^\circ$$

不足以满足性能要求。若 $\omega_3 > 50$，则导致校正装置在转折频率 50 处要提供 $+40$ dB/dec 的斜率，校正装置变得复杂。

> **结论**：思路一对于例 1 并不理想，$\omega_c^*$ 被推得太高，导致中频段宽度不足。

---

#### 4.9.2 思路二：优先使高频段斜率与原系统一致

**核心思想**：高频段仅需斜率相同，尽量选择 $\omega_c^*$ 使得原系统高频段的某个转折频率符合 $\omega_3 \geq \omega_c^* \dfrac{M_r + 1}{M_r}$。

**具体步骤：**

1. **选定 $M_r$**。判断在 $\omega_c^*$ 右侧是否存在原系统的转折频率。如果存在，进入下一步。

2. **设 $\omega_3$ 为在 $\omega_c^*$ 右侧满足条件 $\omega_3 \geq \omega_c^* \dfrac{M_r + 1}{M_r}$ 的最小转折频率**。求出 $\omega_c^*$ 的范围，选择一个可行的 $\omega_c^*$。

3. 从 $\omega_3$ 向高频段绘制与原系统斜率相同的曲线，作为期望频率特性的高频段。

**例 1 中思路二的应用：**

$M_r = 1.6$，$\dfrac{M_r + 1}{M_r} = \dfrac{2.6}{1.6} = 1.625$。

原系统转折频率：$8.33$、$50$。

在 $\omega_c^* \geq 12$ 右侧，取 $\omega_3 = 50$（原系统转折频率）：

$$50 \geq 1.625\omega_c^* \implies \omega_c^* \leq \frac{50}{1.625} = 30.77$$

选择 $\omega_c^* = 13$（满足 $12 \leq 13 \leq 30.77$），则 $\omega_3$ 可取到 $45$（小于 $50$，且满足 $\omega_3 \geq 21.13$）。

> **这正是例 1 中实际采用的方案**：$\omega_c^* = 13$，$\omega_3 = 45$，高频段与原系统斜率一致，校正装置简单。

---

### 4.10 设计注意事项

1. **中频段宽度**：转折频率 $\omega_2$ 和 $\omega_3$ 之间保持足够的宽度，一般至少**十倍频程**（即 $H \geq 10$），以确保足够的相角裕度。

2. **期望特性类型**：中频段通常是 **2-1-2 型**。有时 **2-1-3 型**也可行（如例 4.2），具体取决于原系统的结构。

3. **校正装置的可实现性**：设计出的 $G_c(s)$ 必须是物理上可实现的。需检查：
   - 传递函数的分母阶次 $\geq$ 分子阶次（因果性）
   - 所有时间常数为正值（稳定性）
   - 所需元件参数在实际可实现范围内

4. **低频段设计**：低频段通常与原系统**重合**，以保证稳态性能不受影响。若校正装置需要在低频段提供额外增益，则需增加滞后环节。

5. **高频段设计**：高频段斜率与原系统**保持一致**即可，不必完全重叠。这样校正装置在高频段近似为单位增益（或常数增益），结构最简单。

---

### 4.11 设计步骤总结

```
期望频率特性法 — 完整设计流程
==========================================

① 确定开环增益 K
   · 根据稳态误差/误差系数要求确定 K
   · 绘制原系统 Bode 图（L₀(ω)）

② 时域指标 → 频域指标
   · σp* → Mr（由 σp = 0.16 + 0.4(Mr-1)）
   · ts* → ωc*（由 ts = π/ωc × [2+1.5(Mr-1)+2.5(Mr-1)²]）

③ 确定中频段
   · 由 Mr 计算 ω₂ 上限和 ω₃ 下限
   · 在 ωc* 处作 -20 dB/dec 直线
   · 选择合理的 ω₂、ω₃

④ 连接低频段
   · 中频段向左延伸，与低频段（起始段）相连
   · 低频段通常与原系统重合（保证稳态性能）
   · 若不能直接连接，增加过渡段（斜率 -40 dB/dec）

⑤ 确定高频段
   · 中频段向右延伸
   · 高频段斜率与原系统保持一致（简化校正装置）
   · 可能是 -40、-60 dB/dec 等

⑥ 求校正装置 Gc(s)
   · Lc(ω) = LK(ω) - L₀(ω)
   · 由 Lc(ω) 的转折频率确定 Gc(s) 的零极点

⑦ 验算
   · 计算校正后 ωc、γ、Mr
   · 计算 σp、ts 等时域指标
   · 确认全部满足设计要求
```

**$\omega_c^*$ 选择策略速查表：**

| 策略 | 核心条件 | 适用场景 |
|------|---------|---------|
| **思路一**（低频重叠优先） | $\omega_2 \leq \omega_c^* \dfrac{M_r - 1}{M_r}$，$\omega_2$ 为与原系统低频交点 | 原系统低频段斜率变化少 |
| **思路二**（高频斜率一致优先） | $\omega_3 \geq \omega_c^* \dfrac{M_r + 1}{M_r}$，$\omega_3$ 为原系统某转折频率 | 原系统有合适的高频转折频率 |

> **经验法则**：通常**思路二**更容易得到简单的校正装置，因为它直接利用原系统已有的转折频率，减少了校正装置需要提供的额外零极点。
