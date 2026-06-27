# NA06b 三角分解法

这份笔记按 PDF 的知识主线重写：从高斯消元的矩阵形式出发，说明为什么会得到 LU 分解，再整理 Doolittle、Crout、平方根法、改进平方根法和追赶法。重点放在“什么时候用什么方法”和“题目中怎样写通式”。

## 一、先把主线讲清楚

### 1. 三角分解法要解决什么

线性方程组写成矩阵形式是

$$
Ax=b.
$$

如果 $A$ 是一般矩阵，直接求 $x$ 不方便；但如果能把 $A$ 分解成两个容易求解的三角矩阵，就可以把一个难问题拆成两个简单问题。

最常见的是

$$
A=LU,
$$

其中

- $L$ 是下三角矩阵。
- $U$ 是上三角矩阵。

于是

$$
Ax=b
\quad\Longleftrightarrow\quad
LUx=b.
$$

令

$$
Ux=y,
$$

就得到两步：

$$
Ly=b,\quad Ux=y.
$$

第一步用前代求 $y$，第二步用回代求 $x$。

### 2. 为什么它比每次重新消元更有用

如果同一个系数矩阵 $A$ 对应多个右端项：

$$
Ax=b_1,\quad Ax=b_2,\quad Ax=b_3,
$$

那么只要先做一次分解

$$
A=LU,
$$

之后每个右端项都只需要求解两个三角方程组。分解本身大约是 $O(n^3)$，但每次前代、回代只是 $O(n^2)$，所以当右端项很多时很划算。

### 3. 本讲方法之间的关系

本讲所有方法都围绕同一个思想：

| 方法 | 适用矩阵 | 分解形式 | 主要用途 |
|---|---|---|---|
| Doolittle 分解 | 一般非奇异矩阵，在主元条件满足时 | $A=LU,\ l_{ii}=1$ | 通用 LU 分解 |
| Crout 分解 | 一般非奇异矩阵，在主元条件满足时 | $A=LU,\ u_{ii}=1$ | 另一种 LU 规范 |
| Cholesky 平方根法 | 对称正定矩阵 | $A=LL^T$ | 更省计算和存储 |
| 改进平方根法 | 对称正定矩阵 | $A=LDL^T$ | 避免开平方 |
| 追赶法 | 三对角方程组 | 特殊 Crout 分解 | $O(n)$ 解三对角系统 |

## 二、从高斯消元到 LU 分解

### 1. 高斯消元的矩阵形式

高斯消元每一步都可以看成左乘一个消元矩阵。

第 1 步用主元 $a_{11}^{(1)}$ 消去第一列下面的元素。消元因子为

$$
m_{i1}=\frac{a_{i1}^{(1)}}{a_{11}^{(1)}},
\quad i=2,\dots,n.
$$

对应的消元矩阵形如

$$
L_1=
\begin{bmatrix}
1 & & & \\
-m_{21} & 1 & & \\
\vdots & & \ddots & \\
-m_{n1} & & & 1
\end{bmatrix}.
$$

继续做第 $2,3,\dots,n-1$ 步，最后得到上三角矩阵 $U$：

$$
L_{n-1}\cdots L_2L_1A=U.
$$

因此

$$
A=L_1^{-1}L_2^{-1}\cdots L_{n-1}^{-1}U.
$$

把

$$
L=L_1^{-1}L_2^{-1}\cdots L_{n-1}^{-1},
$$

就得到

$$
A=LU.
$$

这里的 $L$ 是单位下三角矩阵，它记录了高斯消元过程中用过的消元因子；$U$ 是消元后得到的上三角矩阵。

### 2. LU 分解的存在条件

不选主元的 LU 分解能够顺利进行，要求消元过程中主元不为 0。常用的充分条件是：$A$ 的所有顺序主子式不为 0。

也就是

$$
\det A_k\ne 0,\quad k=1,2,\dots,n,
$$

其中 $A_k$ 是 $A$ 的左上角 $k$ 阶主子阵。

如果条件不满足，可能需要换行，也就是带主元选取的 LU 分解。

## 三、Doolittle 分解

### 1. 分解形式

Doolittle 分解规定 $L$ 的对角元全为 1：

$$
A=LU,
$$

$$
L=
\begin{bmatrix}
1 & & & \\
l_{21} & 1 & & \\
\vdots & \vdots & \ddots & \\
l_{n1} & l_{n2} & \cdots & 1
\end{bmatrix},
\quad
U=
\begin{bmatrix}
u_{11} & u_{12} & \cdots & u_{1n}\\
 & u_{22} & \cdots & u_{2n}\\
 & & \ddots & \vdots\\
 & & & u_{nn}
\end{bmatrix}.
$$

由 $A=LU$ 比较元素：

$$
a_{ij}=\sum_{k=1}^{\min(i,j)}l_{ik}u_{kj}.
$$

### 2. 计算通式

第 $i$ 步时，假设 $U$ 的前 $i-1$ 行和 $L$ 的前 $i-1$ 列已经算出。

先算 $U$ 的第 $i$ 行：

$$
u_{ij}=a_{ij}-\sum_{k=1}^{i-1}l_{ik}u_{kj},
\quad j=i,i+1,\dots,n.
$$

再算 $L$ 的第 $i$ 列：

$$
l_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{i-1}l_{jk}u_{ki}
}{
u_{ii}
},
\quad j=i+1,i+2,\dots,n.
$$

第一步特别简单：

$$
u_{1j}=a_{1j},\quad j=1,\dots,n,
$$

$$
l_{j1}=\frac{a_{j1}}{u_{11}},\quad j=2,\dots,n.
$$

最后只剩

$$
u_{nn}=a_{nn}-\sum_{k=1}^{n-1}l_{nk}u_{kn}.
$$

### 3. 用 Doolittle 解方程组

求解

$$
Ax=b
$$

时，先分解

$$
A=LU.
$$

然后做两步：

$$
Ly=b,
$$

$$
Ux=y.
$$

前代公式：

$$
y_i=b_i-\sum_{j=1}^{i-1}l_{ij}y_j,
\quad i=1,2,\dots,n.
$$

回代公式：

$$
x_i=
\frac{
y_i-\sum_{j=i+1}^{n}u_{ij}x_j
}{
u_{ii}
},
\quad i=n,n-1,\dots,1.
$$

## 四、Crout 分解

### 1. 分解形式

Crout 分解和 Doolittle 本质一样，只是规范不同。Crout 规定 $U$ 的对角元全为 1：

$$
A=LU,
$$

其中 $L$ 是一般下三角矩阵，$U$ 是单位上三角矩阵：

$$
u_{ii}=1.
$$

### 2. 计算通式

由

$$
a_{ij}=\sum_{k=1}^{\min(i,j)}l_{ik}u_{kj}
$$

得到 Crout 的计算顺序：先算 $L$ 的第 $j$ 列，再算 $U$ 的第 $j$ 行。

计算 $L$ 的第 $j$ 列：

$$
l_{ij}=a_{ij}-\sum_{k=1}^{j-1}l_{ik}u_{kj},
\quad i=j,j+1,\dots,n.
$$

计算 $U$ 的第 $j$ 行：

$$
u_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{j-1}l_{jk}u_{ki}
}{
l_{jj}
},
\quad i=j+1,j+2,\dots,n.
$$

### 3. Doolittle 和 Crout 怎么区分

| 分解 | $L$ | $U$ | 记忆方法 |
|---|---|---|---|
| Doolittle | 单位下三角 | 一般上三角 | 1 放在 $L$ 的对角线上 |
| Crout | 一般下三角 | 单位上三角 | 1 放在 $U$ 的对角线上 |

做题时先看题目要求。如果没有指定，课程中通常默认 Doolittle 形式。

## 五、平方根法 Cholesky 分解

### 1. 适用条件

平方根法只适用于**对称正定矩阵**。

对称：

$$
A=A^T.
$$

正定：

$$
x^TAx>0,\quad x\ne 0.
$$

对称正定矩阵有几个重要性质：

- $A^{-1}$ 仍然对称正定。
- 对角元 $a_{ii}>0$。
- 所有特征值都大于 0。
- 所有顺序主子式都大于 0。

这些性质保证 Cholesky 分解可以顺利进行。

### 2. 分解形式

如果 $A$ 对称正定，则存在非奇异下三角矩阵 $L$，使得

$$
A=LL^T.
$$

这就是 Cholesky 分解，也叫平方根法。

### 3. 计算通式

设

$$
L=(l_{ij}),\quad l_{ij}=0\ (j>i).
$$

对角元：

$$
l_{ii}=
\sqrt{
a_{ii}-\sum_{k=1}^{i-1}l_{ik}^2
},
\quad i=1,2,\dots,n.
$$

非对角元：

$$
l_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{i-1}l_{jk}l_{ik}
}{
l_{ii}
},
\quad j=i+1,i+2,\dots,n.
$$

第一列特别是：

$$
l_{11}=\sqrt{a_{11}},
\quad
l_{j1}=\frac{a_{j1}}{l_{11}}.
$$

### 4. 用 Cholesky 解方程组

如果

$$
A=LL^T,
$$

那么

$$
Ax=b
\quad\Longleftrightarrow\quad
LL^Tx=b.
$$

令

$$
L^Tx=y,
$$

先解

$$
Ly=b,
$$

再解

$$
L^Tx=y.
$$

第一步前代，第二步回代。

## 六、改进平方根法 LDL^T

### 1. 为什么要改进

Cholesky 分解需要开平方。为了避免频繁开平方，可以把对称正定矩阵分解为

$$
A=LDL^T,
$$

其中

- $L$ 是单位下三角矩阵。
- $D$ 是对角矩阵。

这叫改进平方根法，也常写作 $LDL^T$ 分解。

### 2. 分解形式

设

$$
D=\operatorname{diag}(d_1,d_2,\dots,d_n),
$$

$$
L=
\begin{bmatrix}
1 & & & \\
l_{21} & 1 & & \\
\vdots & \vdots & \ddots & \\
l_{n1} & l_{n2} & \cdots & 1
\end{bmatrix}.
$$

则

$$
A=LDL^T.
$$

### 3. 计算通式

对角元：

$$
d_i=
a_{ii}-\sum_{k=1}^{i-1}l_{ik}^2d_k,
\quad i=1,2,\dots,n.
$$

下三角元素：

$$
l_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{i-1}l_{jk}l_{ik}d_k
}{
d_i
},
\quad j=i+1,i+2,\dots,n.
$$

第一步为

$$
d_1=a_{11},
\quad
l_{j1}=\frac{a_{j1}}{d_1}.
$$

### 4. 用 LDL^T 解方程组

若

$$
A=LDL^T,
$$

则

$$
LDL^Tx=b.
$$

按三步解：

$$
Ly=b,
$$

$$
Dz=y,
$$

$$
L^Tx=z.
$$

中间一步最简单：

$$
z_i=\frac{y_i}{d_i}.
$$

## 七、追赶法解三对角方程组

### 1. 三对角方程组的结构

三对角方程组的系数矩阵只有主对角线、上对角线、下对角线可能非零：

$$
\begin{bmatrix}
b_1 & c_1 & & & \\
a_2 & b_2 & c_2 & & \\
& a_3 & b_3 & \ddots & \\
& & \ddots & \ddots & c_{n-1}\\
& & & a_n & b_n
\end{bmatrix}
\begin{bmatrix}
x_1\\x_2\\ \vdots\\x_{n-1}\\x_n
\end{bmatrix}
=
\begin{bmatrix}
f_1\\f_2\\ \vdots\\f_{n-1}\\f_n
\end{bmatrix}.
$$

追赶法就是针对这种矩阵的专门算法，本质是特殊的 Crout 分解。

### 2. 分解通式

把 $A$ 分解为

$$
A=LU,
$$

其中

$$
L=
\begin{bmatrix}
\alpha_1 & & & \\
a_2 & \alpha_2 & & \\
& a_3 & \alpha_3 & \\
& & \ddots & \ddots
\end{bmatrix},
\quad
U=
\begin{bmatrix}
1 & \beta_1 & & \\
& 1 & \beta_2 & \\
& & \ddots & \ddots\\
& & & 1
\end{bmatrix}.
$$

比较元素可得：

$$
\alpha_1=b_1,
\quad
\beta_1=\frac{c_1}{\alpha_1}.
$$

对 $i=2,\dots,n-1$：

$$
\alpha_i=b_i-a_i\beta_{i-1},
\quad
\beta_i=\frac{c_i}{\alpha_i}.
$$

最后：

$$
\alpha_n=b_n-a_n\beta_{n-1}.
$$

如果某个 $\alpha_i=0$，算法会中断。

### 3. 追：前代

先解

$$
Ly=f.
$$

计算：

$$
y_1=\frac{f_1}{\alpha_1},
$$

$$
y_i=\frac{f_i-a_i y_{i-1}}{\alpha_i},
\quad i=2,3,\dots,n.
$$

### 4. 赶：回代

再解

$$
Ux=y.
$$

计算：

$$
x_n=y_n,
$$

$$
x_i=y_i-\beta_i x_{i+1},
\quad i=n-1,n-2,\dots,1.
$$

### 5. 什么时候追赶法可靠

如果三对角矩阵 $A$ 对角占优，并满足边界和非零条件，追赶法通常可以顺利使用。直观上说，主对角线要足够强，不能被上下对角线“压住”。

常见充分条件可以理解为：

$$
|b_i|\ge |a_i|+|c_i|
$$

并且端点和相关非对角元素不退化。做题时若题目给出“对角占优三对角矩阵”，通常就是在提示可以用追赶法。

## 八、方法选择

### 1. 先看矩阵类型

| 看到的矩阵特征 | 优先方法 |
|---|---|
| 一般矩阵，没有特殊结构 | Doolittle 或 Crout |
| 对称正定矩阵 | Cholesky 或 LDL^T |
| 对称正定且想避免开方 | 改进平方根法 $LDL^T$ |
| 三对角矩阵 | 追赶法 |
| 同一个 $A$ 配多个 $b$ | 先分解，再反复前代和回代 |

### 2. 再看题目要求

- 题目写“Doolittle”：令 $l_{ii}=1$。
- 题目写“Crout”：令 $u_{ii}=1$。
- 题目写“平方根法”：写 $A=LL^T$。
- 题目写“改进平方根法”：写 $A=LDL^T$。
- 题目写“三对角”或“追赶法”：写 $\alpha_i,\beta_i,y_i,x_i$ 的递推。

## 九、解题通式总结

### 通式 1：Doolittle 分解

适用：

$$
A=LU,\quad l_{ii}=1.
$$

步骤：

1. 计算 $U$ 的第 $i$ 行：

$$
u_{ij}=a_{ij}-\sum_{k=1}^{i-1}l_{ik}u_{kj},
\quad j=i,\dots,n.
$$

2. 计算 $L$ 的第 $i$ 列：

$$
l_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{i-1}l_{jk}u_{ki}
}{
u_{ii}
},
\quad j=i+1,\dots,n.
$$

3. 解方程组：

$$
Ly=b,\quad Ux=y.
$$

### 通式 2：Crout 分解

适用：

$$
A=LU,\quad u_{ii}=1.
$$

步骤：

1. 计算 $L$ 的第 $j$ 列：

$$
l_{ij}=a_{ij}-\sum_{k=1}^{j-1}l_{ik}u_{kj},
\quad i=j,\dots,n.
$$

2. 计算 $U$ 的第 $j$ 行：

$$
u_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{j-1}l_{jk}u_{ki}
}{
l_{jj}
},
\quad i=j+1,\dots,n.
$$

### 通式 3：Cholesky 平方根法

适用：

$$
A=A^T,\quad x^TAx>0.
$$

分解：

$$
A=LL^T.
$$

公式：

$$
l_{ii}=
\sqrt{
a_{ii}-\sum_{k=1}^{i-1}l_{ik}^2
},
$$

$$
l_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{i-1}l_{jk}l_{ik}
}{
l_{ii}
}.
$$

解方程：

$$
Ly=b,\quad L^Tx=y.
$$

### 通式 4：改进平方根法

适用：

$$
A=A^T,\quad x^TAx>0.
$$

分解：

$$
A=LDL^T.
$$

公式：

$$
d_i=a_{ii}-\sum_{k=1}^{i-1}l_{ik}^2d_k,
$$

$$
l_{ji}=
\frac{
a_{ji}-\sum_{k=1}^{i-1}l_{jk}l_{ik}d_k
}{
d_i
}.
$$

解方程：

$$
Ly=b,\quad Dz=y,\quad L^Tx=z.
$$

### 通式 5：追赶法

适用三对角系统。

分解递推：

$$
\alpha_1=b_1,\quad \beta_1=\frac{c_1}{\alpha_1},
$$

$$
\alpha_i=b_i-a_i\beta_{i-1},
\quad
\beta_i=\frac{c_i}{\alpha_i},
\quad i=2,\dots,n-1,
$$

$$
\alpha_n=b_n-a_n\beta_{n-1}.
$$

前代：

$$
y_1=\frac{f_1}{\alpha_1},
\quad
y_i=\frac{f_i-a_i y_{i-1}}{\alpha_i}.
$$

回代：

$$
x_n=y_n,
\quad
x_i=y_i-\beta_i x_{i+1}.
$$

## 十、常见题型

### 题型一：给矩阵，要求 Doolittle 分解

写出

$$
L=
\begin{bmatrix}
1&0&0\\
l_{21}&1&0\\
l_{31}&l_{32}&1
\end{bmatrix},
\quad
U=
\begin{bmatrix}
u_{11}&u_{12}&u_{13}\\
0&u_{22}&u_{23}\\
0&0&u_{33}
\end{bmatrix}.
$$

再用 $A=LU$ 比较元素。三阶题最好直接按元素展开，最不容易错。

### 题型二：给矩阵，要求 Crout 分解

写出

$$
L=
\begin{bmatrix}
l_{11}&0&0\\
l_{21}&l_{22}&0\\
l_{31}&l_{32}&l_{33}
\end{bmatrix},
\quad
U=
\begin{bmatrix}
1&u_{12}&u_{13}\\
0&1&u_{23}\\
0&0&1
\end{bmatrix}.
$$

再比较 $A=LU$。

### 题型三：对称正定矩阵分解为 $LL^T$

先说明矩阵对称。若题目要求验证正定，可用顺序主子式全正来判断。

然后套 Cholesky 公式，注意对角元要开平方，且应取正平方根。

### 题型四：分解为 $LDL^T$

先写 $L$ 是单位下三角，$D$ 是对角矩阵。做题时按 $d_1,l_{21},l_{31},d_2,l_{32},d_3$ 的顺序算，结构会很清楚。

### 题型五：用追赶法解三对角方程组

先识别三条对角线：

- 下对角线：$a_2,\dots,a_n$。
- 主对角线：$b_1,\dots,b_n$。
- 上对角线：$c_1,\dots,c_{n-1}$。

再按四组递推写：

$$
\alpha,\beta \rightarrow y \rightarrow x.
$$

## 十一、易错点

- Doolittle 和 Crout 的区别只在对角线归一化位置，不是两种完全不同的思想。
- 做 Doolittle 时，$L$ 的对角线是 1；做 Crout 时，$U$ 的对角线是 1。
- Cholesky 只能用于对称正定矩阵，不是任意对称矩阵都可以。
- Cholesky 的 $l_{ii}$ 要取正平方根。
- $LDL^T$ 中 $L$ 是单位下三角，$D$ 是对角阵，不要把 $D$ 吸收到 $L$ 里。
- 追赶法只适合三对角结构，普通稠密矩阵不能硬套。
- 追赶法如果出现 $\alpha_i=0$，递推会中断。

## 十二、核心公式速查

| 方法 | 分解形式 | 关键公式 |
|---|---|---|
| Doolittle | $A=LU,\ l_{ii}=1$ | $u_{ij}=a_{ij}-\sum_{k=1}^{i-1}l_{ik}u_{kj}$ |
| Doolittle | $A=LU,\ l_{ii}=1$ | $l_{ji}=(a_{ji}-\sum_{k=1}^{i-1}l_{jk}u_{ki})/u_{ii}$ |
| Crout | $A=LU,\ u_{ii}=1$ | $l_{ij}=a_{ij}-\sum_{k=1}^{j-1}l_{ik}u_{kj}$ |
| Crout | $A=LU,\ u_{ii}=1$ | $u_{ji}=(a_{ji}-\sum_{k=1}^{j-1}l_{jk}u_{ki})/l_{jj}$ |
| Cholesky | $A=LL^T$ | $l_{ii}=\sqrt{a_{ii}-\sum_{k=1}^{i-1}l_{ik}^2}$ |
| Cholesky | $A=LL^T$ | $l_{ji}=(a_{ji}-\sum_{k=1}^{i-1}l_{jk}l_{ik})/l_{ii}$ |
| 改进平方根法 | $A=LDL^T$ | $d_i=a_{ii}-\sum_{k=1}^{i-1}l_{ik}^2d_k$ |
| 改进平方根法 | $A=LDL^T$ | $l_{ji}=(a_{ji}-\sum_{k=1}^{i-1}l_{jk}l_{ik}d_k)/d_i$ |
| 追赶法 | 三对角 $A=LU$ | $\alpha_i=b_i-a_i\beta_{i-1},\ \beta_i=c_i/\alpha_i$ |
| 追赶法 | $Ly=f,\ Ux=y$ | $y_i=(f_i-a_iy_{i-1})/\alpha_i,\ x_i=y_i-\beta_ix_{i+1}$ |
