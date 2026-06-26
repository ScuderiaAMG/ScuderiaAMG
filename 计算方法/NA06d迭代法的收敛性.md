# NA06d 迭代法的收敛性

这份笔记按知识线索整理：先说明概念，再梳理公式和方法，最后整理常见题型。

> Huazhong University of Science and Technology · 《计算方法》课程
>
---

## 一、先把概念讲清楚

### 1. 误差传播——"误差的基因遗传"

迭代法的每一次计算，新误差都来自旧误差的"遗传"：

$$e^{(k)} = B^k e^{(0)}$$

这就像**家族基因遗传**：第 $k$ 代子孙的特征 = 祖先特征 × (遗传因子)$^k$。如果遗传因子（谱半径 $\rho(B)$）小于 1，那么特征会逐代衰减直至消失——这就是**收敛**。如果遗传因子 ≥ 1，特征被放大或维持——这就是**发散**。

> **核心洞察**：收敛与否**只取决于迭代矩阵 $B$ 的性质**，与初始值 $x^{(0)}$ 和右端项 $b$ 均无关！

### 2. 谱半径——"收敛的终审法官"

$\rho(B)$（矩阵 $B$ 所有特征值绝对值的最大值）是判断收敛的**充要条件**：

- $\rho(B) < 1$ → **必收敛**（从任意初值出发）
- $\rho(B) \geq 1$ → **必发散**
- $\rho(B)$ 越小 → **收敛越快**（误差以 $\sim[\rho(B)]^k$ 的速度衰减）

范数 $\|B\|$ 只是"初审法官"——$\|B\| < 1$ 是收敛的**充分不必要**条件（$\|B\| \geq 1$ 不代表发散，还要看 $\rho(B)$）。

### 3. 松弛法——"步子迈多大最合适？"

Gauss-Seidel 每次给出一个"建议的新值"。但有时候直接跳到建议值（$\omega=1$）未必最优：

- 步子迈太大 → 可能越过真解，甚至发散
- 步子迈太小 → 收敛太慢，浪费时间
- 找**最佳步长 $\omega_{opt}$** → 最小化 $\rho(H_\omega)$

这就是松弛法的本质：在旧值与 G-S 建议值之间做**加权平均**，通过调节松弛因子 $\omega$ 来**最小化谱半径、最大化收敛速度**。

| $\omega$ 范围 | 名称 | 效果 |
|--------------|------|------|
| $0 < \omega < 1$ | 低松弛 (Under-Relaxation) | 步子放小，稳定但慢 |
| $\omega = 1$ | Gauss-Seidel | 标准步长 |
| $\omega > 1$ | 超松弛 (SOR) | 步子放大，加速收敛 |

### 4. 严格对角占优——"天生收敛的体质"

如果矩阵 $A$ 满足**严格对角占优**（每行对角元的绝对值 > 同行其他元素绝对值之和），那么 Jacobi 和 Gauss-Seidel 迭代**必然收敛**。这就像一个"天选之子"——不需要计算谱半径就能断定收敛。

$$|a_{ii}| > \sum_{j \neq i} |a_{ij}| \quad (\forall i) \;\Longrightarrow\; \text{Jacobi 和 G-S 均收敛}$$

### 5. Jacobi 收敛但 G-S 发散？——"没有绝对的王者"

直觉上 G-S 应该比 Jacobi"更好"，但 PDF 给出反例：
- 同一个方程组，Jacobi 迭代矩阵谱半径为 0（**超快收敛**）
- G-S 迭代矩阵谱半径为 2（**发散**）

这说明**两者没有绝对的优劣关系**，必须具体问题具体分析。

---

## 二、知识脉络（按知识线索整理）

---

### 迭代法收敛性基本理论

#### 2.1.1 误差传播方程

设迭代格式 $x^{(k+1)} = B x^{(k)} + f$，真解满足 $x^* = B x^* + f$。定义第 $k$ 步的**误差向量**：

$$e^{(k)} = x^{(k)} - x^*$$

则误差的传播满足：

$$\boxed{e^{(k+1)} = B e^{(k)}}$$

递推得：

$$\boxed{e^{(k)} = B^k e^{(0)}}$$

#### 2.1.2 矩阵序列的收敛

定义：设 $A_k = (a_{ij}^{(k)})_{n \times n} \in \mathbb{R}^{n \times n}$，则

$$\lim_{k \to \infty} A_k = A \;\Longleftrightarrow\; \lim_{k \to \infty} a_{ij}^{(k)} = a_{ij} \quad (\forall\; 1 \leq i, j \leq n)$$

等价于对任何算子范数有：$\|A_k - A\| \to 0 \;(k \to \infty)$

特别地，$B^k \to 0$（零矩阵）等价于 $\|B^k\| \to 0$。

#### 2.1.3 收敛的充要条件（核心定理）

从误差方程 $e^{(k)} = B^k e^{(0)}$ 可知，迭代从任意初值出发收敛的充要条件是 $B^k \to 0$。

**定理（PDF 核心定理）**：

$$\boxed{B^k \to 0 \;\Longleftrightarrow\; \rho(B) < 1}$$

即：

$$\boxed{\text{迭代 } x^{(k+1)} = Bx^{(k)} + f \text{ 从任意 } x^{(0)} \text{ 出发收敛} \;\Longleftrightarrow\; \rho(B) < 1}$$

> **逻辑链**：迭代收敛 $\Longleftrightarrow$ $B^k \to 0$ $\Longleftrightarrow$ $\rho(B) < 1$

#### 2.1.4 收敛的充分条件

**(1) 范数条件**

若存在某矩阵范数使 $\|B\| = q < 1$，则迭代收敛，且有以下误差估计：

$$\|e^{(k)}\| \leq \|B\|^k \cdot \|e^{(0)}\| = q^k \cdot \|e^{(0)}\|$$

$$\|e^{(k)}\| \leq \|B\| \cdot \|e^{(k-1)}\| \leq \cdots \leq \|B\|^k \cdot \|e^{(0)}\|$$

> **注**：$\|B\| < 1$ 是**充分不必要**条件。$\|B\| \geq 1$ 不能断定发散，需进一步考察 $\rho(B)$。

**(2) 严格对角占优条件（PDF 重点定理）**

若 $A$ 为**严格对角占优矩阵**（strictly diagonally dominant matrix），即：

$$|a_{ii}| > \sum_{j \neq i} |a_{ij}| \quad (i = 1, 2, \ldots, n)$$

则解 $Ax = b$ 的 **Jacobi 迭代和 Gauss-Seidel 迭代均收敛**。

> **这是最实用的判别法**——不需要计算迭代矩阵和谱半径，直接看原矩阵的对角优势即可！

---

### 收敛性判别例题

#### 例题 1：用两种方法判断 Jacobi 迭代的收敛性

**方程组**：

$$\begin{cases}
8x_1 - 3x_2 + 2x_3 = 20 \\
4x_1 + 11x_2 - x_3 = 33 \\
6x_1 + 3x_2 + 12x_3 = 36
\end{cases}$$

**第一步**：写出 Jacobi 迭代形式

$$\begin{cases}
x_1 = \frac{20}{8} + \frac{3}{8}x_2 - \frac{2}{8}x_3 \\[4pt]
x_2 = \frac{33}{11} - \frac{4}{11}x_1 + \frac{1}{11}x_3 \\[4pt]
x_3 = \frac{36}{12} - \frac{6}{12}x_1 - \frac{3}{12}x_2
\end{cases}$$

**方法一：谱半径判别（充要条件）**

求 Jacobi 迭代矩阵 $B_J$ 的特征值：

$$\lambda_1 = -0.3082,\quad \lambda_2 = 0.1541 + 0.3245i,\quad \lambda_3 = 0.1541 - 0.3245i$$

$$\rho(B_J) = \max\{|\lambda_1|, |\lambda_2|, |\lambda_3|\} = 0.3592 < 1$$

> **结论**：$\rho(B_J) < 1$，Jacobi 迭代**收敛**。

**方法二：范数判别（充分条件）**

$$\|B_J\|_\infty = \max\left\{\frac{5}{8}, \frac{5}{11}, \frac{3}{4}\right\} = \frac{3}{4} = 0.75 < 1$$

$$\|B_J\|_1 = \max\left\{\frac{19}{22}, \frac{5}{8}, \frac{15}{44}\right\} = \frac{19}{22} \approx 0.864 < 1$$

> **结论**：$\|B_J\| < 1$，Jacobi 迭代**收敛**。

> **教学启示**：谱半径 ≤ 任何一种算子范数。范数判断更简单但更保守。

---

### 松弛法 /* Relaxation Methods */

#### 2.3.1 基本思想

松弛法是对 Gauss-Seidel 迭代法的修正，思想是：

1. 先用 G-S 迭代法计算一个"建议值" $\tilde{x}_i^{(k+1)}$
2. 再将建议值与上一步的近似值 $x_i^{(k)}$ 做**加权平均**，得到最终的新值

#### 2.3.2 松弛法迭代格式

**分量形式**：

$$\boxed{x_i^{(k+1)} = (1 - \omega) x_i^{(k)} + \omega \cdot \tilde{x}_i^{(k+1)}}$$

其中 $\tilde{x}_i^{(k+1)}$ 为 G-S 建议值：

$$\tilde{x}_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j=1}^{i-1} a_{ij} x_j^{(k+1)} - \sum_{j=i+1}^{n} a_{ij} x_j^{(k)}\right)$$

**代入得松弛法迭代公式**：

$$\boxed{x_i^{(k+1)} = (1-\omega)x_i^{(k)} + \frac{\omega}{a_{ii}}\left(b_i - \sum_{j=1}^{i-1} a_{ij} x_j^{(k+1)} - \sum_{j=i+1}^{n} a_{ij} x_j^{(k)}\right)}$$

> $\omega > 0$ 称为**松弛因子** (relaxation factor)

#### 2.3.3 松弛因子的三种情形

| $\omega$ 范围 | 名称 | 英文 | 含义 |
|--------------|------|------|------|
| $0 < \omega < 1$ | **低松弛法** | Under-Relaxation | 步子保守，用于 G-S 不收敛时使其收敛 |
| $\omega = 1$ | **Gauss-Seidel 法** | G-S | 松弛法的特例 |
| $\omega > 1$ | **（渐次）超松弛法** | SOR (Successive Over-Relaxation) | 步子放大，用于加速收敛 |

#### 2.3.4 松弛法的矩阵形式

将松弛法写为 $x^{(k+1)} = H_\omega x^{(k)} + g_\omega$ 形式：

$$H_\omega = (D + \omega L)^{-1}[(1-\omega)D - \omega U]$$

其中 $A = D + L + U$（对角 + 严格下三角 + 严格上三角）。

#### 2.3.5 松弛法收敛定理

**定理**：设 $A$ 可逆，且 $a_{ii} \neq 0$，则松弛法从任意 $x^{(0)}$ 出发对某个 $\omega$ 收敛的**充要条件**是：

$$\boxed{\rho(H_\omega) < 1}$$

#### 2.3.6 收敛速度分析

**问题**：什么因子决定了收敛速度？

**分析**：设 $B$ 有特征值 $\lambda_1, \ldots, \lambda_n$，对应 $n$ 个线性无关的特征向量 $v_1, \ldots, v_n$。初始误差可展开为：

$$e^{(0)} = \sum_{i=1}^{n} \alpha_i v_i$$

则第 $k$ 步误差为：

$$e^{(k)} = B^k e^{(0)} = \sum_{i=1}^{n} \alpha_i \lambda_i^k v_i$$

当 $k$ 充分大时，$|\lambda_i|^k$ 中最大者（即 $\rho(B)$）占主导：

$$\boxed{e^{(k)} \sim [\rho(B)]^k \cdot e^{(0)}}$$

> **答案**：**迭代矩阵的谱半径 $\rho(B)$ 越小，收敛越快！**
>
> 对于松弛法，希望找到 $\omega_{opt}$ 使得 $\rho(H_\omega)$ 最小。

#### 最优松弛因子例题

**例题 2**：$A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$，$b = \begin{bmatrix} 1 \\ 2 \end{bmatrix}$，考虑迭代格式：

$$x^{(k+1)} = x^{(k)} + \omega(Ax^{(k)} - b)$$

问：① $\omega$ 取何值可使迭代收敛？② $\omega$ 取何值时迭代收敛最快？

**解**：迭代矩阵 $B = I + \omega A$，求其特征值：

$$|\lambda I - B| = \left|\begin{matrix} \lambda - (1+2\omega) & -\omega \\ -\omega & \lambda - (1+2\omega) \end{matrix}\right| = 0$$

得：$\lambda_1 = 1 + \omega$，$\lambda_2 = 1 + 3\omega$

**① 收敛条件** $\rho(B) < 1$：

$$|1 + \omega| < 1 \;\text{且}\; |1 + 3\omega| < 1 \;\Longrightarrow\; -\frac{2}{3} < \omega < 0$$

**② 求最优 $\omega$**：$\rho(B) = \max\{|1+\omega|, |1+3\omega|\}$

作函数图像分析，两直线交点处 $\rho(B)$ 最小：

$$|1+\omega| = |1+3\omega| \;\Longrightarrow\; \omega = -\frac{1}{2}$$

> **结论**：$\omega = -\frac{1}{2}$ 时收敛最快，此时 $\rho(B) = \frac{1}{2}$。

---

### Jacobi 收敛而 G-S 发散的反例

#### 例题 3：判断 Jacobi 和 G-S 的收敛性

**方程组**：

$$\begin{bmatrix} 1 & 2 & -2 \\ 1 & 1 & 1 \\ 2 & 2 & 1 \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix} = \begin{bmatrix} 1 \\ 1 \\ 1 \end{bmatrix}$$

#### Jacobi 迭代收敛性分析

**Jacobi 迭代格式**：

$$\begin{bmatrix} x_1^{(k+1)} \\ x_2^{(k+1)} \\ x_3^{(k+1)} \end{bmatrix} = \begin{bmatrix} 0 & -2 & 2 \\ -1 & 0 & -1 \\ -2 & -2 & 0 \end{bmatrix} \begin{bmatrix} x_1^{(k)} \\ x_2^{(k)} \\ x_3^{(k)} \end{bmatrix} + \begin{bmatrix} 1 \\ 1 \\ 1 \end{bmatrix}$$

**Jacobi 迭代矩阵**：

$$B_J = \begin{bmatrix} 0 & -2 & 2 \\ -1 & 0 & -1 \\ -2 & -2 & 0 \end{bmatrix}$$

**求特征值**：

$$\det(\lambda I - B_J) = \det\begin{bmatrix} \lambda & 2 & -2 \\ 1 & \lambda & 1 \\ 2 & 2 & \lambda \end{bmatrix} = \lambda^3 = 0$$

$$\lambda_1 = \lambda_2 = \lambda_3 = 0$$

$$\rho(B_J) = \max|\lambda| = 0 < 1$$

> **结论**：Jacobi 迭代**收敛**（且谱半径为 0，理论上有限步收敛！）

#### Gauss-Seidel 迭代收敛性分析

**Gauss-Seidel 迭代格式**：

$$\begin{cases}
x_1^{(k+1)} = -2x_2^{(k)} + 2x_3^{(k)} + 1 \\
x_2^{(k+1)} = -x_1^{(k+1)} - x_3^{(k)} + 1 \\
x_3^{(k+1)} = -2x_1^{(k+1)} - 2x_2^{(k+1)} + 1
\end{cases}$$

代入化简得：

$$\begin{cases}
x_1^{(k+1)} = -2x_2^{(k)} + 2x_3^{(k)} + 1 \\
x_2^{(k+1)} = 2x_2^{(k)} - 3x_3^{(k)} \\
x_3^{(k+1)} = 2x_3^{(k)} - 1
\end{cases}$$

**Gauss-Seidel 迭代矩阵**：

$$B_{GS} = \begin{bmatrix} 0 & -2 & 2 \\ 0 & 2 & -3 \\ 0 & 0 & 2 \end{bmatrix}$$

$B_{GS}$ 是上三角矩阵，特征值即对角元：

$$\lambda_1 = 0,\quad \lambda_2 = 2,\quad \lambda_3 = 2$$

$$\rho(B_{GS}) = \max|\lambda| = 2 > 1$$

> **结论**：Gauss-Seidel 迭代**发散**！

> ⚠️ **重要启示**：此例有力地说明——**Jacobi 收敛时 G-S 可能发散，G-S 收敛时 Jacobi 也可能不收敛**。两种方法没有绝对的优劣关系！

---

### 课上习题

> 为"课上习题"标题页，具体习题内容可能需要结合课堂讲授。

---

### 方法框架总览

PDF 末页列出本课程（解线性方程组部分）的主要方法体系：

| 方法 | 类别 | 说明 |
|------|------|------|
| **LU 分解** | 直接法 | 高斯消元的矩阵形式 |
| **Crout 分解（追赶法）** | 直接法 | 适用于三对角方程组 |
| **平方根法（Cholesky）** | 直接法 | 适用于对称正定矩阵 |
| **约当消去法（Gauss-Jordan）** | 直接法 | 直接化为单位矩阵 |

---

## 三、解题通法

### 1. 收敛性的核心判据

对迭代
$$
x^{(k+1)}=Bx^{(k)}+f,
$$
误差满足
$$
e^{(k)}=B^ke^{(0)}.
$$

迭代对任意初值收敛的充要条件是
$$
\rho(B)<1.
$$

### 2. 快速充分条件

若某种矩阵范数满足
$$
\|B\|<1,
$$
则迭代收敛。

常用关系：
$$
\rho(B)\le \|B\|.
$$

### 3. Jacobi / G-S 判断流程

1. 写出迭代矩阵 $B_J$ 或 $B_{GS}$。
2. 优先算谱半径 $\rho(B)$。
3. 若谱半径难算，可用 $\|B\|_1$ 或 $\|B\|_\infty$ 做充分判断。
4. 若 $A$ 严格对角占优，可直接给出收敛结论。

### 4. SOR 松弛法

松弛因子 $\omega$ 控制步长：

- $0<\omega<1$：低松弛。
- $\omega=1$：Gauss-Seidel。
- $1<\omega<2$：超松弛常见范围。

对称正定矩阵下，SOR 在
$$
0<\omega<2
$$
时收敛。

### 5. 易错点

- $\rho(B)<1$ 是充要条件，$\|B\|<1$ 只是充分条件。
- Jacobi 收敛不必然推出 G-S 收敛，反之也要看条件。
- 谱半径看特征值模最大值，不是矩阵元素最大值。
