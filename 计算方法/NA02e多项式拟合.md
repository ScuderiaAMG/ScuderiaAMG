# 曲线拟合与函数逼近

这份笔记按知识线索整理：先分清“拟合在解决什么问题”，再推导最小二乘法，最后给出可以直接套用的完整解题通法。

## 一、先把概念讲清楚

### 拟合和插值的区别

插值和拟合都想用一个简单函数近似真实关系，但它们的目标不同。

- **插值**要求曲线穿过所有已知点：$P(x_i)=y_i$。
- **拟合**不要求穿过每个点，只要求整体误差尽量小。

如果数据点来自精确计算，插值是合理的；如果数据来自实验测量，点本身带有误差，强行穿过所有点反而会把噪声也学进去。这时更适合用拟合。

### 最小二乘法的核心想法

给定数据点
$$
(x_1,y_1),(x_2,y_2),\cdots,(x_m,y_m),
$$
选一个简单函数 $P(x)$ 去近似这些数据。每个点的误差是
$$
r_i=P(x_i)-y_i,
$$
称为**残差**。

最小二乘法选择参数，使残差平方和
$$
S=\sum_{i=1}^{m}r_i^2=\sum_{i=1}^{m}[P(x_i)-y_i]^2
$$
最小。

为什么用平方？

- 正负误差不会相互抵消。
- 平方函数可导，能用偏导数列方程。
- 大误差会被更明显地惩罚。

### 多项式拟合在做什么

最常见的拟合函数是多项式：
$$
P_n(x)=a_0+a_1x+a_2x^2+\cdots+a_nx^n.
$$

题目通常给出 $m$ 个点，要求找一个 $n$ 次多项式拟合它们。一般有
$$
n \ll m,
$$
也就是多项式次数远小于数据点个数。

若 $m=n+1$ 且要求通过所有点，那更像插值；若 $m>n+1$ 且要求误差平方和最小，那就是最小二乘拟合。

---

## 二、知识脉络

### 曲线拟合的基本问题

已知数据点 $(x_i,y_i)$，寻找一个结构简单、便于计算的函数 $P(x)$，使 $P(x_i)$ 与 $y_i$ 总体上尽可能接近。

常见误差标准有三类：

| 标准 | 目标 | 说明 |
|------|------|------|
| 极小化最大误差 | $\max_i |P(x_i)-y_i|$ 最小 | 理论上重要，但求解较复杂 |
| 最小绝对偏差 | $\sum_i |P(x_i)-y_i|$ 最小 | 抗异常值较好，但不可导 |
| 最小二乘 | $\sum_i [P(x_i)-y_i]^2$ 最小 | 计算方便，是本讲重点 |

### 一次线性拟合

设拟合函数为
$$
P(x)=a_0+a_1x.
$$

目标函数为
$$
S(a_0,a_1)=\sum_{i=1}^{m}(a_0+a_1x_i-y_i)^2.
$$

在极小点处，关于 $a_0,a_1$ 的偏导数为 0：
$$
\frac{\partial S}{\partial a_0}=2\sum_{i=1}^{m}(a_0+a_1x_i-y_i)=0,
$$
$$
\frac{\partial S}{\partial a_1}=2\sum_{i=1}^{m}(a_0+a_1x_i-y_i)x_i=0.
$$

整理得到一次拟合的正规方程：
$$
\begin{cases}
ma_0+a_1\sum x_i=\sum y_i,\\
a_0\sum x_i+a_1\sum x_i^2=\sum x_iy_i.
\end{cases}
$$

解出 $a_0,a_1$ 后，拟合直线就是
$$
P(x)=a_0+a_1x.
$$

### 一次拟合的闭式公式

如果题目只要求一次线性拟合，可以直接用：
$$
a_1=\frac{m\sum x_iy_i-\sum x_i\sum y_i}{m\sum x_i^2-(\sum x_i)^2},
$$
$$
a_0=\frac{\sum y_i-a_1\sum x_i}{m}.
$$

这个公式本质上就是解上面的 $2\times 2$ 正规方程。

### 二次多项式拟合

设
$$
P_2(x)=a_0+a_1x+a_2x^2.
$$

目标函数为
$$
S(a_0,a_1,a_2)=\sum_{i=1}^{m}(a_0+a_1x_i+a_2x_i^2-y_i)^2.
$$

令三个偏导数为 0，得到：
$$
\begin{cases}
ma_0+a_1\sum x_i+a_2\sum x_i^2=\sum y_i,\\
a_0\sum x_i+a_1\sum x_i^2+a_2\sum x_i^3=\sum x_iy_i,\\
a_0\sum x_i^2+a_1\sum x_i^3+a_2\sum x_i^4=\sum x_i^2y_i.
\end{cases}
$$

二次拟合最容易出错的地方是漏算 $\sum x_i^3$、$\sum x_i^4$ 和 $\sum x_i^2y_i$。

### 一般 $n$ 次多项式拟合

设
$$
P_n(x)=a_0+a_1x+\cdots+a_nx^n.
$$

目标函数为
$$
S(a_0,\dots,a_n)=\sum_{i=1}^{m}\left(\sum_{j=0}^{n}a_jx_i^j-y_i\right)^2.
$$

令
$$
\frac{\partial S}{\partial a_k}=0,\quad k=0,1,\dots,n,
$$
得到正规方程：
$$
\sum_{j=0}^{n}a_j\sum_{i=1}^{m}x_i^{j+k}
=
\sum_{i=1}^{m}y_ix_i^k,\quad k=0,1,\dots,n.
$$

记
$$
b_k=\sum_{i=1}^{m}x_i^k,\quad c_k=\sum_{i=1}^{m}y_ix_i^k,
$$
则正规方程可以写成矩阵形式：
$$
\begin{bmatrix}
b_0 & b_1 & \cdots & b_n\\
b_1 & b_2 & \cdots & b_{n+1}\\
\vdots & \vdots & \ddots & \vdots\\
b_n & b_{n+1} & \cdots & b_{2n}
\end{bmatrix}
\begin{bmatrix}
a_0\\a_1\\ \vdots\\a_n
\end{bmatrix}
=
\begin{bmatrix}
c_0\\c_1\\ \vdots\\c_n
\end{bmatrix}.
$$

系数矩阵是对称矩阵，左上角的 $b_0=m$。

### 矩阵观点

把多项式拟合写成矩阵形式更简洁。令
$$
A=
\begin{bmatrix}
1&x_1&x_1^2&\cdots&x_1^n\\
1&x_2&x_2^2&\cdots&x_2^n\\
\vdots&\vdots&\vdots&&\vdots\\
1&x_m&x_m^2&\cdots&x_m^n
\end{bmatrix},
\quad
\mathbf a=
\begin{bmatrix}
a_0\\a_1\\ \vdots\\a_n
\end{bmatrix},
\quad
\mathbf y=
\begin{bmatrix}
y_1\\y_2\\ \vdots\\y_m
\end{bmatrix}.
$$

拟合问题就是让
$$
A\mathbf a\approx \mathbf y
$$
的残差长度最小。正规方程为
$$
A^TA\mathbf a=A^T\mathbf y.
$$

这和前面的求和公式完全等价。

### 线性化拟合

有些模型看起来不是直线，但通过变量代换可以化成直线，再用一次最小二乘拟合。

常见形式如下：

| 原模型 | 变量代换 | 线性形式 | 参数还原 |
|--------|----------|----------|----------|
| $y=a+\dfrac{b}{x}$ | $X=\dfrac1x,\ Y=y$ | $Y=a+bX$ | 直接得到 $a,b$ |
| $y=\dfrac1{a+bx}$ | $X=x,\ Y=\dfrac1y$ | $Y=a+bX$ | 直接得到 $a,b$ |
| $y=ae^{bx}$ | $X=x,\ Y=\ln y,\ A=\ln a$ | $Y=A+bX$ | $a=e^A$ |
| $y=ae^{b/x}$ | $X=\dfrac1x,\ Y=\ln y,\ A=\ln a$ | $Y=A+bX$ | $a=e^A$ |
| $y=ae^{-b/x}$ | $X=\dfrac1x,\ Y=\ln y,\ A=\ln a,\ B=-b$ | $Y=A+BX$ | $a=e^A,\ b=-B$ |
| $y=ax^b$ | $X=\ln x,\ Y=\ln y,\ A=\ln a$ | $Y=A+bX$ | $a=e^A$ |
| $y=a+b\ln x$ | $X=\ln x,\ Y=y$ | $Y=a+bX$ | 直接得到 $a,b$ |

注意：取对数要求数据满足 $y_i>0$；令 $X=1/x$ 要求 $x_i\neq0$。

### 拟合误差的度量

求出 $P(x)$ 后，通常要计算：

残差：
$$
r_i=P(x_i)-y_i.
$$

残差平方和：
$$
S=\sum_{i=1}^{m}r_i^2.
$$

均方误差或均方根误差：
$$
\sigma=\sqrt{\frac1m\sum_{i=1}^{m}r_i^2}.
$$

有些教材会把 $\sqrt{\sum r_i^2}$ 称为误差指标。考试时按题目定义来；如果题目写“均方误差”，通常使用 $\sqrt{\frac1m\sum r_i^2}$。

---

## 三、解题通法

### 1. 先判定模型

拿到题目先确定拟合函数：

| 题目类型 | 拟合形式 |
|----------|----------|
| 一次拟合、拟合直线 | $P(x)=a_0+a_1x$ |
| 二次拟合、抛物线拟合 | $P_2(x)=a_0+a_1x+a_2x^2$ |
| $n$ 次多项式拟合 | $P_n(x)=a_0+a_1x+\cdots+a_nx^n$ |
| 指数、幂函数、倒数模型 | 先变量代换，化成 $Y=A+BX$ |

判断标准：若 $m>n+1$ 且要求平方误差最小，就是最小二乘拟合；若 $m=n+1$ 且要求通过所有点，更像插值。

### 2. 多项式拟合的统一步骤

设
$$
P_n(x)=a_0+a_1x+\cdots+a_nx^n.
$$

按下面流程做：

1. 计算求和量
   $$
   b_k=\sum_{i=1}^{m}x_i^k,\quad k=0,1,\dots,2n,
   $$
   $$
   c_k=\sum_{i=1}^{m}y_ix_i^k,\quad k=0,1,\dots,n.
   $$
   其中 $b_0=m$。

2. 列正规方程
   $$
   \begin{bmatrix}
   b_0 & b_1 & \cdots & b_n\\
   b_1 & b_2 & \cdots & b_{n+1}\\
   \vdots & \vdots & \ddots & \vdots\\
   b_n & b_{n+1} & \cdots & b_{2n}
   \end{bmatrix}
   \begin{bmatrix}
   a_0\\
   a_1\\
   \vdots\\
   a_n
   \end{bmatrix}
   =
   \begin{bmatrix}
   c_0\\
   c_1\\
   \vdots\\
   c_n
   \end{bmatrix}.
   $$

3. 解出 $a_0,a_1,\dots,a_n$，写出 $P_n(x)$。

4. 若要求误差，代回原数据点计算
   $$
   r_i=P_n(x_i)-y_i,\quad S=\sum r_i^2,\quad \sigma=\sqrt{S/m}.
   $$

口诀：$n$ 次拟合要算到 $x^{2n}$，右端要算到 $x^ny$。

### 3. 常用特例

**一次拟合**只需计算
$$
m,\sum x_i,\sum y_i,\sum x_i^2,\sum x_iy_i.
$$
正规方程为
$$
\begin{cases}
ma_0+a_1\sum x_i=\sum y_i,\\
a_0\sum x_i+a_1\sum x_i^2=\sum x_iy_i.
\end{cases}
$$

**二次拟合**需计算
$$
m,\sum x_i,\sum x_i^2,\sum x_i^3,\sum x_i^4,
$$
$$
\sum y_i,\sum x_iy_i,\sum x_i^2y_i.
$$
正规方程为
$$
\begin{cases}
ma_0+a_1\sum x_i+a_2\sum x_i^2=\sum y_i,\\
a_0\sum x_i+a_1\sum x_i^2+a_2\sum x_i^3=\sum x_iy_i,\\
a_0\sum x_i^2+a_1\sum x_i^3+a_2\sum x_i^4=\sum x_i^2y_i.
\end{cases}
$$

### 4. 线性化拟合

目标是把原模型化成
$$
Y=A+BX,
$$
再对 $(X_i,Y_i)$ 做一次线性拟合，最后还原参数。

| 原模型 | 代换 | 还原 |
|--------|------|------|
| $y=a+\dfrac bx$ | $X=1/x,\ Y=y$ | 直接得 $a,b$ |
| $y=\dfrac1{a+bx}$ | $X=x,\ Y=1/y$ | 直接得 $a,b$ |
| $y=ae^{bx}$ | $X=x,\ Y=\ln y,\ A=\ln a$ | $a=e^A$ |
| $y=ax^b$ | $X=\ln x,\ Y=\ln y,\ A=\ln a$ | $a=e^A$ |
| $y=ae^{-b/x}$ | $X=1/x,\ Y=\ln y,\ A=\ln a,\ B=-b$ | $a=e^A,\ b=-B$ |

注意：线性化后最小的是变换后空间的误差；若题目要求原始误差，要把参数还原后用原模型计算 $P(x_i)-y_i$。

### 5. 易错点

- $n$ 次多项式有 $n+1$ 个未知系数。
- 正规方程左端矩阵应当对称，且左上角是 $b_0=m$。
- 二次拟合不要漏掉 $\sum x_i^3$、$\sum x_i^4$、$\sum x_i^2y_i$。
- 线性化题最后必须把 $X,Y,A,B$ 还原成原来的 $x,y,a,b$。
- 均方根误差一般用 $\sigma=\sqrt{S/m}$，若题目另有定义，以题目为准。

---

## 四、公式速查

### 一次拟合

$$
\begin{cases}
ma_0+a_1\sum x_i=\sum y_i,\\
a_0\sum x_i+a_1\sum x_i^2=\sum x_iy_i.
\end{cases}
$$

$$
a_1=\frac{m\sum x_iy_i-\sum x_i\sum y_i}{m\sum x_i^2-(\sum x_i)^2},
\quad
a_0=\frac{\sum y_i-a_1\sum x_i}{m}.
$$

### 二次拟合

$$
\begin{cases}
ma_0+a_1\sum x_i+a_2\sum x_i^2=\sum y_i,\\
a_0\sum x_i+a_1\sum x_i^2+a_2\sum x_i^3=\sum x_iy_i,\\
a_0\sum x_i^2+a_1\sum x_i^3+a_2\sum x_i^4=\sum x_i^2y_i.
\end{cases}
$$

### $n$ 次拟合

$$
\sum_{j=0}^{n}a_j\sum_{i=1}^{m}x_i^{j+k}
=
\sum_{i=1}^{m}y_ix_i^k,\quad k=0,1,\dots,n.
$$

### 矩阵形式

$$
A^TA\mathbf a=A^T\mathbf y.
$$

### 残差平方和与均方根误差

$$
S=\sum_{i=1}^{m}[P(x_i)-y_i]^2,
\quad
\sigma=\sqrt{\frac Sm}.
$$
