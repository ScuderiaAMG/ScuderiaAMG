# 第六章 线性方程组求解 - 课件例题

---

## NA06a 消元法

### 例 1：用高斯消元法求解线性方程组
（对应PDF第4-5页）

**题目**：用高斯消元法求解下列三阶线性方程组

$$
\begin{cases}
x_1 + 2x_2 + 3x_3 = 9 & \quad (I) \\
2x_1 + 5x_2 + 2x_3 = 18 & \quad (II) \\
3x_1 + 3x_2 + 4x_3 = -7 & \quad (III)
\end{cases}
$$

**解**：

**第 1 步：消去 $x_1$（从第 II、III 方程中）**

计算乘数（multiplier）：

$$
m_{21} = \frac{a_{21}}{a_{11}} = \frac{2}{1} = 2, \quad
m_{31} = \frac{a_{31}}{a_{11}} = \frac{3}{1} = 3
$$

将第 II 式减去 $m_{21}$ 倍的第 I 式，第 III 式减去 $m_{31}$ 倍的第 I 式：

新第 II 式：
$$
(2-2\times1)x_1 + (5-2\times2)x_2 + (2-2\times3)x_3 = 18 - 2\times9
$$
$$
\Rightarrow 0\cdot x_1 + 1\cdot x_2 + (-4)x_3 = 0
$$

新第 III 式：
$$
(3-3\times1)x_1 + (3-3\times2)x_2 + (4-3\times3)x_3 = -7 - 3\times9
$$
$$
\Rightarrow 0\cdot x_1 + (-3)x_2 + (-5)x_3 = -34
$$

消元后得到同解方程组：

$$
\begin{cases}
x_1 + 2x_2 + 3x_3 = 9 & (I) \\
x_2 - 4x_3 = 0 & (II) \\
-3x_2 - 5x_3 = -34 & (III)
\end{cases}
$$

**第 2 步：消去 $x_2$（从第 III 方程中）**

计算乘数：

$$
m_{32} = \frac{a_{32}^{(2)}}{a_{22}^{(2)}} = \frac{-3}{1} = -3
$$

将第 III 式减去 $m_{32}$ 倍的第 II 式：

新第 III 式：
$$
0\cdot x_1 + 0\cdot x_2 + (-5 - (-3)\times(-4))x_3 = -34 - (-3)\times0
$$
$$
\Rightarrow 0\cdot x_1 + 0\cdot x_2 + (-5 - 12)x_3 = -34
$$
$$
\Rightarrow -17x_3 = -34
$$

消元后得到上三角方程组：

$$
\begin{cases}
x_1 + 2x_2 + 3x_3 = 9 & (I) \\
x_2 - 4x_3 = 0 & (II) \\
-17x_3 = -34 & (III)
\end{cases}
$$

**第 3 步：回代求解（back substitution）**

由 (III) 式：
$$
-17x_3 = -34 \quad\Rightarrow\quad x_3 = \frac{-34}{-17} = 2
$$

代入 (II) 式：
$$
x_2 - 4\times2 = 0 \quad\Rightarrow\quad x_2 = 8
$$

代入 (I) 式：
$$
x_1 + 2\times8 + 3\times2 = 9 \quad\Rightarrow\quad x_1 + 16 + 6 = 9 \quad\Rightarrow\quad x_1 = -13
$$

**答案**：
$$
x_1 = -13,\quad x_2 = 8,\quad x_3 = 2
$$

---

### 例 2：单精度计算中的小主元问题
（对应PDF第8页）

**题目**：用单精度浮点数解方程组

$$
\begin{cases}
10^{-9}x_1 + x_2 = 1 \\
x_1 + x_2 = 2
\end{cases}
$$

**解**：

该方程组的精确解为：
$$
x_1 = \frac{1}{1 - 10^{-9}} = 1.\underbrace{00\ldots01}_{9\text{位}} ,\quad
x_2 = \frac{2 - 10^{-9}}{1 - 10^{-9}} = 0.\underbrace{99\ldots99}_{9\text{位}}
$$

即 $x_1 \approx 1$，$x_2 \approx 1$。

用 Gaussian Elimination 计算（不选主元）：

增广矩阵为：
$$
\begin{bmatrix}
10^{-9} & 1 & 1 \\
1 & 1 & 2
\end{bmatrix}
$$

第 1 步：$m_{21} = \frac{a_{21}}{a_{11}} = \frac{1}{10^{-9}} = 10^9$

新第 2 行：第 2 行 $- 10^9 \times$ 第 1 行
$$
a_{22}^{(2)} = 1 - 10^9 \times 1 = 1 - 10^9 \approx -10^9\ (\text{单精度下})
$$
$$
b_{2}^{(2)} = 2 - 10^9 \times 1 = 2 - 10^9 \approx -10^9\ (\text{单精度下})
$$

得到：
$$
\begin{bmatrix}
10^{-9} & 1 & 1 \\
0 & -10^9 & -10^9
\end{bmatrix}
$$

回代求解：
$$
x_2 = \frac{-10^9}{-10^9} = 1, \quad
x_1 = \frac{1 - 1\times1}{10^{-9}} = 0
$$

**分析**：由于主元 $10^{-9}$ 是一个极小的数（小主元），导致 $m_{21}=10^9$ 非常大，在相减过程中严重放大了舍入误差，最终得到 $x_1=0$ 的错误结果。这说明了选主元（pivoting）的必要性。

**答案**（精确解）：$x_1 \approx 1.000000001$，$x_2 \approx 0.999999999$  
**答案**（高斯消元不选主元）：$x_1 = 0$，$x_2 = 1$（错误）

---

### 例 3：列主元消去法
（对应PDF第10页）

**题目**：用列主元消去法解方程组

$$
\begin{bmatrix}
1 & 1 \\
1 & 10^{-9}
\end{bmatrix}
\begin{bmatrix}
x_1 \\
x_2
\end{bmatrix}
=
\begin{bmatrix}
2 \\
1
\end{bmatrix}
$$

**解**：

增广矩阵为：
$$
\begin{bmatrix}
1 & 1 & 2 \\
1 & 10^{-9} & 1
\end{bmatrix}
$$

**选主元**：比较第 1 列元素，$|a_{11}|=1$，$|a_{21}|=1$，绝对值相等，取第 1 行第 1 列为主元，无需换行。

**第 1 步**：$m_{21} = \frac{a_{21}}{a_{11}} = \frac{1}{1} = 1$

新第 2 行：第 2 行 $- 1 \times$ 第 1 行
$$
a_{22}^{(2)} = 10^{-9} - 1 \approx -1, \quad b_{2}^{(2)} = 1 - 2 = -1
$$

得到：
$$
\begin{bmatrix}
1 & 1 & 2 \\
0 & -1 & -1
\end{bmatrix}
$$

**回代**：
$$
x_2 = \frac{-1}{-1} = 1, \quad x_1 = \frac{2 - 1\times1}{1} = 1
$$

**答案**：$x_1 = 1$，$x_2 = 1$

---

### 例 4：列主元消去法（另一例）
（对应PDF第10页）

**题目**：用列主元消去法解方程组

$$
\begin{bmatrix}
10^9 & 1 \\
1 & 1
\end{bmatrix}
\begin{bmatrix}
x_1 \\
x_2
\end{bmatrix}
=
\begin{bmatrix}
2 \\
1
\end{bmatrix}
$$

**解**：

增广矩阵为：
$$
\begin{bmatrix}
10^9 & 1 & 2 \\
1 & 1 & 1
\end{bmatrix}
$$

**选主元**：比较第 1 列元素，$|10^9| > |1|$，因此选择 $10^9$ 作为主元，不需换行。

**第 1 步**：$m_{21} = \frac{a_{21}}{a_{11}} = \frac{1}{10^9} = 10^{-9}$

新第 2 行：第 2 行 $- 10^{-9} \times$ 第 1 行
$$
a_{22}^{(2)} = 1 - 10^{-9} \times 1 \approx 1, \quad b_{2}^{(2)} = 1 - 10^{-9} \times 2 \approx 1
$$

得到：
$$
\begin{bmatrix}
10^9 & 1 & 2 \\
0 & 1 & 1
\end{bmatrix}
$$

**回代**：
$$
x_2 = 1, \quad x_1 = \frac{2 - 1\times1}{10^9} \approx 10^{-9}
$$

**注意**：这两个方程组在数学上严格等价。采用列主元消去法能有效避免小主元问题。

---

## NA06b 三角分解法

（此节PDF内容以理论推导为主，包含LU分解、Doolittle分解、平方根法、追赶法的公式推导，未提供完整的数值例题）

### 例 1：Doolittle 分解法
（对应PDF第4-5页）

**题目**：用 Doolittle 分解法将矩阵 $A$ 分解为 $LU$，其中 $L$ 为单位下三角阵，$U$ 为上三角阵，并求解 $Ax=b$。

$$
A = \begin{pmatrix}
2 & 1 & 1 \\
4 & 5 & 2 \\
2 & 3 & 6
\end{pmatrix},\quad
b = \begin{pmatrix}
4 \\
11 \\
11
\end{pmatrix}
$$

**解**：

设 $A = LU$，其中：
$$
L = \begin{pmatrix}
1 & 0 & 0 \\
l_{21} & 1 & 0 \\
l_{31} & l_{32} & 1
\end{pmatrix},\quad
U = \begin{pmatrix}
u_{11} & u_{12} & u_{13} \\
0 & u_{22} & u_{23} \\
0 & 0 & u_{33}
\end{pmatrix}
$$

按照 Doolittle 分解法，先计算 $U$ 的第 1 行和 $L$ 的第 1 列，然后依次计算 $U$ 的第 $i$ 行和 $L$ 的第 $i$ 列。

**计算 $U$ 的第 1 行**（$j = 1, 2, 3$）：
$$
u_{1j} = a_{1j}
$$
$$
u_{11} = 2,\quad u_{12} = 1,\quad u_{13} = 1
$$

**计算 $L$ 的第 1 列**（$i = 2, 3$）：
$$
l_{i1} = \frac{a_{i1}}{u_{11}}
$$
$$
l_{21} = \frac{a_{21}}{u_{11}} = \frac{4}{2} = 2,\quad
l_{31} = \frac{a_{31}}{u_{11}} = \frac{2}{2} = 1
$$

**计算 $U$ 的第 2 行**（$j = 2, 3$）：
$$
u_{2j} = a_{2j} - l_{21} \cdot u_{1j}
$$
$$
u_{22} = a_{22} - l_{21} \cdot u_{12} = 5 - 2 \times 1 = 3
$$
$$
u_{23} = a_{23} - l_{21} \cdot u_{13} = 2 - 2 \times 1 = 0
$$

**计算 $L$ 的第 2 列**（$i = 3$）：
$$
l_{32} = \frac{a_{32} - l_{31} \cdot u_{12}}{u_{22}} = \frac{3 - 1 \times 1}{3} = \frac{2}{3}
$$

**计算 $U$ 的第 3 行**（$j = 3$）：
$$
u_{33} = a_{33} - (l_{31} \cdot u_{13} + l_{32} \cdot u_{23}) = 6 - (1 \times 1 + \frac{2}{3} \times 0) = 5
$$

所以分解结果为：
$$
L = \begin{pmatrix}
1 & 0 & 0 \\
2 & 1 & 0 \\
1 & \frac{2}{3} & 1
\end{pmatrix},\quad
U = \begin{pmatrix}
2 & 1 & 1 \\
0 & 3 & 0 \\
0 & 0 & 5
\end{pmatrix}
$$

验证：$LU = A$
$$
\begin{pmatrix}
1 & 0 & 0 \\
2 & 1 & 0 \\
1 & \frac{2}{3} & 1
\end{pmatrix}
\begin{pmatrix}
2 & 1 & 1 \\
0 & 3 & 0 \\
0 & 0 & 5
\end{pmatrix}
=
\begin{pmatrix}
2 & 1 & 1 \\
4 & 5 & 2 \\
2 & 3 & 6
\end{pmatrix}
= A \quad \checkmark
$$

**求解 $Ly = b$**（前代 forward substitution）：
$$
\begin{cases}
y_1 = 4 \\
2y_1 + y_2 = 11 \Rightarrow y_2 = 11 - 8 = 3 \\
y_1 + \frac{2}{3}y_2 + y_3 = 11 \Rightarrow y_3 = 11 - 4 - 2 = 5
\end{cases}
$$
即 $y = (4, 3, 5)^T$。

**求解 $Ux = y$**（回代 backward substitution）：
$$
\begin{cases}
5x_3 = 5 \Rightarrow x_3 = 1 \\
3x_2 + 0\cdot x_3 = 3 \Rightarrow x_2 = 1 \\
2x_1 + x_2 + x_3 = 4 \Rightarrow 2x_1 = 4 - 1 - 1 = 2 \Rightarrow x_1 = 1
\end{cases}
$$

**答案**：$x = (1, 1, 1)^T$

---

## NA06c 迭代法

### 例 1：Jacobi 迭代法
（对应PDF第6-7页）

**题目**：用 Jacobi 迭代法求解下列线性方程组

$$
\begin{cases}
10x_1 + 3x_2 + x_3 = 14 \\
2x_1 - 10x_2 + 3x_3 = -5 \\
x_1 + 3x_2 + 10x_3 = 14
\end{cases}
$$

**解**：

**第 1 步：将方程组化为等价形式 $x = Bx + f$**

从每个方程中分别解出 $x_1, x_2, x_3$：

$$
\begin{cases}
x_1 = \dfrac{14 - 3x_2 - x_3}{10} = -0.3x_2 - 0.1x_3 + 1.4 \\[6pt]
x_2 = \dfrac{-5 - 2x_1 + 3x_3}{-10} = 0.2x_1 + 0.3x_3 + 0.5 \\[6pt]
x_3 = \dfrac{14 - x_1 - 3x_2}{10} = -0.1x_1 - 0.3x_2 + 1.4
\end{cases}
$$

**第 2 步：建立 Jacobi 迭代格式**

$$
\begin{cases}
x_1^{(k+1)} = -0.3x_2^{(k)} - 0.1x_3^{(k)} + 1.4 \\[4pt]
x_2^{(k+1)} = 0.2x_1^{(k)} + 0.3x_3^{(k)} + 0.5 \\[4pt]
x_3^{(k+1)} = -0.1x_1^{(k)} - 0.3x_2^{(k)} + 1.4
\end{cases}
\quad k = 0, 1, 2, \ldots
$$

**第 3 步：取初值 $x^{(0)} = (0, 0, 0)^T$，迭代计算**

$k = 1$：
$$
x_1^{(1)} = -0.3\times0 - 0.1\times0 + 1.4 = 1.4
$$
$$
x_2^{(1)} = 0.2\times0 + 0.3\times0 + 0.5 = 0.5
$$
$$
x_3^{(1)} = -0.1\times0 - 0.3\times0 + 1.4 = 1.4
$$

$k = 2$：
$$
x_1^{(2)} = -0.3\times0.5 - 0.1\times1.4 + 1.4 = -0.15 - 0.14 + 1.4 = 1.11
$$
$$
x_2^{(2)} = 0.2\times1.4 + 0.3\times1.4 + 0.5 = 0.28 + 0.42 + 0.5 = 1.20
$$
$$
x_3^{(2)} = -0.1\times1.4 - 0.3\times0.5 + 1.4 = -0.14 - 0.15 + 1.4 = 1.11
$$

$k = 3$：
$$
x_1^{(3)} = -0.3\times1.20 - 0.1\times1.11 + 1.4 = -0.36 - 0.111 + 1.4 = 0.929
$$
$$
x_2^{(3)} = 0.2\times1.11 + 0.3\times1.11 + 0.5 = 0.222 + 0.333 + 0.5 = 1.055
$$
$$
x_3^{(3)} = -0.1\times1.11 - 0.3\times1.20 + 1.4 = -0.111 - 0.36 + 1.4 = 0.929
$$

$k = 4$：
$$
x_1^{(4)} = -0.3\times1.055 - 0.1\times0.929 + 1.4 = -0.3165 - 0.0929 + 1.4 = 0.9906
$$
$$
x_2^{(4)} = 0.2\times0.929 + 0.3\times0.929 + 0.5 = 0.1858 + 0.2787 + 0.5 = 0.9645
$$
$$
x_3^{(4)} = -0.1\times0.929 - 0.3\times1.055 + 1.4 = -0.0929 - 0.3165 + 1.4 = 0.9906
$$

继续迭代，逐步逼近精确解。

**精确解**：$x_1 = 1,\ x_2 = 1,\ x_3 = 1$

迭代结果汇总：

| $k$ | $x_1^{(k)}$ | $x_2^{(k)}$ | $x_3^{(k)}$ |
|-----|-------------|-------------|-------------|
| 0   | 0           | 0           | 0           |
| 1   | 1.4         | 0.5         | 1.4         |
| 2   | 1.11        | 1.20        | 1.11        |
| 3   | 0.929       | 1.055       | 0.929       |
| 4   | 0.9906      | 0.9645      | 0.9906      |

---

### 例 2：Jacobi 与 Gauss-Seidel 迭代法对比
（对应PDF第10-12页）

**题目**：分别用 Jacobi 迭代法和 Gauss-Seidel 迭代法求解方程组

$$
\begin{cases}
10x_1 - x_2 - 2x_3 = 3 \\
-2x_1 + 10x_2 - x_3 = 15 \\
-x_1 - 2x_2 + 5x_3 = 10
\end{cases}
$$

**解**：

**第 1 步：将方程组化为等价形式**

从每个方程中分别解出 $x_1, x_2, x_3$：

$$
\begin{cases}
x_1 = \dfrac{3 + x_2 + 2x_3}{10} = 0.1x_2 + 0.2x_3 + 0.3 \\[6pt]
x_2 = \dfrac{15 + 2x_1 + x_3}{10} = 0.2x_1 + 0.1x_3 + 1.5 \\[6pt]
x_3 = \dfrac{10 + x_1 + 2x_2}{5} = 0.2x_1 + 0.4x_2 + 2
\end{cases}
$$

**第 2 步：建立 Jacobi 迭代格式**

$$
\begin{cases}
x_1^{(k+1)} = 0.2x_2^{(k)} + 0.1x_3^{(k)} + 0.3 \\
x_2^{(k+1)} = 0.2x_1^{(k)} + 0.1x_3^{(k)} + 1.5 \\
x_3^{(k+1)} = 0.2x_1^{(k)} + 0.4x_2^{(k)} + 2
\end{cases}
$$

**建立 Gauss-Seidel 迭代格式**

在 Gauss-Seidel 法中，计算 $x_i^{(k+1)}$ 时使用已经计算出的最新分量：

$$
\begin{cases}
x_1^{(k+1)} = 0.2x_2^{(k)} + 0.1x_3^{(k)} + 0.3 \\
x_2^{(k+1)} = 0.2x_1^{(k+1)} + 0.1x_3^{(k)} + 1.5 \\
x_3^{(k+1)} = 0.2x_1^{(k+1)} + 0.4x_2^{(k+1)} + 2
\end{cases}
$$

**第 3 步：取初值 $x^{(0)} = (0, 0, 0)^T$，分别迭代**

**Jacobi 迭代结果**：

| $k$ | $x_1^{(k)}$ | $x_2^{(k)}$ | $x_3^{(k)}$ |
|-----|-------------|-------------|-------------|
| 0   | 0.0000      | 0.0000      | 0.0000      |
| 1   | 0.3000      | 1.5000      | 2.0000      |
| 2   | 0.8000      | 1.7600      | 2.6600      |
| 3   | 0.9180      | 1.9260      | 2.8640      |
| 4   | 0.9716      | 1.9700      | 2.9540      |
| 5   | 0.9894      | 1.9897      | 2.9823      |
| 6   | 0.9963      | 1.9961      | 2.9938      |
| 7   | 0.9986      | 1.9986      | 2.9977      |
| 8   | 0.9995      | 1.9995      | 2.9992      |
| 9   | 0.9998      | 1.9998      | 2.9998      |

**Gauss-Seidel 迭代结果**：

| $k$ | $x_1^{(k)}$ | $x_2^{(k)}$ | $x_3^{(k)}$ |
|-----|-------------|-------------|-------------|
| 0   | 0.00000     | 0.00000     | 0.00000     |
| 1   | 0.30000     | 1.56000     | 2.68400     |
| 2   | 0.88040     | 1.94448     | 2.95387     |
| 3   | 0.98428     | 1.99224     | 2.99375     |
| 4   | 0.99782     | 1.99894     | 2.99914     |
| 5   | 0.99970     | 1.99985     | 2.99988     |
| 6   | 0.99996     | 1.99998     | 2.99998     |

**分析**：
- Gauss-Seidel 迭代法在第 5 次迭代后已非常接近精确解，而 Jacobi 迭代法需要更多迭代。
- 一般来说，Gauss-Seidel 迭代法收敛速度比 Jacobi 迭代法快。
- Jacobi 迭代法公式简单，适合并行计算；Gauss-Seidel 迭代法只需一个向量存储空间。

**精确解**：$x_1 = 1,\ x_2 = 2,\ x_3 = 3$

---

## NA06d 迭代法的收敛性

### 例 1：判断 Jacobi 迭代的收敛性
（对应PDF第3-4页）

**题目**：判断线性方程组 Jacobi 迭代的收敛性

$$
\begin{cases}
8x_1 - 3x_2 + 2x_3 = 20 \\
4x_1 + 11x_2 - x_3 = 33 \\
6x_1 + 3x_2 + 12x_3 = 36
\end{cases}
$$

**解**：

**第 1 步：将方程组化为 Jacobi 迭代形式**

$$
\begin{cases}
x_1 = \dfrac{20}{8} + \dfrac{3}{8}x_2 - \dfrac{2}{8}x_3 = 2.5 + 0.375x_2 - 0.25x_3 \\[6pt]
x_2 = \dfrac{33}{11} - \dfrac{4}{11}x_1 + \dfrac{1}{11}x_3 = 3 - 0.3636x_1 + 0.0909x_3 \\[6pt]
x_3 = \dfrac{36}{12} - \dfrac{6}{12}x_1 - \dfrac{3}{12}x_2 = 3 - 0.5x_1 - 0.25x_2
\end{cases}
$$

Jacobi 迭代矩阵为：
$$
B_J = \begin{pmatrix}
0 & \frac{3}{8} & -\frac{2}{8} \\[4pt]
-\frac{4}{11} & 0 & \frac{1}{11} \\[4pt]
-\frac{6}{12} & -\frac{3}{12} & 0
\end{pmatrix}
$$

**第 2 步：计算迭代矩阵的谱半径**

方法一：求特征值

解 $|\lambda I - B_J| = 0$：
$$
\begin{vmatrix}
\lambda & -\frac{3}{8} & \frac{2}{8} \\[4pt]
\frac{4}{11} & \lambda & -\frac{1}{11} \\[4pt]
\frac{6}{12} & \frac{3}{12} & \lambda
\end{vmatrix} = 0
$$

计算得特征值：
$$
\lambda_1 = -0.3082,\quad \lambda_2 = 0.1541 + 0.3245i,\quad \lambda_3 = 0.1541 - 0.3245i
$$

谱半径：
$$
\rho(B_J) = \max\{|\lambda_1|, |\lambda_2|, |\lambda_3|\} = 0.3592 < 1
$$

方法二：计算矩阵范数（充分条件）

行和范数：
$$
\|B_J\|_{\infty} = \max\left\{\frac{5}{8}, \frac{5}{11}, \frac{9}{12}\right\} = \max\{0.625, 0.4545, 0.75\} = 0.75 < 1
$$

列和范数：
$$
\|B_J\|_1 = \max\left\{\frac{19}{22}, \frac{5}{8}, \frac{15}{44}\right\} = \max\{0.8636, 0.625, 0.3409\} = 0.8636 < 1
$$

两种方式均满足 $\rho(B_J) < 1$ 和 $\|B_J\| < 1$。

**结论**：该方程组采用 Jacobi 迭代法计算是收敛的。

---

### 例 2：松弛法的最优松弛因子
（对应PDF第9页）

**题目**：给定矩阵 $A = \begin{pmatrix} 1 & 2 \\ 2 & 1 \end{pmatrix}$ 和向量 $b = \begin{pmatrix} 1 \\ 2 \end{pmatrix}$，考虑迭代格式
$$
x^{(k+1)} = x^{(k)} + \omega(b - Ax^{(k)})
$$
问：（1）$\omega$ 取何值时迭代收敛？
（2）$\omega$ 取何值时迭代收敛最快？

**解**：

**迭代矩阵**：
$$
B = I + \omega A = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix} + \omega \begin{pmatrix} 1 & 2 \\ 2 & 1 \end{pmatrix}
= \begin{pmatrix} 1 + \omega & 2\omega \\ 2\omega & 1 + \omega \end{pmatrix}
$$

**计算特征值**：

$$
\begin{vmatrix}
1+\omega-\lambda & 2\omega \\
2\omega & 1+\omega-\lambda
\end{vmatrix} = 0
$$

$$
(1+\omega-\lambda)^2 - (2\omega)^2 = 0
$$

$$
[(1+\omega-\lambda) - 2\omega][(1+\omega-\lambda) + 2\omega] = 0
$$

$$
(1 - \omega - \lambda)(1 + 3\omega - \lambda) = 0
$$

所以特征值为：
$$
\lambda_1 = 1 + \omega,\quad \lambda_2 = 1 + 3\omega
$$

**（1）收敛条件**

迭代收敛 $\iff \rho(B) < 1 \iff \max\{|1+\omega|, |1+3\omega|\} < 1$

即：
$$
\begin{cases}
|1+\omega| < 1 & \Rightarrow -2 < \omega < 0 \\
|1+3\omega| < 1 & \Rightarrow -\frac{2}{3} < \omega < 0
\end{cases}
$$

取交集得：
$$
-\frac{2}{3} < \omega < 0
$$

**（2）最优松弛因子**

谱半径 $\rho(B) = \max\{|1+\omega|, |1+3\omega|\}$ 在 $\omega \in (-\frac{2}{3}, 0)$ 上的最小值。

比较两个函数：
- $|1+\omega|$ 在 $\omega \in [-\frac{2}{3}, 0]$ 上从 $\frac{1}{3}$ 递减到 $1$（下降），然后递增
- $|1+3\omega|$ 在 $\omega \in [-\frac{2}{3}, 0]$ 上从 $1$ 递减到 $1$（在 $\omega=-\frac{1}{3}$ 处为 $0$）

最优解在 $|1+\omega| = |1+3\omega|$ 时取得：
$$
|1+\omega| = |1+3\omega|
$$

在区间 $(-\frac{2}{3}, 0)$ 上，$1+\omega > 0$，$1+3\omega$ 在 $\omega = -\frac{1}{3}$ 处变号。

考虑 $\omega \in (-\frac{2}{3}, -\frac{1}{3})$：$1+\omega > 0$，$1+3\omega < 0$
$$
1+\omega = -(1+3\omega) \Rightarrow 1+\omega = -1-3\omega \Rightarrow 4\omega = -2 \Rightarrow \omega = -\frac{1}{2}
$$

考虑 $\omega \in (-\frac{1}{3}, 0)$：$1+\omega > 0$，$1+3\omega > 0$
$$
1+\omega = 1+3\omega \Rightarrow \omega = 0
$$

因此最优松弛因子为 $\omega = -\frac{1}{2}$，此时：
$$
\lambda_1 = 1 - \frac{1}{2} = \frac{1}{2},\quad \lambda_2 = 1 - \frac{3}{2} = -\frac{1}{2}
$$
$$
\rho(B) = \frac{1}{2}
$$

**答案**：
（1）收敛条件：$-\dfrac{2}{3} < \omega < 0$
（2）最优松弛因子：$\omega = -\dfrac{1}{2}$，此时谱半径最小为 $\dfrac{1}{2}$

---

### 例 3：判断 Jacobi 迭代和 Gauss-Seidel 迭代的收敛性
（对应PDF第11-12页）

**题目**：判别下列方程组用 Jacobi 迭代法和 Gauss-Seidel 迭代法求解是否收敛

$$
\begin{pmatrix}
1 & 2 & -2 \\
1 & 1 & 1 \\
2 & 2 & 1
\end{pmatrix}
\begin{pmatrix}
x_1 \\
x_2 \\
x_3
\end{pmatrix}
=
\begin{pmatrix}
1 \\
1 \\
1
\end{pmatrix}
$$

**解**：

**（1）Jacobi 迭代法的收敛性**

Jacobi 迭代格式：
$$
\begin{cases}
x_1^{(k+1)} = -2x_2^{(k)} + 2x_3^{(k)} + 1 \\
x_2^{(k+1)} = -x_1^{(k)} - x_3^{(k)} + 1 \\
x_3^{(k+1)} = -2x_1^{(k)} - 2x_2^{(k)} + 1
\end{cases}
$$

Jacobi 迭代矩阵：
$$
B_J = \begin{pmatrix}
0 & -2 & 2 \\
-1 & 0 & -1 \\
-2 & -2 & 0
\end{pmatrix}
$$

计算特征值：
$$
\begin{vmatrix}
\lambda I - B_J \end{vmatrix}
= \begin{vmatrix}
\lambda & 2 & -2 \\
1 & \lambda & 1 \\
2 & 2 & \lambda
\end{vmatrix} = 0
$$

展开行列式：
$$
\lambda(\lambda^2 - 2) - 2(\lambda - 2) + (-2)(2 - 2\lambda) = 0
$$

仔细计算：
$$
\begin{vmatrix}
\lambda & 2 & -2 \\
1 & \lambda & 1 \\
2 & 2 & \lambda
\end{vmatrix}
= \lambda(\lambda^2 - 2) - 2(\lambda - 2) + (-2)(2 - 2\lambda)
$$
$$
= \lambda^3 - 2\lambda - 2\lambda + 4 - 4 + 4\lambda
$$
$$
= \lambda^3
$$

所以 $\lambda_1 = \lambda_2 = \lambda_3 = 0$。

谱半径：
$$
\rho(B_J) = 0 < 1
$$

**结论**：Jacobi 迭代法收敛。

**（2）Gauss-Seidel 迭代法的收敛性**

Gauss-Seidel 迭代格式：
$$
\begin{cases}
x_1^{(k+1)} = -2x_2^{(k)} + 2x_3^{(k)} + 1 \\
x_2^{(k+1)} = -x_1^{(k+1)} - x_3^{(k)} + 1 \\
x_3^{(k+1)} = -2x_1^{(k+1)} - 2x_2^{(k+1)} + 1
\end{cases}
$$

将 $x_1^{(k+1)}$ 代入 $x_2^{(k+1)}$ 的表达式中，再将 $x_1^{(k+1)}, x_2^{(k+1)}$ 代入 $x_3^{(k+1)}$：

$$
\begin{cases}
x_1^{(k+1)} = -2x_2^{(k)} + 2x_3^{(k)} + 1 \\
x_2^{(k+1)} = -(-2x_2^{(k)} + 2x_3^{(k)} + 1) - x_3^{(k)} + 1 = 2x_2^{(k)} - 3x_3^{(k)} \\
x_3^{(k+1)} = -2(-2x_2^{(k)} + 2x_3^{(k)} + 1) - 2(2x_2^{(k)} - 3x_3^{(k)}) + 1 \\
\qquad = (4x_2^{(k)} - 4x_3^{(k)} - 2) + (-4x_2^{(k)} + 6x_3^{(k)}) + 1 = 2x_3^{(k)} - 1
\end{cases}
$$

所以 Gauss-Seidel 迭代法的矩阵形式为：
$$
x^{(k+1)} = B_G x^{(k)} + g
$$
其中：
$$
B_G = \begin{pmatrix}
0 & -2 & 2 \\
0 & 2 & -3 \\
0 & 0 & 2
\end{pmatrix}
$$

由于 $B_G$ 是上三角矩阵，特征值即对角线元素：
$$
\lambda_1 = 0,\quad \lambda_2 = 2,\quad \lambda_3 = 2
$$

谱半径：
$$
\rho(B_G) = 2 > 1
$$

**结论**：Gauss-Seidel 迭代法发散。

**对比**：
- Jacobi 迭代法的谱半径 $\rho(B_J) = 0 < 1$，收敛；
- Gauss-Seidel 迭代法的谱半径 $\rho(B_G) = 2 > 1$，发散。

这表明 Jacobi 收敛时，Gauss-Seidel 不一定收敛。

---

## NA06e 直接法的误差分析

### 例 1：Hilbert 矩阵的条件数
（对应PDF第5页）

**题目**：Hilbert 矩阵 $H_n$ 定义为 $h_{ij} = \dfrac{1}{i+j-1}$，计算其条件数。

$$
H_n = \begin{pmatrix}
1 & \frac{1}{2} & \frac{1}{3} & \cdots & \frac{1}{n} \\[4pt]
\frac{1}{2} & \frac{1}{3} & \frac{1}{4} & \cdots & \frac{1}{n+1} \\[4pt]
\frac{1}{3} & \frac{1}{4} & \frac{1}{5} & \cdots & \frac{1}{n+2} \\[4pt]
\vdots & \vdots & \vdots & \ddots & \vdots \\[4pt]
\frac{1}{n} & \frac{1}{n+1} & \frac{1}{n+2} & \cdots & \frac{1}{2n-1}
\end{pmatrix}
$$

**解**：

Hilbert 矩阵是著名的病态矩阵（ill-conditioned matrix）。

条件数（行和范数）：
$$
\text{cond}(H_2)_\infty = 27
$$
$$
\text{cond}(H_3)_\infty \approx 748
$$
$$
\text{cond}(H_6)_\infty = 2.9 \times 10^6
$$
$$
\text{cond}(H_n)_\infty \to \infty \quad \text{as} \quad n \to \infty
$$

**分析**：随着 $n$ 增大，Hilbert 矩阵的条件数急剧增大，说明矩阵越来越病态。对于 $n \ge 10$ 的 Hilbert 矩阵，用直接法求解线性方程组时，即使微小的扰动也会导致解的严重失真。

**判断矩阵病态程度的经验方法**：
- 行列式很大或很小（如某些行、列近似相关）；
- 元素间相差大数量级，且无规则；
- 主元消去过程中出现小主元；
- 特征值相差大数量级。

---

### 例 2：病态方程组的扰动分析
（对应PDF第6页）

**题目**：考虑方程组
$$
\begin{pmatrix}
1 & 1 \\
1 & 1.0001
\end{pmatrix}
\begin{pmatrix}
x \\
y
\end{pmatrix}
=
\begin{pmatrix}
2 \\
2.0001
\end{pmatrix}
$$
常数项微小扰动后变为
$$
\begin{pmatrix}
1 & 1 \\
1 & 1.0001
\end{pmatrix}
\begin{pmatrix}
x \\
y
\end{pmatrix}
=
\begin{pmatrix}
2 \\
2.0001
\end{pmatrix}
$$

**解**：

**原方程组的精确解**：
$$
\begin{cases}
x + y = 2 \\
x + 1.0001y = 2.0001
\end{cases}
$$

两式相减：
$$
(1.0001 - 1)y = 2.0001 - 2 \Rightarrow 0.0001y = 0.0001 \Rightarrow y = 1
$$

代入第一式：
$$
x + 1 = 2 \Rightarrow x = 1
$$

所以原方程组的精确解为 $x = (1, 1)^T$。

**常数项微小扰动后**：
当常数项发生微小变化时，解发生剧烈变化，说明该矩阵严重病态。

这个例子说明：当矩阵的条件数很大时，即使常数项的微小扰动也会导致解的剧烈变化。

---

### 例 3：条件数的计算
（对应PDF第7页）

**题目**：给定矩阵 $A = \begin{pmatrix} 1 & 0.99 \\ 0.99 & 0.98 \end{pmatrix}$ 和向量 $b = \begin{pmatrix} 1.99 \\ 1.97 \end{pmatrix}$，精确解为 $x = (1, 1)^T$。计算 $\text{cond}(A)_2$，并测试病态程度。

**解**：

**第 1 步：求特征值**

$$
|A - \lambda I| = \begin{vmatrix}
1-\lambda & 0.99 \\
0.99 & 0.98-\lambda
\end{vmatrix} = 0
$$

$$
(1-\lambda)(0.98-\lambda) - 0.99^2 = 0
$$

$$
\lambda^2 - 1.98\lambda + (0.98 - 0.9801) = 0
$$

$$
\lambda^2 - 1.98\lambda - 0.0001 = 0
$$

$$
\lambda = \frac{1.98 \pm \sqrt{1.98^2 + 0.0004}}{2}
= \frac{1.98 \pm \sqrt{3.9204 + 0.0004}}{2}
= \frac{1.98 \pm \sqrt{3.9208}}{2}
$$

$$
\lambda_1 = \frac{1.98 + 1.9801}{2} \approx 1.980050504
$$
$$
\lambda_2 = \frac{1.98 - 1.9801}{2} \approx -0.000050504
$$

**第 2 步：求条件数**

$$
\text{cond}(A)_2 = \sqrt{\frac{\lambda_{\max}(A^T A)}{\lambda_{\min}(A^T A)}}
= \frac{|\lambda_1|}{|\lambda_2|}
= \frac{1.980050504}{0.000050504}
\approx 39206 \gg 1
$$

条件数远大于 1，说明矩阵严重病态。

**第 3 步：测试病态程度**

给 $b$ 一个微小扰动：
$$
\delta b = \begin{pmatrix} -0.97 \times 10^{-4} \\ 0.106 \times 10^{-3} \end{pmatrix}
$$

相对误差：
$$
\frac{\|\delta b\|_2}{\|b\|_2} \approx 0.513 \times 10^{-4} < 0.01\%
$$

此时精确解变为：
$$
x^* = \begin{pmatrix} -3 \\ 1.0203 \end{pmatrix}
$$

解的相对误差：
$$
\frac{\|\delta x\|_2}{\|x\|_2} = \frac{\|x^* - x\|_2}{\|x\|_2}
= \frac{\|(-4, 0.0203)^T\|_2}{\|(1, 1)^T\|_2}
= \frac{\sqrt{16 + 0.0004}}{\sqrt{2}} \approx \frac{4.00005}{1.4142} \approx 2.828
> 200\%
$$

**分析**：常数项仅 $0.01\%$ 的扰动，导致解出现超过 $200\%$ 的相对误差。这就是条件数过大（病态矩阵）导致的严重后果。

---

## 汇总

| 章节 | 例题数量 | 知识点 |
|------|---------|--------|
| NA06a 消元法 | 4 | 高斯消元法、小主元问题、列主元消去法 |
| NA06b 三角分解法 | 1 | Doolittle LU分解、前代回代 |
| NA06c 迭代法 | 2 | Jacobi迭代、Gauss-Seidel迭代、收敛速度对比 |
| NA06d 迭代法的收敛性 | 3 | 谱半径、范数条件、松弛法、收敛性判断 |
| NA06e 误差分析 | 3 | Hilbert矩阵、条件数、病态方程组扰动分析 |
| **总计** | **13** | |
