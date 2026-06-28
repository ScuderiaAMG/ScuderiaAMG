# NA06d 迭代法的收敛性

这份笔记按 PDF《迭代法的收敛性》的知识点重新整理。主线是：线性迭代的误差怎样传播，为什么谱半径决定收敛，怎样用范数、严格对角占优、Jacobi、Gauss-Seidel 和松弛法来判断收敛。最后补充常见题型的通用解题方法。

## 一、线性迭代为什么要讨论收敛

线性迭代格式通常写成

$$
x^{(k+1)}=Bx^{(k)}+f.
$$

如果它收敛到 $x^*$，则极限必须满足

$$
x^*=Bx^*+f.
$$

也就是说，迭代收敛时，极限才是对应方程的解。问题在于：给出一个迭代格式以后，它不一定收敛；即使收敛，不同迭代格式的速度也可能差很多。因此，本节核心问题是：

- 怎样判断迭代是否收敛；
- 若收敛，什么因素决定它收敛快慢；
- 对 Jacobi、Gauss-Seidel、松弛法这几类常见迭代，怎样快速判别。

## 二、误差传播方程

设精确解或迭代极限为 $x^*$，定义第 $k$ 步误差

$$
e^{(k)}=x^{(k)}-x^*.
$$

由

$$
x^{(k+1)}=Bx^{(k)}+f,\qquad x^*=Bx^*+f,
$$

两式相减得

$$
e^{(k+1)}=Be^{(k)}.
$$

继续递推：

$$
e^{(k)}=B^ke^{(0)}.
$$

所以迭代是否收敛，本质上是在问：

$$
B^k \to 0
$$

是否成立。若 $B^k\to 0$，那么对任意初始误差 $e^{(0)}$，都有 $e^{(k)}\to 0$，于是 $x^{(k)}\to x^*$。

## 三、矩阵序列收敛的含义

设

$$
A_k=\left(a_{ij}^{(k)}\right)_{n\times n},\qquad A=(a_{ij})_{n\times n}.
$$

矩阵序列 $A_k\to A$ 的意思是每个元素都收敛：

$$
\lim_{k\to\infty}a_{ij}^{(k)}=a_{ij},\qquad 1\le i,j\le n.
$$

在有限维矩阵空间中，这也等价于任意算子范数下

$$
\|A_k-A\|\to 0.
$$

因此，判断 $B^k\to 0$ 可以从矩阵元素、矩阵范数或谱半径角度来做。

## 四、收敛性的核心定理

对于

$$
x=Bx+f
$$

若存在唯一解，则从任意初值 $x^{(0)}$ 出发，迭代

$$
x^{(k+1)}=Bx^{(k)}+f
$$

收敛，当且仅当

$$
B^k\to 0.
$$

又有重要定理：

$$
B^k\to 0
\Longleftrightarrow
\rho(B)<1.
$$

其中

$$
\rho(B)=\max_i|\lambda_i|
$$

称为矩阵 $B$ 的谱半径，$\lambda_i$ 是 $B$ 的特征值。

因此最重要的结论是

$$
\boxed{\rho(B)<1 \Longleftrightarrow \text{迭代从任意初值出发收敛}}
$$

反过来，如果

$$
\rho(B)\ge 1,
$$

则迭代不具有从任意初值出发都收敛的性质。

## 五、范数判别法

由误差传播式可得

$$
\|e^{(k)}\|
=\|Be^{(k-1)}\|
\le \|B\|\cdot \|e^{(k-1)}\|
\le \cdots
\le \|B\|^k\|e^{(0)}\|.
$$

如果存在某个矩阵范数，使

$$
\|B\|=q<1,
$$

则

$$
\|B\|^k\to 0,
\qquad
\|e^{(k)}\|\to 0,
$$

所以迭代收敛。

注意：这是充分条件，不是必要条件。也就是说：

- 若能算出某个范数 $\|B\|<1$，可直接判定收敛；
- 若某个范数 $\|B\|\ge 1$，不能立刻判定发散，还应回到谱半径 $\rho(B)$。

常用的两个范数是

$$
\|B\|_\infty=\max_i\sum_j |b_{ij}|
$$

和

$$
\|B\|_1=\max_j\sum_i |b_{ij}|.
$$

其中 $\|B\|_\infty$ 是最大行和范数，$\|B\|_1$ 是最大列和范数。

## 六、Jacobi 与 Gauss-Seidel 迭代

对线性方程组

$$
Ax=b,
$$

设

$$
A=D+L+U,
$$

其中 $D$ 是对角部分，$L$ 是严格下三角部分，$U$ 是严格上三角部分。

### 1. Jacobi 迭代

Jacobi 迭代为

$$
Dx^{(k+1)}=b-(L+U)x^{(k)}.
$$

写成标准迭代格式：

$$
x^{(k+1)}=B_Jx^{(k)}+f_J,
$$

其中

$$
B_J=-D^{-1}(L+U),\qquad f_J=D^{-1}b.
$$

收敛判别为

$$
\rho(B_J)<1.
$$

### 2. Gauss-Seidel 迭代

Gauss-Seidel 迭代使用本轮已经算出的新分量：

$$
(D+L)x^{(k+1)}=b-Ux^{(k)}.
$$

写成标准迭代格式：

$$
x^{(k+1)}=B_Gx^{(k)}+f_G,
$$

其中

$$
B_G=-(D+L)^{-1}U,\qquad f_G=(D+L)^{-1}b.
$$

收敛判别为

$$
\rho(B_G)<1.
$$

### 3. 严格对角占优的充分条件

若 $A$ 是严格对角占优矩阵，即对每一行都有

$$
|a_{ii}|>\sum_{j\ne i}|a_{ij}|,
$$

则解 $Ax=b$ 的 Jacobi 迭代和 Gauss-Seidel 迭代都收敛。

这个条件非常适合快速判断，但它仍只是充分条件。矩阵不严格对角占优，并不代表 Jacobi 或 Gauss-Seidel 一定发散。

## 七、例题 1：用谱半径和范数判断 Jacobi 收敛

判断方程组采用 Jacobi 迭代是否收敛：

$$
\begin{cases}
8x_1-3x_2+2x_3=20,\\
4x_1+11x_2-x_3=33,\\
6x_1+3x_2+12x_3=36.
\end{cases}
$$

先把它写成 Jacobi 形式：

$$
\begin{cases}
x_1=\dfrac{20}{8}+\dfrac{3}{8}x_2-\dfrac{2}{8}x_3,\\[6pt]
x_2=\dfrac{33}{11}-\dfrac{4}{11}x_1+\dfrac{1}{11}x_3,\\[6pt]
x_3=\dfrac{36}{12}-\dfrac{6}{12}x_1-\dfrac{3}{12}x_2.
\end{cases}
$$

因此

$$
x^{(k+1)}
=
\begin{pmatrix}
0 & \frac{3}{8} & -\frac{2}{8}\\
-\frac{4}{11} & 0 & \frac{1}{11}\\
-\frac{6}{12} & -\frac{3}{12} & 0
\end{pmatrix}
x^{(k)}
+
\begin{pmatrix}
\frac{20}{8}\\[2pt]
\frac{33}{11}\\[2pt]
\frac{36}{12}
\end{pmatrix}.
$$

记上面的迭代矩阵为 $B$。

### 1. 谱半径判别

求 $B$ 的特征值，PDF 中给出的结果为

$$
\lambda_1=-0.3082,\qquad
\lambda_2=0.1541+0.3245i,\qquad
\lambda_3=0.1541-0.3245i.
$$

于是

$$
\rho(B)=\max_i|\lambda_i|=0.3592<1.
$$

所以该方程组的 Jacobi 迭代收敛。

### 2. 范数判别

最大行和范数为

$$
\|B\|_\infty
=\max\left\{\frac58,\frac5{11},\frac34\right\}
=\frac34<1.
$$

最大列和范数为

$$
\|B\|_1
=\max\left\{\frac{19}{22},\frac58,\frac{15}{44}\right\}
=\frac{19}{22}<1.
$$

任意一种算子范数小于 1，都能说明谱半径小于 1，所以也可判定 Jacobi 迭代收敛。

## 八、松弛法

松弛法是对 Gauss-Seidel 迭代的一种修正。它的思想是：

1. 先按 Gauss-Seidel 的方式算出一个临时新值 $\tilde{x}_i^{(k+1)}$；
2. 再把旧值 $x_i^{(k)}$ 与临时新值做加权平均，得到真正的新值。

松弛因子记为

$$
\omega>0.
$$

更新公式为

$$
x_i^{(k+1)}
=(1-\omega)x_i^{(k)}+\omega \tilde{x}_i^{(k+1)}
=x_i^{(k)}+\omega\left(\tilde{x}_i^{(k+1)}-x_i^{(k)}\right).
$$

三种情况：

| $\omega$ 范围 | 名称 | 含义 |
|---|---|---|
| $0<\omega<1$ | 低松弛法 | 步子变小，更保守 |
| $\omega=1$ | Gauss-Seidel 法 | 不加松弛，正好回到 G-S |
| $\omega>1$ | 逐次超松弛法，也称 SOR | 步子变大，可能加速 |

对方程组 $Ax=b$，第 $i$ 个分量的 Gauss-Seidel 临时值为

$$
\tilde{x}_i^{(k+1)}
=
\frac{
b_i-\sum_{j=1}^{i-1}a_{ij}x_j^{(k+1)}
-\sum_{j=i+1}^{n}a_{ij}x_j^{(k)}
}{a_{ii}}.
$$

代入松弛更新得

$$
x_i^{(k+1)}
=
(1-\omega)x_i^{(k)}
+
\frac{\omega}{a_{ii}}
\left(
b_i-\sum_{j=1}^{i-1}a_{ij}x_j^{(k+1)}
-\sum_{j=i+1}^{n}a_{ij}x_j^{(k)}
\right).
$$

仍设

$$
A=D+L+U.
$$

SOR 可写为矩阵形式：

$$
(D+\omega L)x^{(k+1)}
=
\left[(1-\omega)D-\omega U\right]x^{(k)}
+\omega b.
$$

因此

$$
x^{(k+1)}=H_\omega x^{(k)}+g_\omega,
$$

其中

$$
H_\omega
=
(D+\omega L)^{-1}
\left[(1-\omega)D-\omega U\right].
$$

若 $A$ 可逆且 $a_{ii}\ne 0$，则给定 $\omega$ 时，松弛法从任意初值出发收敛的充要条件是

$$
\rho(H_\omega)<1.
$$

## 九、收敛速度由谱半径决定

对迭代

$$
x^{(k+1)}=Bx^{(k)}+f,
$$

有

$$
e^{(k)}=B^ke^{(0)}.
$$

如果 $B$ 有 $n$ 个线性无关的特征向量 $v_1,\ldots,v_n$，初始误差可写成

$$
e^{(0)}=\sum_{i=1}^n \alpha_i v_i.
$$

于是

$$
e^{(k)}
=
B^ke^{(0)}
=
\sum_{i=1}^n \alpha_i \lambda_i^k v_i.
$$

当 $k$ 很大时，最大的 $|\lambda_i|$ 主导误差衰减速度。因此：

$$
\rho(B)\text{ 越小，迭代通常收敛越快。}
$$

对松弛法来说，选择 $\omega$ 的目标就是让

$$
\rho(H_\omega)
$$

尽量小。

## 十、例题 2：求参数范围和最快收敛参数

设

$$
A=
\begin{pmatrix}
2&1\\
1&2
\end{pmatrix},
\qquad
b=
\begin{pmatrix}
1\\
2
\end{pmatrix},
$$

考虑迭代格式

$$
x^{(k+1)}=x^{(k)}+\omega(Ax^{(k)}-b).
$$

问：

1. $\omega$ 取什么值可使迭代收敛？
2. $\omega$ 取什么值时迭代收敛最快？

把迭代写成

$$
x^{(k+1)}=(I+\omega A)x^{(k)}-\omega b.
$$

因此迭代矩阵是

$$
B=I+\omega A.
$$

矩阵 $A$ 的特征值为 $1,3$，所以 $B$ 的特征值为

$$
\lambda_1=1+\omega,\qquad
\lambda_2=1+3\omega.
$$

收敛要求

$$
\rho(B)<1,
$$

即

$$
|1+\omega|<1,\qquad |1+3\omega|<1.
$$

两者合并得

$$
-\frac23<\omega<0.
$$

收敛速度由

$$
\rho(B)=\max\{|1+\omega|,\ |1+3\omega|\}
$$

决定。为了让最大值尽量小，应让两个绝对值在最优点处相等：

$$
1+\omega=-(1+3\omega).
$$

解得

$$
\omega=-\frac12.
$$

此时谱半径最小，迭代最快。

## 十一、例题 3：Jacobi 收敛但 Gauss-Seidel 发散

判断下列方程组用 Jacobi 迭代法和 Gauss-Seidel 法求解是否收敛：

$$
\begin{pmatrix}
1&2&-2\\
1&1&1\\
2&2&1
\end{pmatrix}
\begin{pmatrix}
x_1\\x_2\\x_3
\end{pmatrix}
=
\begin{pmatrix}
1\\1\\1
\end{pmatrix}.
$$

### 1. Jacobi 迭代

把每个方程分别解出对应变量：

$$
\begin{cases}
x_1^{(k+1)}=-2x_2^{(k)}+2x_3^{(k)}+1,\\
x_2^{(k+1)}=-x_1^{(k)}-x_3^{(k)}+1,\\
x_3^{(k+1)}=-2x_1^{(k)}-2x_2^{(k)}+1.
\end{cases}
$$

所以

$$
B_J=
\begin{pmatrix}
0&-2&2\\
-1&0&-1\\
-2&-2&0
\end{pmatrix}.
$$

PDF 中计算

$$
\det(\lambda I-B_J)=\lambda^3,
$$

所以全部特征值都是 $0$，于是

$$
\rho(B_J)=0<1.
$$

因此 Jacobi 迭代收敛。

### 2. Gauss-Seidel 迭代

Gauss-Seidel 使用最新分量，先写成

$$
\begin{cases}
x_1^{(k+1)}=-2x_2^{(k)}+2x_3^{(k)}+1,\\
x_2^{(k+1)}=-x_1^{(k+1)}-x_3^{(k)}+1,\\
x_3^{(k+1)}=-2x_1^{(k+1)}-2x_2^{(k+1)}+1.
\end{cases}
$$

把第一式代入第二式、再代入第三式，可化为

$$
\begin{cases}
x_1^{(k+1)}=-2x_2^{(k)}+2x_3^{(k)}+1,\\
x_2^{(k+1)}=2x_2^{(k)}-3x_3^{(k)},\\
x_3^{(k+1)}=2x_3^{(k)}-1.
\end{cases}
$$

因此 Gauss-Seidel 的迭代矩阵为

$$
B_G=
\begin{pmatrix}
0&-2&2\\
0&2&-3\\
0&0&2
\end{pmatrix}.
$$

这是上三角矩阵，特征值就是对角元：

$$
\lambda=0,\ 2,\ 2.
$$

所以

$$
\rho(B_G)=2>1.
$$

因此 Gauss-Seidel 迭代发散。

这个例子说明：Jacobi 和 Gauss-Seidel 的收敛性不能简单互推。必须分别写出各自的迭代矩阵，再看谱半径。

## 十二、常见题型的通用解题方法

### 题型 1：给出一般迭代格式，判断是否收敛

题目形式：

$$
x^{(k+1)}=Bx^{(k)}+f.
$$

通用步骤：

1. 找出迭代矩阵 $B$。
2. 求 $B$ 的特征值。
3. 计算

$$
\rho(B)=\max_i|\lambda_i|.
$$

4. 若 $\rho(B)<1$，则从任意初值出发收敛；若 $\rho(B)\ge 1$，则不满足全局收敛。

这是最稳、最根本的方法。

### 题型 2：要求快速证明迭代收敛

优先尝试范数法：

$$
\|B\|_\infty<1
\quad\text{或}\quad
\|B\|_1<1.
$$

只要找到一个矩阵范数小于 1，就能直接说明收敛。若算出来不小于 1，不要立刻判定发散，应继续用谱半径法。

### 题型 3：判断 Jacobi 或 Gauss-Seidel 是否收敛

通用步骤：

1. 把 $A$ 分解为

$$
A=D+L+U.
$$

2. Jacobi 用

$$
B_J=-D^{-1}(L+U).
$$

3. Gauss-Seidel 用

$$
B_G=-(D+L)^{-1}U.
$$

4. 分别判断

$$
\rho(B_J)<1,\qquad \rho(B_G)<1.
$$

若题目只要求快速判断且 $A$ 严格对角占优，则可以直接说 Jacobi 与 Gauss-Seidel 均收敛。

### 题型 4：用严格对角占优判断

检查每一行是否满足

$$
|a_{ii}|>\sum_{j\ne i}|a_{ij}|.
$$

若全部满足，则 Jacobi 与 Gauss-Seidel 都收敛。若有一行不满足，不能直接说发散，只能说这个充分条件不能用，需要继续算迭代矩阵的谱半径。

### 题型 5：含参数的迭代收敛范围

题目常给

$$
B(\alpha)
$$

或

$$
B(\omega).
$$

通用步骤：

1. 求特征值 $\lambda_i(\alpha)$ 或 $\lambda_i(\omega)$。
2. 写出

$$
\rho(B)=\max_i|\lambda_i|.
$$

3. 解不等式

$$
\rho(B)<1.
$$

4. 得到参数范围。

如果是二维或特征值很简单的问题，经常会变成几个绝对值不等式，例如

$$
|1+\omega|<1,\qquad |1+3\omega|<1.
$$

### 题型 6：求最快收敛参数

先求出收敛范围，再在该范围内最小化谱半径：

$$
\min_\omega \rho(B(\omega)).
$$

常见做法是把

$$
\rho(B(\omega))=\max\{|\lambda_1(\omega)|,|\lambda_2(\omega)|,\ldots\}
$$

画成或想成若干个绝对值函数的最大值。最优点常出现在两个主导绝对值相等的位置。

### 题型 7：松弛法或 SOR 判别

先写出

$$
x^{(k+1)}=H_\omega x^{(k)}+g_\omega.
$$

再判断

$$
\rho(H_\omega)<1.
$$

如果题目问怎样选 $\omega$ 加速收敛，就转化为

$$
\min_\omega \rho(H_\omega).
$$

### 题型 8：比较两个迭代法谁更快

不要只看矩阵元素大小，也不要凭经验说 Gauss-Seidel 一定更快。应比较谱半径：

$$
\rho(B_1)<\rho(B_2)
\quad\Longrightarrow\quad
\text{通常 }B_1\text{ 对应的迭代更快。}
$$

## 十三、易错点

- $\rho(B)<1$ 是线性定常迭代从任意初值收敛的充要条件。
- $\|B\|<1$ 通常只是充分条件，不是必要条件。
- 某个范数算出来大于或等于 1，不代表迭代一定发散。
- 严格对角占优是对原矩阵 $A$ 判断，不是对迭代矩阵 $B$ 判断。
- Jacobi 收敛不能推出 Gauss-Seidel 收敛，反过来也不能推出。
- 松弛法中 $\omega=1$ 才是 Gauss-Seidel；$0<\omega<1$ 是低松弛，$\omega>1$ 是超松弛。
- 收敛快慢主要看谱半径，不是看迭代矩阵元素“肉眼大不大”。
- 写 SOR 矩阵形式时，右端不要漏掉 $+\omega b$。

## 十四、核心公式速查

| 内容 | 公式 |
|---|---|
| 一般迭代 | $x^{(k+1)}=Bx^{(k)}+f$ |
| 误差定义 | $e^{(k)}=x^{(k)}-x^*$ |
| 误差传播 | $e^{(k+1)}=Be^{(k)}$ |
| 误差递推 | $e^{(k)}=B^ke^{(0)}$ |
| 任意初值收敛 | $B^k\to 0$ |
| 谱半径判别 | $B^k\to 0\Longleftrightarrow \rho(B)<1$ |
| 最大行和范数 | $\|B\|_\infty=\max_i\sum_j|b_{ij}|$ |
| 最大列和范数 | $\|B\|_1=\max_j\sum_i|b_{ij}|$ |
| 范数充分条件 | $\|B\|=q<1$ |
| Jacobi 矩阵 | $B_J=-D^{-1}(L+U)$ |
| Gauss-Seidel 矩阵 | $B_G=-(D+L)^{-1}U$ |
| 严格对角占优 | $|a_{ii}|>\sum_{j\ne i}|a_{ij}|$ |
| 松弛更新 | $x_i^{(k+1)}=(1-\omega)x_i^{(k)}+\omega\tilde{x}_i^{(k+1)}$ |
| SOR 矩阵 | $H_\omega=(D+\omega L)^{-1}[(1-\omega)D-\omega U]$ |
| SOR 收敛 | $\rho(H_\omega)<1$ |

## 十五、PDF 末页提到的相关直接法

PDF 最后一页列出了一些与线性方程组求解有关的直接法名称：

- 约当消去法；
- LU 分解；
- Crout 分解，也称追赶法；
- 平方根法。

这些方法与本讲的迭代收敛性不是同一条主线：它们通常用于直接求解线性方程组；本讲重点是 Jacobi、Gauss-Seidel、松弛法等迭代格式是否会收敛，以及怎样判断收敛速度。
