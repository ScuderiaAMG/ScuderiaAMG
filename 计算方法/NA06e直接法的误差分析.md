# NA06e 线性方程组直接法的误差分析

这份笔记按 PDF 的知识主线重写：围绕 $Ax=b$ 中 $A$ 和 $b$ 的扰动如何影响解 $x$ 展开，重点整理条件数、病态矩阵判断和误差估计通式。

## 一、先把主线讲清楚

### 1. 直接法为什么也需要误差分析

直接法如高斯消元、LU 分解在无舍入误差时可以有限步得到精确解。但实际计算中：

- $A$ 的元素可能来自测量或建模，本身有误差。
- $b$ 可能有测量误差。
- 计算机浮点运算会产生舍入误差。

因此实际求得的解往往不是精确解，而是带扰动问题的解。

本讲研究：

$$
Ax=b
$$

中 $A$ 和 $b$ 的误差会怎样影响 $x$。

### 2. 条件数是误差放大的核心

本讲最重要的量是条件数：

$$
\operatorname{cond}(A)=\|A\|\cdot\|A^{-1}\|.
$$

它衡量线性方程组对输入误差的敏感程度。

- $\operatorname{cond}(A)$ 接近 1：问题良态，误差不容易被放大。
- $\operatorname{cond}(A)$ 很大：问题病态，小误差可能导致大偏差。

条件数只取决于矩阵 $A$，和你用哪种具体算法无关。

## 二、只有右端项 b 有误差

### 1. 问题设定

设 $A$ 精确，$b$ 有扰动 $\delta b$。精确问题为

$$
Ax=b.
$$

扰动后得到

$$
A(x+\delta x)=b+\delta b.
$$

两式相减：

$$
A\delta x=\delta b.
$$

因此

$$
\delta x=A^{-1}\delta b.
$$

### 2. 绝对误差界

取范数：

$$
\|\delta x\|
\le
\|A^{-1}\|\cdot\|\delta b\|.
$$

这里 $\|A^{-1}\|$ 可以看作绝对误差放大因子。

### 3. 相对误差界

由

$$
b=Ax
$$

可得

$$
\|b\|\le \|A\|\cdot\|x\|.
$$

所以

$$
\frac{1}{\|x\|}
\le
\frac{\|A\|}{\|b\|}.
$$

结合绝对误差界：

$$
\frac{\|\delta x\|}{\|x\|}
\le
\|A\|\cdot\|A^{-1}\|
\frac{\|\delta b\|}{\|b\|}.
$$

也就是

$$
\boxed{
\frac{\|\delta x\|}{\|x\|}
\le
\operatorname{cond}(A)
\frac{\|\delta b\|}{\|b\|}
}
$$

这说明：右端项的相对误差最多会被条件数放大。

## 三、只有系数矩阵 A 有误差

### 1. 问题设定

设 $b$ 精确，$A$ 有扰动 $\delta A$。扰动后问题为

$$
(A+\delta A)(x+\delta x)=b.
$$

原问题为

$$
Ax=b.
$$

将两式联系起来：

$$
(A+\delta A)\delta x=-\delta A x.
$$

等价地，

$$
(I+A^{-1}\delta A)\delta x
=
-A^{-1}\delta A x.
$$

当扰动足够小，使得

$$
\|A^{-1}\|\cdot\|\delta A\|<1,
$$

矩阵 $I+A^{-1}\delta A$ 可逆。

### 2. 相对误差界

可得到估计：

$$
\frac{\|\delta x\|}{\|x\|}
\le
\frac{
\|A^{-1}\|\cdot\|\delta A\|
}{
1-\|A^{-1}\|\cdot\|\delta A\|
}.
$$

改写成相对扰动形式：

$$
\frac{\|\delta x\|}{\|x\|}
\le
\frac{
\operatorname{cond}(A)\dfrac{\|\delta A\|}{\|A\|}
}{
1-\operatorname{cond}(A)\dfrac{\|\delta A\|}{\|A\|}
}.
$$

这个公式说明：如果

$$
\operatorname{cond}(A)\frac{\|\delta A\|}{\|A\|}
$$

接近 1，误差界会迅速变大。

## 四、A 和 b 同时有误差

### 1. 综合误差界

若 $A$ 和 $b$ 都有扰动，则常用估计为

$$
\frac{\|\delta x\|}{\|x\|}
\le
\frac{
\operatorname{cond}(A)
}{
1-\operatorname{cond}(A)\dfrac{\|\delta A\|}{\|A\|}
}
\left(
\frac{\|\delta A\|}{\|A\|}
+
\frac{\|\delta b\|}{\|b\|}
\right).
$$

前提是

$$
\operatorname{cond}(A)\frac{\|\delta A\|}{\|A\|}<1.
$$

### 2. 公式怎么理解

这个式子可以读成：

$$
\text{解的相对误差}
\approx
\text{条件数}
\times
\text{输入相对误差}.
$$

如果条件数很大，即使输入误差很小，解也可能完全不可信。

## 五、条件数

### 1. 定义

在某个矩阵范数下：

$$
\operatorname{cond}(A)=\|A\|\cdot\|A^{-1}\|.
$$

不同范数下条件数的具体数值不同，但对矩阵病态程度的相对判断通常一致。

### 2. 常见条件数

1-范数条件数：

$$
\operatorname{cond}_1(A)=\|A\|_1\|A^{-1}\|_1.
$$

无穷范数条件数：

$$
\operatorname{cond}_\infty(A)=\|A\|_\infty\|A^{-1}\|_\infty.
$$

2-范数条件数：

$$
\operatorname{cond}_2(A)=\|A\|_2\|A^{-1}\|_2.
$$

若用奇异值表示：

$$
\operatorname{cond}_2(A)=
\frac{\sigma_{\max}(A)}{\sigma_{\min}(A)}.
$$

若 $A$ 为对称矩阵，则可用特征值写成

$$
\operatorname{cond}_2(A)
=
\frac{\max_i|\lambda_i|}{\min_i|\lambda_i|}.
$$

### 3. 条件数的意义

- $\operatorname{cond}(A)=1$ 是最理想的情况。
- $\operatorname{cond}(A)$ 越大，矩阵越病态。
- 条件数大说明问题本身敏感，不是换一种直接法就能根本解决。

## 六、病态矩阵

### 1. Hilbert 矩阵

Hilbert 矩阵是典型病态矩阵：

$$
H_n=\left(\frac{1}{i+j-1}\right).
$$

随着 $n$ 增大，条件数迅速变大：

$$
\operatorname{cond}(H_n)\to\infty.
$$

这说明即使矩阵规模不大，也可能非常难以得到可靠解。

### 2. 不计算逆矩阵时如何判断病态

实际中一般不直接算 $A^{-1}$ 来判断病态，因为求逆本身就可能不稳定。常用经验判断：

- 行列式特别大或特别小。
- 某些行或列近似线性相关。
- 元素数量级相差很大且无规律。
- 消元过程中出现很小主元。
- 特征值相差很多数量级。

### 3. 病态方程组的直观例子

考虑矩阵

$$
A=
\begin{bmatrix}
1 & 1\\
1 & 1.0001
\end{bmatrix}.
$$

两行几乎相同，所以矩阵接近奇异。此时右端项的微小变化，就可能让解发生很大变化。

这不是算法“算坏了”，而是问题本身对误差太敏感。

## 七、解题通式总结

### 通式 1：只有 b 有误差

设

$$
A(x+\delta x)=b+\delta b.
$$

则

$$
\delta x=A^{-1}\delta b.
$$

误差界：

$$
\|\delta x\|
\le
\|A^{-1}\|\|\delta b\|.
$$

相对误差界：

$$
\frac{\|\delta x\|}{\|x\|}
\le
\operatorname{cond}(A)
\frac{\|\delta b\|}{\|b\|}.
$$

### 通式 2：只有 A 有误差

设

$$
(A+\delta A)(x+\delta x)=b.
$$

若

$$
\operatorname{cond}(A)\frac{\|\delta A\|}{\|A\|}<1,
$$

则

$$
\frac{\|\delta x\|}{\|x\|}
\le
\frac{
\operatorname{cond}(A)\dfrac{\|\delta A\|}{\|A\|}
}{
1-\operatorname{cond}(A)\dfrac{\|\delta A\|}{\|A\|}
}.
$$

### 通式 3：A 和 b 同时有误差

$$
\frac{\|\delta x\|}{\|x\|}
\le
\frac{
\operatorname{cond}(A)
}{
1-\operatorname{cond}(A)\dfrac{\|\delta A\|}{\|A\|}
}
\left(
\frac{\|\delta A\|}{\|A\|}
+
\frac{\|\delta b\|}{\|b\|}
\right).
$$

### 通式 4：计算条件数

按定义：

$$
\operatorname{cond}(A)=\|A\|\|A^{-1}\|.
$$

若 $A$ 对称：

$$
\operatorname{cond}_2(A)
=
\frac{\max_i|\lambda_i|}{\min_i|\lambda_i|}.
$$

若 $A$ 一般：

$$
\operatorname{cond}_2(A)
=
\frac{\sigma_{\max}(A)}{\sigma_{\min}(A)}.
$$

## 八、方法选择和常见题型

### 1. 给扰动，估计解误差

先判断扰动来自 $b$、$A$，还是二者都有，然后套对应误差界。

### 2. 给矩阵，计算条件数

若题目指定范数，就按指定范数算：

- $\|A\|_1$：列和最大。
- $\|A\|_\infty$：行和最大。
- $\|A\|_2$：一般用奇异值；对称矩阵可用特征值。

### 3. 判断是否病态

优先看：

- 条件数是否远大于 1。
- 特征值是否数量级差异巨大。
- 行列是否近似相关。

### 4. 解释为什么小扰动导致大误差

回答关键词：

$$
\operatorname{cond}(A)\gg 1.
$$

说明矩阵病态，输入误差被显著放大。

## 九、易错点

- 条件数取决于 $A$，不是取决于具体求解方法。
- 条件数的数值依赖范数，但病态程度判断通常一致。
- $\det(A)$ 很小不等于一定病态，但常常是危险信号。
- 不要为了判断病态轻易计算 $A^{-1}$，实际中更常用估计和诊断。
- 条件数大时，提高算法精度只能缓解，不能改变问题本身敏感。

## 十、核心公式速查

| 内容 | 公式 |
|---|---|
| 条件数 | $\operatorname{cond}(A)=\|A\|\|A^{-1}\|$ |
| $b$ 扰动绝对误差 | $\|\delta x\|\le \|A^{-1}\|\|\delta b\|$ |
| $b$ 扰动相对误差 | $\|\delta x\|/\|x\|\le \operatorname{cond}(A)\|\delta b\|/\|b\|$ |
| $A$ 扰动相对误差 | $\dfrac{\|\delta x\|}{\|x\|}\le\dfrac{\operatorname{cond}(A)\|\delta A\|/\|A\|}{1-\operatorname{cond}(A)\|\delta A\|/\|A\|}$ |
| 综合误差界 | $\dfrac{\|\delta x\|}{\|x\|}\le\dfrac{\operatorname{cond}(A)}{1-\operatorname{cond}(A)\|\delta A\|/\|A\|}\left(\dfrac{\|\delta A\|}{\|A\|}+\dfrac{\|\delta b\|}{\|b\|}\right)$ |
| 对称矩阵 2-条件数 | $\operatorname{cond}_2(A)=\max_i|\lambda_i|/\min_i|\lambda_i|$ |
| 一般矩阵 2-条件数 | $\operatorname{cond}_2(A)=\sigma_{\max}(A)/\sigma_{\min}(A)$ |
