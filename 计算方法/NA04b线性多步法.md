# NA04b 线性多步法

这份笔记按知识线索整理：先说明概念，再梳理公式和方法，最后整理常见题型。

## 一、先把概念讲清楚

### 什么是线性多步法？

前面学习的欧拉法、龙格-库塔法都是**单步法**——计算 $y_{i+1}$ 时只用前一步 $y_i$ 的信息。而**多步法**的思路是：既然前面已经计算出了 $y_0, y_1, y_2, ..., y_i$ 这么多值，为什么不用更多已知信息来提高精度呢？

**生活类比**：想象你是一个天气预报员。单步法就像只看昨天来预测今天——信息有限。多步法则像同时参考昨天、前天、大前天的天气来预测今天——信息越多，预测通常越准。

### 核心思想

线性多步法的公式形式为：
$$y_{i+1} = \alpha_0 y_i + \alpha_1 y_{i-1} + \cdots + \alpha_k y_{i-k} + h[\beta_{-1} y'_{i+1} + \beta_0 y'_i + \beta_1 y'_{i-1} + \cdots + \beta_k y'_{i-k}]$$

其中 $y'_i = f(x_i, y_i)$。

- 如果 $\beta_{-1} = 0$，公式为**显式**（可直接计算 $y_{i+1}$）
- 如果 $\beta_{-1} \neq 0$，公式为**隐式**（需解方程）

### 为什么需要多步法？

1. **精度更高**：同等计算量下，多步法可获得更高精度
2. **效率更高**：每步只需计算一次 $f$（RK4 需 4 次）
3. **缺点**：不能自启动，需要先用单步法计算前几个值

---

## 二、知识脉络

### 线性多步法的基本概念

**多步法的优势**：充分利用已知的 $y_0, y_1, \ldots, y_i$（精度高）。

**与单步法的对比**：
- 求解初值问题的数值方法都是"步进式"的
- **单步法**：只用其前一步的值 $y_i$
- **多步法**：使用前面多个已知值 $y_0, y_1, \ldots, y_i$

**线性多步法的一般公式**：
$$y_{i+1} = \sum_{j=0}^k \alpha_j y_{i-j} + h \sum_{j=-1}^k \beta_j y'_{i-j}$$

其中 $y'_m = f(x_m, y_m)$。

- 当 $\beta_{-1} = 0$ 时为**显式**格式
- 当 $\beta_{-1} \neq 0$ 时为**隐式**格式

### 确定待定系数的例题

**例题**：设
$$y_{i+1} = \alpha_0 y_i + \alpha_1 y_{i-1} + \alpha_2 y_{i-2} + h[\beta_0 y'_i + \beta_1 y'_{i-1} + \beta_2 y'_{i-2} + \beta_3 y'_{i-3}]$$

确定式中待定系数 $\alpha_0, \alpha_1, \alpha_2, \beta_0, \beta_1, \beta_2, \beta_3$，使得公式具有 4 阶精度。

**解法**：利用 Taylor 展开，将各项在 $x_i$ 处展开。

首先，各 $y$ 值的 Taylor 展开：
$$y_{i-1} = y_i - h y'_i + \frac{h^2}{2} y''_i - \frac{h^3}{6} y'''_i + \frac{h^4}{24} y^{(4)}_i + O(h^5)$$
$$y_{i-2} = y_i - 2h y'_i + 2h^2 y''_i - \frac{4h^3}{3} y'''_i + \frac{2h^4}{3} y^{(4)}_i + O(h^5)$$

各 $y'$ 值的 Taylor 展开：
$$y'_{i-1} = y'_i - h y''_i + \frac{h^2}{2} y'''_i - \frac{h^3}{6} y^{(4)}_i + O(h^4)$$
$$y'_{i-2} = y'_i - 2h y''_i + 2h^2 y'''_i - \frac{4h^3}{3} y^{(4)}_i + O(h^4)$$
$$y'_{i-3} = y'_i - 3h y''_i + \frac{9h^2}{2} y'''_i - \frac{9h^3}{2} y^{(4)}_i + O(h^4)$$

$y(x_{i+1})$ 的 Taylor 展开（假设 $y(x_i) = y_i$）：
$$y(x_{i+1}) = y_i + h y'_i + \frac{h^2}{2} y''_i + \frac{h^3}{6} y'''_i + \frac{h^4}{24} y^{(4)}_i + O(h^5)$$

代入线性多步法公式，对比系数使得 $y_{i+1} - y(x_{i+1}) = O(h^5)$（即 4 阶精度），得到方程组：

$$
\begin{cases}
\alpha_0 + \alpha_1 + \alpha_2 = 1 \\
-\alpha_1 - 2\alpha_2 + \beta_0 + \beta_1 + \beta_2 + \beta_3 = 1 \\
\frac{1}{2}\alpha_1 + 2\alpha_2 - \beta_1 - 2\beta_2 - 3\beta_3 = \frac{1}{2} \\
-\frac{1}{6}\alpha_1 - \frac{4}{3}\alpha_2 + \frac{1}{2}\beta_1 + 2\beta_2 + \frac{9}{2}\beta_3 = \frac{1}{6} \\
\frac{1}{24}\alpha_1 + \frac{2}{3}\alpha_2 - \frac{1}{6}\beta_1 - \frac{4}{3}\beta_2 - \frac{9}{2}\beta_3 = \frac{1}{24}
\end{cases}
$$

这是 7 个未知数、5 个方程的方程组，因此有多组解。

### Adams 显式与隐式公式

**Adams 方法**是形如下式的 $k$ 步法：
$$y_{i+1} = y_i + h \sum_{j=-1}^k \beta_j y'_{i-j}$$

即 $\alpha_0 = 1$，$\alpha_1 = \alpha_2 = \cdots = \alpha_k = 0$ 的特例。

以 $k=3$ 为例，将系数代入前面的方程组可得：
$$\beta_{-1} \text{ 自由}, \quad \beta_0 = \frac{1}{2} - \frac{5}{12}\beta_{-1}, \quad \beta_1 = -\frac{1}{6} - \frac{4}{3}\beta_{-1}, \quad \beta_2 = \frac{1}{2} - \frac{3}{2}\beta_{-1}, \quad \beta_3 = \frac{5}{6} - \frac{2}{3}\beta_{-1}$$

### Adams 具体公式

**三阶 Adams 显式公式**（$\beta_{-1} = 0$）：
$$y_{n+1} = y_n + \frac{h}{12}(23f_n - 16f_{n-1} + 5f_{n-2})$$

**四阶 Adams 隐式公式**：
$$y_{n+1} = y_n + \frac{h}{24}(9f_{n+1} + 19f_n - 5f_{n-1} + f_{n-2})$$

### 常微分方程数值解法总结

考虑一阶常微分方程的初值问题：
$$\begin{cases}
\frac{dy}{dx} = f(x, y), & x \in [a, b] \\
y(a) = y_0
\end{cases}$$

要计算出解函数 $y(x)$ 在一系列节点 $a = x_0 < x_1 < \cdots < x_n = b$ 处的近似值 $y_i \approx y(x_i)$。

**数值解法分类**：
- Euler 法、隐式 Euler 法
- 梯形公式、中心公式
- 改进的 Euler 法、龙格-库塔法
- **线性多步法**

**课后作业**：p.291 #1

### 微分方程组

**一阶微分方程组**的一般形式：
$$
\begin{cases}
y'_1(x) = f_1(x, y_1, y_2, \ldots, y_m) \\
y'_2(x) = f_2(x, y_1, y_2, \ldots, y_m) \\
\cdots \\
y'_m(x) = f_m(x, y_1, y_2, \ldots, y_m)
\end{cases}
$$

**初值条件**：
$$y_1(x_0) = y_{10}, \quad y_2(x_0) = y_{20}, \quad \ldots, \quad y_m(x_0) = y_{m0}$$

**向量形式**：
令 $\boldsymbol{y} = \begin{pmatrix} y_1 \\ y_2 \\ \vdots \\ y_m \end{pmatrix}$, $\boldsymbol{f} = \begin{pmatrix} f_1 \\ f_2 \\ \vdots \\ f_m \end{pmatrix}$, $\boldsymbol{y}_0 = \begin{pmatrix} y_{10} \\ y_{20} \\ \vdots \\ y_{m0} \end{pmatrix}$

则方程组可写成：
$$\begin{cases}
\boldsymbol{y}'(x) = \boldsymbol{f}(x, \boldsymbol{y}) \\
\boldsymbol{y}(x_0) = \boldsymbol{y}_0
\end{cases}$$

前述所有公式（欧拉法、RK 法等）皆适用于向量形式。

### 高阶微分方程

**高阶微分方程的初值问题**：
$$\begin{cases}
y^{(n)} = f(x, y, y', y'', \ldots, y^{(n-1)}) \\
y(x_0) = a_0, \; y'(x_0) = a_1, \; \ldots, \; y^{(n-1)}(x_0) = a_{n-1}
\end{cases}$$

**解法**：化为**一阶微分方程组**求解。

引入新变量：
$$y_1 = y, \quad y_2 = y', \quad y_3 = y'', \quad \ldots, \quad y_n = y^{(n-1)}$$

则原方程化为：
$$
\begin{cases}
y'_1 = y_2 \\
y'_2 = y_3 \\
\cdots \\
y'_{n-1} = y_n \\
y'_n = f(x, y_1, y_2, \ldots, y_n)
\end{cases}
$$

初值条件化为：
$$y_1(x_0) = a_0, \quad y_2(x_0) = a_1, \quad \ldots, \quad y_n(x_0) = a_{n-1}$$

### 边值问题的数值解——打靶法

**2 阶常微分方程边值问题**：
$$\begin{cases}
y'' = f(x, y, y'), & x \in [a, b] \\
y(a) = \alpha, \quad y(b) = \beta
\end{cases}$$

**打靶法（shooting method）**的基本思想：
1. 先猜测一个初始斜率 $y'(a) = s$
2. 通过解初值问题：
   $$\begin{cases}
   y'' = f(x, y, y') \\
   y(a) = \alpha, \quad y'(a) = s
   \end{cases}$$
   得到 $y(b) = \varphi(s)$
3. 找出 $s^*$ 使得 $\varphi(s^*) = \beta$，即把问题转化为求方程 $\varphi(s) - \beta = 0$ 的根

**图示理解**：
- $y$-$x$ 平面上从 $x=a$ 处以不同斜率 $s$ "射击"，看弹道是否在 $x=b$ 处命中目标 $\beta$
- 每计算一个 $\varphi(s)$ 都必须解一个 ODE（常微分方程）

### 边值问题的数值解——有限差分法

**有限差分法（finite difference method）**的基本步骤：
1. 将求解区间 $[a, b]$ 等分为 $N$ 份，取节点 $x_i = a + ih$（$i = 0, 1, \ldots, N$）
2. 在每一个节点处将 $y'$ 和 $y''$ 离散化：

**二阶导数的中心差商近似**：
$$y''(x) \approx \frac{y(x+h) - 2y(x) + y(x-h)}{h^2}$$

**一阶导数的中心差商近似**：
$$y'(x) \approx \frac{y(x+h) - y(x-h)}{2h}$$

3. 代入原方程得到差分方程组：

$$\begin{cases}
y_0 = \alpha, \quad y_N = \beta \\
\frac{y_{i+1} - 2y_i + y_{i-1}}{h^2} = f\left(x_i, y_i, \frac{y_{i+1} - y_{i-1}}{2h}\right), & i = 1, 2, \ldots, N-1
\end{cases}$$

这样就得到了一个关于 $y_1, y_2, \ldots, y_{N-1}$ 的代数方程组，可用线性方程组求解方法求解。

---

## 三、做题方法

### 1. 线性多步法的一般求解流程

```
给定初值问题 → 选择多步法公式 → 用单步法（如RK4）启动前几步 → 进入多步法循环迭代 → 评估精度
```

### 2. 关键公式对比

| 方法 | 公式 | 阶数 | 类型 |
|------|------|:----:|:----:|
| Adams显式3步法 | $y_{n+1} = y_n + \frac{h}{12}(23f_n - 16f_{n-1} + 5f_{n-2})$ | 3 | 显式 |
| Adams隐式4步法 | $y_{n+1} = y_n + \frac{h}{24}(9f_{n+1} + 19f_n - 5f_{n-1} + f_{n-2})$ | 4 | 隐式 |

### 3. 确定线性多步法系数的标准步骤

**步骤**：
1. 写出线性多步法的待定系数形式
2. 将各项在 $x_i$ 处进行 Taylor 展开
3. 合并同次幂项
4. 令 $y_{i+1}$ 的表达式与 $y(x_{i+1})$ 的 Taylor 展开式的前 $p+1$ 项系数相等
5. 解待定系数的方程组

**注意**：从 $h^0$ （即 $y_i$ 系数）开始逐次比对，直到达到所需精度阶数。

### 4. 微分方程组的数值解法

对向量形式的方程组：
$$\boldsymbol{y}' = \boldsymbol{f}(x, \boldsymbol{y})$$

所有单步法和多步法都直接适用，只需将标量运算改为向量运算：

以 RK4 为例：
$$
\begin{aligned}
\boldsymbol{K}_1 &= \boldsymbol{f}(x_i, \boldsymbol{y}_i) \\
\boldsymbol{K}_2 &= \boldsymbol{f}(x_i + \frac{h}{2}, \boldsymbol{y}_i + \frac{h}{2}\boldsymbol{K}_1) \\
\boldsymbol{K}_3 &= \boldsymbol{f}(x_i + \frac{h}{2}, \boldsymbol{y}_i + \frac{h}{2}\boldsymbol{K}_2) \\
\boldsymbol{K}_4 &= \boldsymbol{f}(x_i + h, \boldsymbol{y}_i + h\boldsymbol{K}_3) \\
\boldsymbol{y}_{i+1} &= \boldsymbol{y}_i + \frac{h}{6}(\boldsymbol{K}_1 + 2\boldsymbol{K}_2 + 2\boldsymbol{K}_3 + \boldsymbol{K}_4)
\end{aligned}
$$

### 5. 高阶方程化一阶方程组的标准步骤

1. 令 $y_1 = y$, $y_2 = y'$, $y_3 = y''$, $\ldots$, $y_n = y^{(n-1)}$
2. 写出各 $y_i$ 的导数关系：$y'_1 = y_2$, $y'_2 = y_3$, $\ldots$, $y'_{n-1} = y_n$
3. 最高阶导数 $y'_n = f(x, y_1, y_2, \ldots, y_n)$
4. 确定向量初值条件
5. 用 ODE 数值方法求解

### 6. 边值问题的两种解法对比

| 方法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **打靶法** | 转化为求初始斜率的根 | 思路直观，可复用 IVP 解法 | 每步需解 ODE，计算量大 |
| **有限差分法** | 离散化后解代数方程组 | 一次求解，对非线性问题有效 | 网格加密时计算量大 |

### 7. 常见陷阱

1. **启动问题**：多步法不能自启动，需先用同阶单步法计算前几步的值
2. **步长一致性**：启动阶段所用步长必须与多步法阶段一致
3. **隐式公式求解**：Adams 隐式法每步需解方程，通常用迭代法
4. **稳定性**：多步法也有稳定性限制，高阶显式多步法稳定区域通常较小
