# NA06b 三角分解法 — 知识点总结

> 原PDF来源：华中科技大学《计算方法》课程讲义 NA06b

---

## 一、通俗原理解释

### 1. 什么是三角分解法？

三角分解法是解线性方程组 $Ax = b$ 的一类**矩阵分解方法**。核心思想是：将系数矩阵 A 分解为两个（或三个）**三角形矩阵**的乘积（如 $A = LU$），然后利用三角方程组极易求解的特性，分两步求出解向量 x。

**直觉理解**：解一般线性方程组 $Ax = b$ 就像直接解一个复杂的谜题。而三角分解法先把这个谜题拆成两个简单的部分——"下三角"和"上三角"。解三角方程组就像顺着梯子一步一步走：下三角从前到后（**追**），上三角从后到前（**赶**），每一步只涉及一个未知数，非常简单。

### 2. 为什么要做三角分解？

- **一次分解，多次求解**：若 A 不变但 b 变化（如不同右端项），只需做一次 $A = LU$ 分解，之后每次求解只需两次回代（$O(n^2)$），而非每次重新消元（$O(n^3)$）。
- **揭示矩阵结构**：对称正定性、三对角性等特殊结构可导出更高效的专门分解方法。
- **计算稳定**：相比原始高斯消元法，分解法更规整，便于误差分析。

### 3. 各方法的通俗类比

#### 高斯消元 → LU 分解（Doolittle / Crout）
**类比**：就像工厂的流水线，高斯消元每次"手工"把矩阵消成上三角。而 LU 分解把消元过程"固化"为矩阵乘法——L 记录了每一步消元的操作（消元乘数），U 是最终的上三角结果。一次固化，反复使用。

#### 平方根法（Cholesky）— 对称正定阵的"专属通道"
**类比**：如果矩阵是对称正定的（如物理中的能量矩阵、最小二乘的法方程），它可以分解为 $A = LL^T$，就像一个正方形的面积可以写成边长的平方。由于只需算一个下三角阵 L，计算量和存储量都减半。

#### 改进平方根法（$LDL^T$）— "避免开方的巧思"
**类比**：Cholesky 的 $LL^T$ 需要开平方根（$\sqrt{\;}$），而开方运算既慢又有精度损失。改进方法将 A 分解为 $A = LDL^T$，其中 D 是对角阵，L 是单位下三角阵。完全避免了开方运算，相当于把开方"吸收"到了对角阵 D 中。

#### 追赶法（Crout 法解三对角阵）— "三对角的极速通道"
**类比**：三对角矩阵（只有主对角线和两条次对角线非零）就像一条只有三个车道的路。普通消元法在这条稀疏的路上做了大量"零的运算"（浪费）。追赶法专为三对角阵设计，两步完成：**追**（从前往后消元）→ **赶**（从后往前回代），计算量仅为 $O(n)$，是解大型三对角方程组的最优方法。

#### Doolittle vs Crout 的区别
- **Doolittle**：L 是**单位**下三角（对角元为 1），U 是一般上三角
- **Crout**：L 是一般下三角，U 是**单位**上三角（对角元为 1）
- 两者本质上等价，只是"归一化"的位置不同

---

## 二、PDF 知识点（完整梳理）

### 第1部分：高斯消元法的矩阵形式 → LU 分解（PDF 第1–3页）

#### 1.1 高斯消元的矩阵表示

**Step 1**：消去第一列
记 $m_{i1} = a_{i1}^{(1)} / a_{11}^{(1)}$（$a_{11} \neq 0$），构造消元矩阵：
$$L_1 = \begin{bmatrix} 1 & & & \\ -m_{21} & 1 & & \\ \vdots & & \ddots & \\ -m_{n1} & & & 1 \end{bmatrix}$$

则 $L_1 [A^{(1)} \mid b^{(1)}] = [A^{(2)} \mid b^{(2)}]$，$A^{(1)}$ 的第一列被消为零（除第一行外）。

**Step k**（第 k 步消元）：
$$L_k = \begin{bmatrix} 1 & & & & \\ & \ddots & & & \\ & & 1 & & \\ & & -m_{k+1,k} & \ddots & \\ & & \vdots & & 1 \end{bmatrix}$$

**Step n−1**：完成后得到：
$$L_{n-1}L_{n-2}\cdots L_1 [A^{(1)} \mid b^{(1)}] = \begin{bmatrix} a_{11}^{(1)} & a_{12}^{(1)} & \cdots & a_{1n}^{(1)} & b_1^{(1)} \\ & a_{22}^{(2)} & \cdots & a_{2n}^{(2)} & b_2^{(2)} \\ & & \ddots & \vdots & \vdots \\ & & & a_{nn}^{(n)} & b_n^{(n)} \end{bmatrix}$$

#### 1.2 从消元矩阵到 LU 分解

记：
$$L = L_1^{-1}L_2^{-1}\cdots L_{n-1}^{-1} = \begin{bmatrix} 1 & & & \\ m_{21} & 1 & & \\ \vdots & \vdots & \ddots & \\ m_{n1} & m_{n2} & \cdots & 1 \end{bmatrix}$$

L 是**单位下三角阵**（对角元全为 1）。

记：
$$U = \begin{bmatrix} a_{11}^{(1)} & a_{12}^{(1)} & \cdots & a_{1n}^{(1)} \\ & a_{22}^{(2)} & \cdots & a_{2n}^{(2)} \\ & & \ddots & \vdots \\ & & & a_{nn}^{(n)} \end{bmatrix}$$

U 是**上三角阵**。

**结论**：$A = LU$ —— 这就是矩阵的 **LU 分解**（Doolittle 分解）。

#### 1.3 Doolittle 分解与 Crout 分解

| 分解类型 | L | U |
|----------|---|---|
| **Doolittle** | **单位**下三角阵（对角元为 1） | 一般上三角阵 |
| **Crout** | 一般下三角阵 | **单位**上三角阵（对角元为 1） |

**注**：Crout 分解可通过 $A^*$ 的 Doolittle 分解得到，即若 $A^* = \tilde{L}\tilde{U}$（Doolittle），则 $A = \tilde{U}^*\tilde{L}^*$（Crout）。

---

### 第2部分：Doolittle 分解的紧凑格式（PDF 第4–6页）

#### 2.1 基本思路

**反复计算浪费** → 通过**直接比较法**导出 L 和 U 元素的计算公式。

将 $A = LU$ 展开：
$$\begin{bmatrix} a_{11} & \cdots & a_{1n} \\ \vdots & & \vdots \\ a_{n1} & \cdots & a_{nn} \end{bmatrix} = \begin{bmatrix} 1 & & \\ l_{21} & 1 & \\ \vdots & & \ddots & \\ l_{n1} & \cdots & & 1 \end{bmatrix} \begin{bmatrix} u_{11} & \cdots & u_{1n} \\ & \ddots & \vdots \\ & & u_{nn} \end{bmatrix}$$

元素关系：$a_{ij} = \sum_{k=1}^{\min(i, j)} l_{ik}u_{kj}$

#### 2.2 直接比较法导出计算公式

**U 的第一行**（$j = 1, \ldots, n$）：
$$u_{1j} = a_{1j}$$

**L 的第一列**（$i = 2, \ldots, n$）：
$$l_{i1} = a_{i1} / u_{11}$$

**U 的第二行**（$j = 2, \ldots, n$）：
$$u_{2j} = a_{2j} - l_{21}u_{1j}$$

**L 的第二列**（$i = 3, \ldots, n$）：
$$l_{i2} = (a_{i2} - l_{i1}u_{12}) / u_{22}$$

#### 2.3 一般计算公式

**第 i 步**（此时 U 的前 $i-1$ 行和 L 的前 $i-1$ 列已求出）：

**U 的第 i 行**（$j = i, i+1, \ldots, n$，注意 $l_{ii}=1$）：
$$u_{ij} = a_{ij} - \sum_{k=1}^{i-1} l_{ik}u_{kj}$$

**L 的第 i 列**（$j = i+1, \ldots, n$）：
$$l_{ji} = \left(a_{ji} - \sum_{k=1}^{i-1} l_{jk}u_{ki}\right) / u_{ii}$$

**最后一步（第 n 步）**：
$$u_{nn} = a_{nn} - \sum_{k=1}^{n-1} l_{nk}u_{kn}$$

#### 2.4 Doolittle 算法步骤

```
Step 1: u_{1j} = a_{1j};  l_{j1} = a_{j1} / u_{11};  (j = 1, ..., n)
Step 2: 对 i = 2, ..., n-1，依次计算 U 的第 i 行和 L 的第 i 列
Step 3: u_{nn} = a_{nn} - Σ_{k=1}^{n-1} l_{nk} u_{kn}
```

---

### 第3部分：平方根法 Cholesky 分解（PDF 第7–9页）

#### 3.1 对称正定矩阵的定义与性质

**定义**：
- **对称阵**：$A = (a_{ij})_{n\times n}$ 满足 $a_{ij} = a_{ji}$
- **正定阵**：对任意非零向量 $\vec{x}$，有 $\vec{x}^T A \vec{x} > 0$

**对称正定阵的重要性质**：
1. $A^{-1}$ 亦对称正定，且 $a_{ii} > 0$
2. A 的顺序主子阵 $A_k$ 亦对称正定
3. A 的特征值 $\lambda_i > 0$
4. A 的全部顺序主子式 $\det(A_k) > 0$

**证明 $a_{ii} > 0$**：取 $\vec{x} = (0, \ldots, 1, \ldots, 0)^T$（第 i 位为 1），则 $a_{ii} = \vec{x}^T A \vec{x} > 0$。

#### 3.2 Cholesky 分解定理

**定理**：设矩阵 A 对称正定，则存在**非奇异下三角阵** $L \in \mathbb{R}^{n \times n}$，使得：
$$A = LL^T$$

且若限定 L 的对角元为正，则分解是唯一的。

#### 3.3 推导过程

将对称正定阵 A 做 LU 分解：
$$U = \begin{bmatrix} u_{11} & & \\ & u_{22} & \\ & & \ddots \\ & & & u_{nn} \end{bmatrix} \begin{bmatrix} 1 & u_{12}/u_{11} & \cdots \\ & 1 & \cdots \\ & & \ddots \end{bmatrix} = D\tilde{U}$$

由于 A 对称，有 $L = \tilde{U}^T$，故：
$$A = LDL^T$$

记 $D^{1/2} = \text{diag}(\sqrt{u_{11}}, \sqrt{u_{22}}, \ldots, \sqrt{u_{nn}})$，令 $\tilde{L} = LD^{1/2}$，则：
$$A = \tilde{L}\tilde{L}^T$$

**为什么 $u_{ii} > 0$？** 因为 $\det(A_k) = u_{11}u_{22}\cdots u_{kk} > 0$，由顺序主子式大于 0 可推得。

#### 3.4 Cholesky 分解计算公式

直接比较 $A = LL^T$ 两边元素：

**第 1 个对角元**：$l_{11} = \sqrt{a_{11}}$

**第 1 列**（$j = 2, \ldots, n$）：$l_{j1} = a_{j1} / l_{11}$

**第 i 个对角元**（$i = 2, \ldots, n-1$）：
$$l_{ii} = \sqrt{a_{ii} - \sum_{k=1}^{i-1} l_{ik}^2}$$

**第 i 列**（$j = i+1, \ldots, n$）：
$$l_{ji} = \left(a_{ji} - \sum_{k=1}^{i-1} l_{jk}l_{ik}\right) / l_{ii}$$

**最后一个对角元**：
$$l_{nn} = \sqrt{a_{nn} - \sum_{k=1}^{n-1} l_{nk}^2}$$

#### 3.5 方程组求解

基于 $A = LL^T$，方程组 $Ax = b$ 归结为两个三角方程组：

1. **前代**（解 $Ly = b$）：$y_1 = b_1/l_{11}$，依此向下求 $y_i$
2. **回代**（解 $L^Tx = y$）：$x_n = y_n/l_{nn}$，依此向上求 $x_i$

---

### 第4部分：改进平方根法 $LDL^T$ 分解（PDF 第14–15页）

#### 4.1 动机

平方根法含有**开方运算**，计算量大且有精度损失。改进方法使用**单位三角阵**作为分解阵，完全避免开方。

#### 4.2 定理

**定理 7**：对称正定阵 A 可分解为：
$$A = LDL^T$$

其中：
$$D = \begin{bmatrix} d_1 & & \\ & d_2 & \\ & & \ddots \\ & & & d_n \end{bmatrix} \quad \text{为对角阵}$$

$$L = \begin{bmatrix} 1 & & & \\ l_{21} & 1 & & \\ \vdots & \ddots & \ddots & \\ l_{n1} & \cdots & l_{n,n-1} & 1 \end{bmatrix} \quad \text{为单位下三角阵}$$

#### 4.3 分解公式

对 $i = 1, 2, \ldots, n$：
$$d_i = a_{ii} - \sum_{k=1}^{i-1} l_{ik}^2 d_k$$
$$l_{ji} = \left(a_{ji} - \sum_{k=1}^{i-1} l_{jk}l_{ik}d_k\right) / d_i \quad (j = i+1, \ldots, n)$$

#### 4.4 方程组求解

$Ax = b$ 转化为：
1. $Ly = b$（追/前代）
2. $L^Tx = D^{-1}y$（赶/回代）

求解公式：
- $y_1 = b_1$，$y_i = b_i - \sum_{k=1}^{i-1} l_{ik}y_k$（$i = 2, \ldots, n$）
- $x_n = y_n/d_n$，$x_i = y_i/d_i - \sum_{k=i+1}^{n} l_{ki}x_k$（$i = n-1, \ldots, 1$）

#### 4.5 一维压缩存储

对于大型方程组，需考虑存储优化。对称正定阵只需存下三角部分，可用一维数组按行或按列压缩存储。

---

### 第5部分：追赶法 — 三对角方程组的 Crout 分解（PDF 第10–13页）

#### 5.1 三对角方程组

$$\begin{bmatrix} b_1 & c_1 & & & \\ a_2 & b_2 & c_2 & & \\ & \ddots & \ddots & \ddots & \\ & & a_{n-1} & b_{n-1} & c_{n-1} \\ & & & a_n & b_n \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \\ \vdots \\ x_{n-1} \\ x_n \end{bmatrix} = \begin{bmatrix} f_1 \\ f_2 \\ \vdots \\ f_{n-1} \\ f_n \end{bmatrix}$$

简记为 $Ax = f$。

**来源**：常微分方程边值问题、三次样条插值等。

#### 5.2 追赶法算法

**Step 1**：对 A 作 Crout 分解（追的预处理）

将三对角阵 A 分解为：
$$A = \begin{bmatrix} \alpha_1 & & & \\ \gamma_2 & \alpha_2 & & \\ & \ddots & \ddots & \\ & & \gamma_n & \alpha_n \end{bmatrix} \begin{bmatrix} 1 & \beta_1 & & \\ & 1 & \beta_2 & \\ & & \ddots & \beta_{n-1} \\ & & & 1 \end{bmatrix}$$

分解公式（直接比较两边元素）：
$$\beta_1 = c_1 / b_1 = c_1 / \alpha_1$$
对 $i = 2, 3, \ldots, n$：
$$\alpha_i = b_i - a_i\beta_{i-1}$$
$$\beta_i = c_i / \alpha_i \quad (i < n)$$

（最后一个 $\alpha_n = b_n - a_n\beta_{n-1}$，不需求 $\beta_n$）

**Step 2**：追 — 解 $Ly = f$

$$y_1 = f_1 / \alpha_1$$
$$y_i = (f_i - a_i y_{i-1}) / \alpha_i \quad (i = 2, \ldots, n)$$

**Step 3**：赶 — 解 $Ux = y$

$$x_n = y_n$$
$$x_i = y_i - \beta_i x_{i+1} \quad (i = n-1, \ldots, 1)$$

#### 5.3 收敛性条件

**定理 3**：若 A 为**对角占优**的三对角阵，且满足：
$$|b_1| > |c_1| > 0, \quad |b_n| > |a_n| > 0, \quad |b_i| \geq |a_i| + |c_i|, \quad a_i \neq 0, c_i \neq 0$$

则 A 非奇异，追赶法可解且不会中断（$\alpha_i \neq 0$）。

#### 5.4 算法复杂度

追赶法的计算量为 **$O(n)$**，仅为全矩阵消元的 $O(n^3)$ 的极小一部分，是解三对角方程组的最优算法。

---

### 第6部分：例题选讲（PDF 第16–18页）

#### 6.1 Doolittle 分解示例

**题 4**：考察四阶方阵 $A = (a_{ij})_{4\times4}$ 的 Doolittle 分解，并针对 n 阶方阵列出分解公式。

**解**：按矩阵乘法展开 $A = LU$，逐行逐列计算：
- 第一行：$u_{11} = a_{11}, u_{12} = a_{12}, u_{13} = a_{13}, u_{14} = a_{14}$
- 第一列：$l_{21} = a_{21}/u_{11}, l_{31} = a_{31}/u_{11}, l_{41} = a_{41}/u_{11}$
- 第二行：$u_{22} = a_{22} - l_{21}u_{12}, u_{23} = a_{23} - l_{21}u_{13}, u_{24} = a_{24} - l_{21}u_{14}$
- 依此类推……

**关键**：设定计算顺序（如逐行生成 L 与 U），则非线性方程组变为显式计算公式。

#### 6.2 Crout 分解示例

**题 6**：给出 Crout 分解公式及基于此分解的方程组求解。

**分解公式**（对 $i = 1, 2, \ldots, n$ 逐行计算）：
$$l_{ij} = a_{ij} - \sum_{k=1}^{j-1} l_{ik}u_{kj} \quad (j = 1, 2, \ldots, i)$$
$$u_{ji} = \left(a_{ji} - \sum_{k=1}^{i-1} l_{jk}u_{ki}\right) / l_{ii} \quad (j = i+1, i+2, \ldots, n)$$

**求解公式**：
- 追（$Ly = b$）：$y_i = \left(b_i - \sum_{k=1}^{i-1} l_{ik}y_k\right) / l_{ii}$
- 赶（$Ux = y$）：$x_i = y_i - \sum_{k=i+1}^{n} u_{ik}x_k$

#### 6.3 不可分解的情形

**题 7**：说明某些矩阵不能进行三角分解。

例如 $A = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$ 无法做 Doolittle 分解（因为 $u_{11} = 0$，导致 $l_{21}$ 无法计算）。这说明**并非所有矩阵都可进行 LU 分解**，需要顺序主子式非零的条件。

#### 6.4 一阶矩阵的启示

**题 1**（平方根法 vs 改进法）：一阶 $A = (a)$ 的分解：
- 平方根法：$a = l \cdot l$，$l = \sqrt{a}$，**含开方**
- 改进法：$a = 1 \cdot d \cdot 1$，$d = a$，**无开方**

最简单的例子揭示了改进平方根法的优势。

#### 6.5 三对角阵的 $LDL^T$ 分解

设三对角阵 A，分解为 $A = LDL^T$（L 为单位下二对角阵，D 为对角阵），分解公式：
$$d_1 = b_1$$
$$l_{i+1} = a_{i+1} / d_i, \quad d_{i+1} = b_{i+1} - l_{i+1}^2 d_i \quad (i = 1, 2, \ldots, n-1)$$

---

### 第7部分：习题（PDF 第19–21页）

#### 习题类型汇总

1. **追赶法求解三对角方程组**
   例：$\begin{bmatrix} 2 & -1 & & \\ -1 & 3 & -2 & \\ & 1 & 2 & -3 \\ & & -1 & 5 \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \\ x_3 \\ x_4 \end{bmatrix} = \begin{bmatrix} 6 \\ 2 \\ 1 \\ 5 \end{bmatrix}$
   
   步骤：消元过程（追）+ 回代过程（赶）

2. **矩阵的 $LDL^T$ 分解**
   例：$A = \begin{bmatrix} 2 & 1 & 0 \\ 1 & 3 & 1 \\ 0 & 1 & 4 \end{bmatrix}$ 分解为 $LDL^T$ 形式

3. **矩阵的 Cholesky（$LL^T$）分解**
   例：$A = \begin{bmatrix} 3 & 2 & 3 \\ 2 & 2 & 0 \\ 3 & 0 & 12 \end{bmatrix}$ 分解为 $LL^T$ 形式

---

## 三、解题通法

### 通法1：Doolittle 分解（LU 分解）解题步骤

```
输入：n 阶方阵 A
输出：单位下三角阵 L，上三角阵 U，满足 A = LU

Step 1: 计算 U 的第一行
        for j = 1 to n:  u_{1j} = a_{1j}

Step 2: 计算 L 的第一列
        for i = 2 to n:  l_{i1} = a_{i1} / u_{11}

Step 3: 逐行/列递推（i = 2, 3, ..., n-1）
        ① 计算 U 的第 i 行：
           for j = i to n:
               u_{ij} = a_{ij} - Σ_{k=1}^{i-1} l_{ik}·u_{kj}
        ② 计算 L 的第 i 列：
           for j = i+1 to n:
               l_{ji} = (a_{ji} - Σ_{k=1}^{i-1} l_{jk}·u_{ki}) / u_{ii}

Step 4: 计算最后一个元素
        u_{nn} = a_{nn} - Σ_{k=1}^{n-1} l_{nk}·u_{kn}
```

**注意**：
- 求解顺序必须是：先 U 的一行，再 L 的一列，交替进行
- 若某 $u_{ii} = 0$，分解中断（需换主元或改用其他方法）
- Doolittle：L 对角元固定为 1；Crout：U 对角元固定为 1

---

### 通法2：基于 LU 分解解方程组 $Ax = b$

```
Step 1: 对 A 做 Doolittle 分解 A = LU

Step 2: 追 — 解 Ly = b（前代，顺序进行）
        y_1 = b_1
        for i = 2 to n:
            y_i = b_i - Σ_{k=1}^{i-1} l_{ik}·y_k

Step 3: 赶 — 解 Ux = y（回代，逆序进行）
        x_n = y_n / u_{nn}
        for i = n-1 down to 1:
            x_i = (y_i - Σ_{k=i+1}^{n} u_{ik}·x_k) / u_{ii}
```

**口诀**：**先追后赶，前代回代**

---

### 通法3：平方根法（Cholesky $LL^T$）解题步骤

```
输入：对称正定矩阵 A（需先验证对称正定性）
输出：下三角阵 L，满足 A = L·L^T

Step 1: 验证对称正定性
        - 检查 A = A^T
        - 检查顺序主子式 det(A_k) > 0（或特征值 > 0）

Step 2: Cholesky 分解
        l_{11} = √a_{11}
        for j = 2 to n:  l_{j1} = a_{j1} / l_{11}
        
        for i = 2 to n-1:
            l_{ii} = √(a_{ii} - Σ_{k=1}^{i-1} l_{ik}²)
            for j = i+1 to n:
                l_{ji} = (a_{ji} - Σ_{k=1}^{i-1} l_{jk}·l_{ik}) / l_{ii}
        
        l_{nn} = √(a_{nn} - Σ_{k=1}^{n-1} l_{nk}²)

Step 3: 解方程组 Ax = b
        前代 Ly = b → 回代 L^T x = y
```

**核心公式记忆**：$l_{ii} = \sqrt{a_{ii} - \sum_{k=1}^{i-1} l_{ik}^2}$（对角元含开方）

---

### 通法4：改进平方根法（$LDL^T$）解题步骤

```
输入：对称正定矩阵 A
输出：单位下三角阵 L，对角阵 D，满足 A = L·D·L^T

Step 1: LDL^T 分解
        for i = 1 to n:
            d_i = a_{ii} - Σ_{k=1}^{i-1} l_{ik}²·d_k
            for j = i+1 to n:
                l_{ji} = (a_{ji} - Σ_{k=1}^{i-1} l_{jk}·l_{ik}·d_k) / d_i

Step 2: 解方程组 Ax = b
        ① Ly = b（追）：
           y_1 = b_1
           for i = 2 to n:  y_i = b_i - Σ_{k=1}^{i-1} l_{ik}·y_k
        
        ② L^T x = D^{-1}y（赶）：
           x_n = y_n / d_n
           for i = n-1 down to 1:
               x_i = y_i/d_i - Σ_{k=i+1}^{n} l_{ki}·x_k
```

**与平方根法的对比**：无开方运算，计算更稳定

---

### 通法5：追赶法解题步骤

```
输入：三对角矩阵（三条对角线数组 a_i, b_i, c_i），右端项 f_i
输出：解向量 x

Step 1: 追赶预处理（Crout 分解）
        α_1 = b_1
        β_1 = c_1 / α_1
        
        for i = 2 to n-1:
            α_i = b_i - a_i·β_{i-1}
            β_i = c_i / α_i
        
        α_n = b_n - a_n·β_{n-1}   （不需求β_n）

Step 2: 追（解 Ly = f）
        y_1 = f_1 / α_1
        for i = 2 to n:
            y_i = (f_i - a_i·y_{i-1}) / α_i

Step 3: 赶（解 Ux = y）
        x_n = y_n
        for i = n-1 down to 1:
            x_i = y_i - β_i·x_{i+1}
```

**追赶法的矩阵分解形式**：
$$A = \begin{bmatrix} \alpha_1 & & \\ a_2 & \alpha_2 & \\ & \ddots & \ddots \\ & & a_n & \alpha_n \end{bmatrix} \begin{bmatrix} 1 & \beta_1 & \\ & 1 & \ddots \\ & & \ddots & \beta_{n-1} \\ & & & 1 \end{bmatrix}$$

**成立条件**：A 需对角占优（$|b_1| > |c_1|$，$|b_n| > |a_n|$，$|b_i| \geq |a_i| + |c_i|$），确保 $\alpha_i \neq 0$。

---

### 方法选择决策树

```
求解 Ax = b
├─ A 是三对角阵？
│  └─ 是 → 追赶法（O(n)，最优）
│        需对角占优条件
│
├─ A 是对称正定阵？
│  ├─ 需避免开方？→ 改进平方根法 LDL^T
│  └─ 可接受开方？→ 平方根法 LL^T（Cholesky）
│     （存储和计算量均为 LU 的一半）
│
├─ A 是一般方阵？
│  ├─ Doolittle 分解（L 单位下三角 + U 上三角）
│  └─ 或 Crout 分解（L 下三角 + U 单位上三角）
│     （两者本质等价）
│
└─ 需要反复求解（不同 b）？
   └─ 优先使用 LU 分解：一次分解，多次回代
```

---

### 三角方程组求解公式速查

| 方程组类型 | 求解方向 | 公式 |
|-----------|---------|------|
| 下三角 $Lx = b$ | 顺序（前代/追） | $x_i = (b_i - \sum_{k=1}^{i-1} l_{ik}x_k) / l_{ii}$ |
| 上三角 $Ux = b$ | 逆序（回代/赶） | $x_i = (b_i - \sum_{k=i+1}^{n} u_{ik}x_k) / u_{ii}$ |
| 单位下三角 | 顺序 | $x_i = b_i - \sum_{k=1}^{i-1} l_{ik}x_k$ |
| 单位上三角 | 逆序 | $x_i = b_i - \sum_{k=i+1}^{n} u_{ik}x_k$ |

---

## 附录：重要公式速查表

| 公式 | 含义 |
|------|------|
| $A = LU$ | Doolittle 分解（L 单位下三角） |
| $A = \tilde{L}\tilde{U}$（L 一般，U 单位） | Crout 分解 |
| $A = LL^T$ | Cholesky 分解（平方根法） |
| $A = LDL^T$ | 改进平方根法（乔累斯基方法） |
| $u_{ij} = a_{ij} - \sum_{k=1}^{i-1} l_{ik}u_{kj}$ | Doolittle：U 的第 i 行 |
| $l_{ji} = (a_{ji} - \sum_{k=1}^{i-1} l_{jk}u_{ki})/u_{ii}$ | Doolittle：L 的第 i 列 |
| $l_{ii} = \sqrt{a_{ii} - \sum_{k=1}^{i-1} l_{ik}^2}$ | Cholesky 对角元 |
| $d_i = a_{ii} - \sum_{k=1}^{i-1} l_{ik}^2 d_k$ | $LDL^T$ 分解对角元 |
| $\alpha_i = b_i - a_i\beta_{i-1}$ | 追赶法 α 递推 |
| $\beta_i = c_i / \alpha_i$ | 追赶法 β 递推 |
| $y_i = (f_i - a_i y_{i-1})/\alpha_i$ | 追赶法"追" |
| $x_i = y_i - \beta_i x_{i+1}$ | 追赶法"赶" |
