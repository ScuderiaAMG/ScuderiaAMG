# NA06c 解线性方程组的迭代法

这份笔记按知识线索整理：先说明概念，再梳理公式和方法，最后整理常见题型。

## 一、先把概念讲清楚

### 什么是迭代法？

迭代法是一种"步步逼近"的方法。对于线性方程组 $A\boldsymbol{x} = \boldsymbol{b}$，我们不直接求解 $\boldsymbol{x} = A^{-1}\boldsymbol{b}$，而是先猜一个初始值 $\boldsymbol{x}^{(0)}$，然后通过某种规则不断修正，使近似解越来越接近真实解。

**生活类比**：想象你在一个陌生的城市找一家餐厅。直接解法就像看地图找到精确路线（但需要完整的地图，计算量大）。迭代法就像逢人就问路——"请问某某餐厅怎么走？"别人告诉你"往前直走，看到红绿灯左转"，你走一段再问下一个人，逐步修正方向，最终到达目的地。

### 为什么要用迭代法？

直接法（如高斯消元法）存在以下问题：
1. 对于高阶方程组，计算量巨大
2. 即使矩阵是稀疏的（大部分元素为0），运算中也很难保持稀疏性，导致存储量巨大
3. 程序复杂

迭代法则能：
1. 保持矩阵的稀疏性（0 元素不参与运算）
2. 计算简单、程序容易实现
3. 对很多高阶方程组收敛较快

### 迭代法的一般思路

将 $A\boldsymbol{x} = \boldsymbol{b}$ 改写为等价形式 $\boldsymbol{x} = B\boldsymbol{x} + \boldsymbol{f}$，然后建立迭代格式：
$$\boldsymbol{x}^{(k+1)} = B\boldsymbol{x}^{(k)} + \boldsymbol{f}$$

从初值 $\boldsymbol{x}^{(0)}$ 出发，得到序列 $\{\boldsymbol{x}^{(k)}\}$。

研究内容：
- 如何建立迭代格式？
- 向量序列的收敛条件？
- 收敛速度？
- 误差估计？

---

## 二、知识脉络

### 线性方程组回顾

求解含有多个未知量 $x_1, x_2, \ldots, x_n$ 的线性方程组：
$$
\begin{cases}
a_{11}x_1 + a_{12}x_2 + \cdots + a_{1n}x_n = b_1 \\
a_{21}x_1 + a_{22}x_2 + \cdots + a_{2n}x_n = b_2 \\
\cdots\cdots\cdots\cdots\cdots\cdots\cdots\cdots\cdots \\
a_{n1}x_1 + a_{n2}x_2 + \cdots + a_{nn}x_n = b_n
\end{cases}
$$

### 上次课程回顾——直接法

**直接法**：若不存在舍入误差，可得精确解。

1. **对角/三角矩阵直接求解**：当 $A$ 为对角矩阵、上三角矩阵、下三角矩阵时，可直接求解
2. **消元法**：通过消元将 $A$ 转化为上三角阵求解
   - 高斯消元法
   - 列主元消元法
   - 标度化列主元消元法
   - 全主元消元法
3. **矩阵分解法**：将 $A$ 进行三角分解
   - LU 分解
   - Crout 分解
   - 平方根法（Cholesky 分解）
4. **高斯-若当消去法**：通过将 $A$ 转化为单位矩阵求解

### 线性方程组的解法分类

**直接法**：
- 若不存在舍入误差，可得精确解
- 适用于中小型方程组
- 对高阶方程组，即使矩阵是稀疏的，运算中很难保持稀疏性，导致存储量大，程序复杂

**间接解法（迭代法）**：
- Jacobi 法
- Gauss-Seidel 法
- 松弛因子迭代法
- 能保持矩阵的稀疏性，具有计算简单、程序编制容易的优点
- 在很多情况下收敛较快，能有效地解一些高阶方程组

### 迭代法的基本思想

**思路**：与解 $f(x) = 0$ 的不动点迭代相似。

将 $A\boldsymbol{x} = \boldsymbol{b}$ 改写为等价形式 $\boldsymbol{x} = B\boldsymbol{x} + \boldsymbol{f}$，建立迭代：
$$\boldsymbol{x}^{(k+1)} = B\boldsymbol{x}^{(k)} + \boldsymbol{f}$$

从初值 $\boldsymbol{x}^{(0)}$ 出发，得到序列 $\{\boldsymbol{x}^{(k)}\}$。

**优势**：计算精度可控，特别适用于求解系数为大型稀疏矩阵的方程组。

**研究内容**：
1. 如何建立迭代格式？
2. 收敛速度？
3. 向量序列的收敛条件？
4. 误差估计？

### Jacobi 迭代法

从方程组中每个方程分离出一个变量：

$$
\begin{cases}
a_{11}x_1 + a_{12}x_2 + \cdots + a_{1n}x_n = b_1 \\
a_{21}x_1 + a_{22}x_2 + \cdots + a_{2n}x_n = b_2 \\
\cdots\cdots\cdots\cdots\cdots\cdots\cdots\cdots\cdots \\
a_{n1}x_1 + a_{n2}x_2 + \cdots + a_{nn}x_n = b_n
\end{cases}
$$

假设 $a_{ii} \neq 0$，从第 $i$ 个方程中分离出 $x_i$：

$$
x_1 = \frac{1}{a_{11}}(-a_{12}x_2 - a_{13}x_3 - \cdots - a_{1n}x_n + b_1) \\
x_2 = \frac{1}{a_{22}}(-a_{21}x_1 - a_{23}x_3 - \cdots - a_{2n}x_n + b_2) \\
\cdots \\
x_n = \frac{1}{a_{nn}}(-a_{n1}x_1 - a_{n2}x_2 - \cdots - a_{n,n-1}x_{n-1} + b_n)
$$

**Jacobi 迭代格式**（全部用第 $k$ 步的值）：

$$
x_1^{(k+1)} = \frac{1}{a_{11}}\left(b_1 - \sum_{j=2}^n a_{1j}x_j^{(k)}\right) \\
x_2^{(k+1)} = \frac{1}{a_{22}}\left(b_2 - \sum_{j=1, j\neq2}^n a_{2j}x_j^{(k)}\right) \\
\cdots \\
x_n^{(k+1)} = \frac{1}{a_{nn}}\left(b_n - \sum_{j=1}^{n-1} a_{nj}x_j^{(k)}\right)
$$

统一形式：
$$x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j=1, j\neq i}^n a_{ij}x_j^{(k)}\right), \quad i = 1, 2, \ldots, n$$

### Jacobi 迭代法例题

**例**：用 Jacobi 迭代法求解下列线性方程组
$$
\begin{cases}
10x_1 + 3x_2 + x_3 = 14 \\
2x_1 - 10x_2 + 3x_3 = -5 \\
x_1 + 3x_2 + 10x_3 = 14
\end{cases}
$$

**解**：将方程组写成等价形式 $\boldsymbol{x} = B\boldsymbol{x} + \boldsymbol{f}$：

$$
\begin{cases}
x_1 = -0.3x_2 - 0.1x_3 + 1.4 \\
x_2 = 0.2x_1 + 0.3x_3 + 0.5 \\
x_3 = -0.1x_1 - 0.3x_2 + 1.4
\end{cases}
$$

**Jacobi 迭代格式**：
$$
\begin{cases}
x_1^{(k+1)} = -0.3x_2^{(k)} - 0.1x_3^{(k)} + 1.4 \\
x_2^{(k+1)} = 0.2x_1^{(k)} + 0.3x_3^{(k)} + 0.5 \\
x_3^{(k+1)} = -0.1x_1^{(k)} - 0.3x_2^{(k)} + 1.4
\end{cases}
$$

取初始值 $x_1^{(0)} = x_2^{(0)} = x_3^{(0)} = 0$：

- $k=1$：$x_1^{(1)} = 1.4$, $x_2^{(1)} = 0.5$, $x_3^{(1)} = 1.4$
- $k=4$：$x_1^{(4)} = 0.9906$, $x_2^{(4)} = 0.9645$, $x_3^{(4)} = 0.9906$
- 精确解：$x_1 = x_2 = x_3 = 1$

### Jacobi 迭代法总结

**页面上内容较少，主要为章节过渡**，仅标识为 §3 Jacobi & Gauss-Seidel Iterative Methods 的 Jacobi 迭代法部分。

### Gauss-Seidel 迭代法

**核心改进**：在计算 $x_i^{(k+1)}$ 时，已经计算出的新值 $x_1^{(k+1)}, x_2^{(k+1)}, \ldots, x_{i-1}^{(k+1)}$ 立即被使用，而不是等到下一次迭代。

**Gauss-Seidel 迭代格式**：

$$
\begin{aligned}
x_1^{(k+1)} &= \frac{1}{a_{11}}\left(b_1 - a_{12}x_2^{(k)} - a_{13}x_3^{(k)} - \cdots - a_{1n}x_n^{(k)}\right) \\
x_2^{(k+1)} &= \frac{1}{a_{22}}\left(b_2 - a_{21}x_1^{(k+1)} - a_{23}x_3^{(k)} - \cdots - a_{2n}x_n^{(k)}\right) \\
x_3^{(k+1)} &= \frac{1}{a_{33}}\left(b_3 - a_{31}x_1^{(k+1)} - a_{32}x_2^{(k+1)} - a_{34}x_4^{(k)} - \cdots - a_{3n}x_n^{(k)}\right) \\
&\vdots \\
x_n^{(k+1)} &= \frac{1}{a_{nn}}\left(b_n - a_{n1}x_1^{(k+1)} - a_{n2}x_2^{(k+1)} - \cdots - a_{n,n-1}x_{n-1}^{(k+1)}\right)
\end{aligned}
$$

**统一形式**：
$$x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j=1}^{i-1} a_{ij}x_j^{(k+1)} - \sum_{j=i+1}^{n} a_{ij}x_j^{(k)}\right)$$

**优势**：只需存储一组向量。

### Jacobi 与 Gauss-Seidel 对比例题

**例**：求解方程组
$$
\begin{cases}
10x_1 - 2x_2 - x_3 = 3 \\
-2x_1 + 10x_2 - x_3 = 15 \\
-x_1 - 2x_2 + 5x_3 = 10
\end{cases}
$$

分离出 $x_1, x_2, x_3$：
$$
\begin{cases}
x_1 = 0.2x_2 + 0.1x_3 + 0.3 \\
x_2 = 0.2x_1 + 0.1x_3 + 1.5 \\
x_3 = 0.2x_1 + 0.4x_2 + 2
\end{cases}
$$

**Jacobi 迭代**（全部用旧值）：
$$
\begin{cases}
x_1^{(k+1)} = 0.2x_2^{(k)} + 0.1x_3^{(k)} + 0.3 \\
x_2^{(k+1)} = 0.2x_1^{(k)} + 0.1x_3^{(k)} + 1.5 \\
x_3^{(k+1)} = 0.2x_1^{(k)} + 0.4x_2^{(k)} + 2
\end{cases}
$$

**Gauss-Seidel 迭代**（用最新值）：
$$
\begin{cases}
x_1^{(k+1)} = 0.2x_2^{(k)} + 0.1x_3^{(k)} + 0.3 \\
x_2^{(k+1)} = 0.2x_1^{(k+1)} + 0.1x_3^{(k)} + 1.5 \\
x_3^{(k+1)} = 0.2x_1^{(k+1)} + 0.4x_2^{(k+1)} + 2
\end{cases}
$$

**Jacobi 迭代结果**（取初值 $\boldsymbol{x}^{(0)} = [0, 0, 0]^T$）：

| $k$ | $x_1^{(k)}$ | $x_2^{(k)}$ | $x_3^{(k)}$ |
|:---:|:---:|:---:|:---:|
| 0 | 0.0000 | 0.0000 | 0.0000 |
| 1 | 0.3000 | 1.5000 | 2.0000 |
| 2 | 0.8000 | 1.7600 | 2.6600 |
| 3 | 0.9180 | 1.9260 | 2.8640 |
| 4 | 0.9716 | 1.9700 | 2.9540 |
| 5 | 0.9894 | 1.9897 | 2.9823 |
| 6 | 0.9963 | 1.9961 | 2.9938 |
| 7 | 0.9986 | 1.9986 | 2.9977 |
| 8 | 0.9995 | 1.9995 | 2.9992 |
| 9 | 0.9998 | 1.9998 | 2.9998 |

**Gauss-Seidel 迭代结果**：

| $k$ | $x_1^{(k)}$ | $x_2^{(k)}$ | $x_3^{(k)}$ |
|:---:|:---:|:---:|:---:|
| 0 | 0.00000 | 0.00000 | 0.00000 |
| 1 | 0.30000 | 1.56000 | 2.68400 |
| 2 | 0.88040 | 1.94448 | 2.95387 |
| 3 | 0.98428 | 1.99224 | 2.99375 |
| 4 | 0.99782 | 1.99894 | 2.99914 |
| 5 | 0.99970 | 1.99985 | 2.99988 |
| 6 | 0.99996 | 1.99998 | 2.99998 |

**结论**：Gauss-Seidel 迭代法比 Jacobi 迭代法收敛更快（6步达到精度 vs 9步）。

### 迭代法的矩阵形式

**矩阵分裂**：将矩阵 $A$ 分裂为 $A = L + D + U$，其中：
- $D$ 为对角矩阵（diagonal）
- $L$ 为严格下三角矩阵（lower triangular，不含对角线元）
- $U$ 为严格上三角矩阵（upper triangular，不含对角线元）

**Jacobi 迭代的矩阵形式**：
$$\boldsymbol{x}^{(k+1)} = -D^{-1}(L+U)\boldsymbol{x}^{(k)} + D^{-1}\boldsymbol{b}$$

即：
$$\boldsymbol{x}^{(k+1)} = B_J \boldsymbol{x}^{(k)} + \boldsymbol{f}_J$$

其中 $B_J = -D^{-1}(L+U)$ 称为 **Jacobi 迭代阵**，$\boldsymbol{f}_J = D^{-1}\boldsymbol{b}$。

**Gauss-Seidel 迭代的矩阵形式**：
$$(D+L)\boldsymbol{x}^{(k+1)} = -U\boldsymbol{x}^{(k)} + \boldsymbol{b}$$

$$\boldsymbol{x}^{(k+1)} = -(D+L)^{-1}U\boldsymbol{x}^{(k)} + (D+L)^{-1}\boldsymbol{b}$$

即：
$$\boldsymbol{x}^{(k+1)} = B_{GS} \boldsymbol{x}^{(k)} + \boldsymbol{f}_{GS}$$

其中 $B_{GS} = -(D+L)^{-1}U$ 称为 **Gauss-Seidel 迭代阵**，$\boldsymbol{f}_{GS} = (D+L)^{-1}\boldsymbol{b}$。

### 两种迭代法的对比

1. **收敛速度**：一般而言，Gauss-Seidel 迭代法收敛速度比 Jacobi 迭代法快
2. **存储要求**：
   - Jacobi 迭代法：需存放 $\boldsymbol{x}^{(k)}$ 和 $\boldsymbol{x}^{(k+1)}$ 两个存储空间
   - Gauss-Seidel 迭代法：只需一个向量存储空间
3. **并行性**：
   - Jacobi 迭代法：公式简单，特别适合于并行计算
   - Gauss-Seidel 迭代法：是一种典型的串行算法
4. **收敛性**：两种方法都存在收敛性问题
   - 有例子表明：Gauss-Seidel 法收敛时，Jacobi 法可能不收敛
   - 反之亦然：Jacobi 法收敛时，Gauss-Seidel 法也可能不收敛

### 向量范数

**向量范数**用于误差的度量。

**向量范数的定义**（$\mathbb{R}^n$ 空间的向量范数 $\|\cdot\|$ 对任意 $\boldsymbol{x}, \boldsymbol{y} \in \mathbb{R}^n$ 满足）：
1. **正定性**：$\|\boldsymbol{x}\| \geq 0$，且 $\|\boldsymbol{x}\| = 0 \iff \boldsymbol{x} = \boldsymbol{0}$
2. **齐次性**：$\|\alpha\boldsymbol{x}\| = |\alpha|\|\boldsymbol{x}\|$，对任意 $\alpha \in \mathbb{C}$
3. **三角不等式**：$\|\boldsymbol{x} + \boldsymbol{y}\| \leq \|\boldsymbol{x}\| + \|\boldsymbol{y}\|$

**常用向量范数**：

- **1-范数**：$\|\boldsymbol{x}\|_1 = \sum_{i=1}^n |x_i|$
- **2-范数（欧氏范数）**：$\|\boldsymbol{x}\|_2 = \sqrt{\sum_{i=1}^n x_i^2}$
- **$p$-范数**：$\|\boldsymbol{x}\|_p = \left(\sum_{i=1}^n |x_i|^p\right)^{1/p}$
- **$\infty$-范数（最大范数）**：$\|\boldsymbol{x}\|_\infty = \max_{1 \leq i \leq n} |x_i|$

注：$\lim_{p \to \infty} \|\boldsymbol{x}\|_p = \|\boldsymbol{x}\|_\infty$

### 向量序列的收敛与范数等价

**向量序列收敛的定义**：
向量序列 $\{\boldsymbol{x}^{(k)}\}$ 收敛于向量 $\boldsymbol{x}^*$ 是指对每一个 $1 \leq i \leq n$ 都有：
$$\lim_{k \to \infty} x_i^{(k)} = x_i^*$$

可以理解为 $\lim_{k \to \infty} \|\boldsymbol{x}^{(k)} - \boldsymbol{x}^*\| = 0$。

**范数的强弱**：
- 若存在常数 $C > 0$ 使得对任意 $\boldsymbol{x} \in \mathbb{R}^n$ 有 $\|\boldsymbol{x}\|_A \leq C\|\boldsymbol{x}\|_B$，则称范数 $\|\cdot\|_A$ 比 $\|\cdot\|_B$ 强
- 若 $\|\cdot\|_A$ 比 $\|\cdot\|_B$ 强，且 $\|\cdot\|_B$ 也比 $\|\cdot\|_A$ 强，则称两范数等价

**重要定理**：$\mathbb{R}^n$ 上一切范数都等价。
即存在常数 $C_1, C_2 > 0$ 使得：
$$C_1\|\boldsymbol{x}\|_B \leq \|\boldsymbol{x}\|_A \leq C_2\|\boldsymbol{x}\|_B$$

### 矩阵范数

**矩阵范数的定义**（$\mathbb{R}^{m \times n}$ 空间的矩阵范数 $\|\cdot\|$ 对任意 $A, B \in \mathbb{R}^{m \times n}$ 满足）：
1. **正定性**：$\|A\| \geq 0$，且 $\|A\| = 0 \iff A = 0$
2. **齐次性**：$\|\alpha A\| = |\alpha|\|A\|$，对任意 $\alpha \in \mathbb{C}$
3. **三角不等式**：$\|A + B\| \leq \|A\| + \|B\|$
4. **相容性**（当 $m=n$ 时）：$\|AB\| \leq \|A\| \cdot \|B\|$

**算子范数**（由向量范数诱导的矩阵范数）：

- **行和范数**（$\infty$-范数）：
  $$\|A\|_\infty = \max_{1 \leq i \leq n} \sum_{j=1}^n |a_{ij}|$$

- **列和范数**（1-范数）：
  $$\|A\|_1 = \max_{1 \leq j \leq n} \sum_{i=1}^n |a_{ij}|$$

- **2-范数（谱范数）**：
  $$\|A\|_2 = \sqrt{\lambda_{\max}(A^T A)}$$
  其中 $\lambda_{\max}(A^T A)$ 表示 $A^T A$ 的最大特征值。

### 谱半径

**谱半径的定义**：矩阵 $A$ 的谱半径记为：
$$\rho(A) = \max_{1 \leq i \leq n} |\lambda_i|$$

其中 $\lambda_i$ 为 $A$ 的特征根。

### 谱半径相关定理

**定理 1**：对任意算子范数 $\|\cdot\|$，有：
$$\rho(A) \leq \|A\|$$

**证明**：设 $\lambda$ 是 $A$ 的任一特征根，$\boldsymbol{u}$ 为对应的特征向量。
由算子范数的相容性：$\|A\boldsymbol{u}\| \leq \|A\|\|\boldsymbol{u}\|$
但 $A\boldsymbol{u} = \lambda\boldsymbol{u}$，所以 $\|A\boldsymbol{u}\| = |\lambda|\|\boldsymbol{u}\|$
故 $|\lambda|\|\boldsymbol{u}\| \leq \|A\|\|\boldsymbol{u}\|$，即 $|\lambda| \leq \|A\|$
由于 $\lambda$ 任意，所以 $\rho(A) \leq \|A\|$。

**定理 2**：若 $A$ 对称，则有 $\|A\|_2 = \rho(A)$

**证明**：$\|A\|_2 = \sqrt{\lambda_{\max}(A^T A)} = \sqrt{\lambda_{\max}(A^2)}$（因为 $A$ 对称，$A^T = A$）
若 $\lambda$ 是 $A$ 的一个特征根，则 $\lambda^2$ 必是 $A^2$ 的特征根。
又：对称矩阵的特征根为实数，即 $\lambda(A^2)$ 为非负实数，故：
$$\lambda_{\max}(A^2) = [\lambda_{\max}(A)]^2$$
所以 $\|A\|_2 = \lambda_{\max}(A) = \rho(A)$。

因此，2-范数也称为**谱范数**（spectral norm）。

## 三、解题通法

### 1. 迭代法统一形式

把线性方程组化为
$$
x^{(k+1)}=Bx^{(k)}+f.
$$

收敛的核心条件是
$$
\rho(B)<1.
$$

### 2. Jacobi 迭代

分量形式：
$$
x_i^{(k+1)}=\frac{1}{a_{ii}}\left(b_i-\sum_{j\ne i}a_{ij}x_j^{(k)}\right).
$$

矩阵形式：
$$
B_J=-D^{-1}(L+U),\quad f_J=D^{-1}b.
$$

### 3. Gauss-Seidel 迭代

分量形式：
$$
x_i^{(k+1)}=\frac{1}{a_{ii}}\left(b_i-\sum_{j<i}a_{ij}x_j^{(k+1)}-\sum_{j>i}a_{ij}x_j^{(k)}\right).
$$

矩阵形式：
$$
B_{GS}=-(D+L)^{-1}U.
$$

### 4. 收敛判断

常用充分条件：

- 若 $\|B\|<1$，则收敛。
- 若 $A$ 严格对角占优，Jacobi 和 Gauss-Seidel 通常收敛。
- 若 $A$ 对称正定，Gauss-Seidel 收敛。

### 5. 易错点

- Jacobi 使用上一轮所有分量，G-S 新算出的分量立即使用。
- 判断收敛看迭代矩阵，不是看 $A$ 本身的范数。
- 初值影响迭代过程，但不改变收敛时的精确解。
