# 第三章 数值积分 - 课件例题

## NA03 计算方法中的核心思想与问题主线

本部分为课程导论内容，讲解了计算方法的基本概念、课程定位和实际问题求解流程，未包含数值积分的具体例题。

---

## NA03a 数值积分

### 例1: 梯形公式的代数精度检验

**题目**：对于 $[a,b]$ 上 1 次插值，有梯形公式

$$
\int_a^b f(x)\,dx \approx \frac{b-a}{2}[f(a)+f(b)]
$$

考察其代数精度。

**解**：

代数精度定义为：若某个求积公式所对应的误差 $R[f]$ 满足 $R[P_k]=0$ 对任意 $k \le n$ 阶的多项式成立，且 $R[P_{n+1}] \neq 0$ 对某个 $n+1$ 阶多项式成立，则称此求积公式的代数精度为 $n$。

逐次检查梯形公式是否精确成立：

**(1) 代入 $P_0(x)=1$ ：**

左边：
$$\int_a^b 1\,dx = b-a$$
右边：
$$\frac{b-a}{2}[1+1] = b-a$$
左边 = 右边，精确成立。

**(2) 代入 $P_1(x)=x$ ：**

左边：
$$\int_a^b x\,dx = \left.\frac{x^2}{2}\right|_a^b = \frac{b^2-a^2}{2}$$
右边：
$$\frac{b-a}{2}[a+b] = \frac{b-a}{2}(a+b) = \frac{b^2-a^2}{2}$$
左边 = 右边，精确成立。

**(3) 代入 $P_2(x)=x^2$ ：**

左边：
$$\int_a^b x^2\,dx = \left.\frac{x^3}{3}\right|_a^b = \frac{b^3-a^3}{3}$$
右边：
$$\frac{b-a}{2}[a^2+b^2]$$
由于
$$\frac{b^3-a^3}{3} = \frac{(b-a)(a^2+ab+b^2)}{3} \neq \frac{b-a}{2}(a^2+b^2)$$
因此公式不精确成立。

故梯形公式的代数精度为 $\boxed{1}$。

---

### 例2 (课本例1): 用梯形公式和Simpson公式计算积分

**题目**：试分别用梯形公式和抛物线公式（Simpson公式）计算积分：
$$\int_{0.5}^{1} \sqrt{x}\,dx$$

**解**：

**方法一：梯形公式**

梯形公式：$\displaystyle\int_a^b f(x)\,dx \approx \frac{b-a}{2}[f(a)+f(b)]$

代入 $a=0.5$，$b=1$，$f(x)=\sqrt{x}$：

$$\begin{aligned}
\int_{0.5}^{1} \sqrt{x}\,dx
&\approx \frac{1-0.5}{2}[\sqrt{0.5}+\sqrt{1}] \\
&= 0.25 \times (0.70710678 + 1) \\
&= 0.25 \times 1.70710678 \\
&= 0.426776695
\end{aligned}$$

**方法二：Simpson公式（抛物线公式）**

Simpson公式：$\displaystyle\int_a^b f(x)\,dx \approx \frac{b-a}{6}\left[f(a)+4f\!\left(\frac{a+b}{2}\right)+f(b)\right]$

代入 $a=0.5$，$b=1$，$c=\frac{a+b}{2}=0.75$：

$$\begin{aligned}
\int_{0.5}^{1} \sqrt{x}\,dx
&\approx \frac{1-0.5}{6}[\sqrt{0.5}+4\sqrt{0.75}+\sqrt{1}] \\
&= \frac{0.5}{6} \times (0.70710678 + 4\times 0.8660254 + 1) \\
&= 0.08333333 \times (0.70710678 + 3.4641016 + 1) \\
&= 0.08333333 \times 5.17120838 \\
&= 0.43093403
\end{aligned}$$

**准确值（用Newton-Leibniz公式）：**

$$\begin{aligned}
\int_{0.5}^{1} \sqrt{x}\,dx &= \int_{0.5}^{1} x^{1/2}\,dx = \left.\frac{2}{3}x^{3/2}\right|_{0.5}^{1} \\
&= \frac{2}{3}\left(1^{3/2} - 0.5^{3/2}\right) \\
&= \frac{2}{3}(1 - 0.35355339) \\
&= \frac{2}{3} \times 0.64644661 \\
&= 0.43096441
\end{aligned}$$

结果对比：

| 方法 | 近似值 | 误差 |
|:---:|:---:|:---:|
| 梯形公式 | 0.426776695 | $4.1877\times10^{-3}$ |
| Simpson公式 | 0.43093403 | $3.038\times10^{-5}$ |
| 准确值 | 0.43096441 | - |

可见Simpson公式的精度远高于梯形公式。请尝试用 $n=3,4,5$ 的Newton-Cotes公式来计算该积分。

---

## NA03b 复合求积

### 例1: 用复合求积公式计算圆周率

**题目**：利用 $\displaystyle\int_0^1 \frac{4}{1+x^2}\,dx = \pi$，分别用复合梯形公式（区间8等分）和复合Simpson公式（区间4等分）计算 $\pi$ 的近似值。

**解**：

取 $f(x)=\dfrac{4}{1+x^2}$，$a=0$，$b=1$。

**1. 复合梯形公式 $T_8$**

将 $[0,1]$ 8等分，步长 $h = \dfrac{1}{8} = 0.125$。

复合梯形公式：$\displaystyle T_n = \frac{h}{2}\left[f(a) + 2\sum_{k=1}^{n-1} f(a+kh) + f(b)\right]$

代入 $n=8$：
$$\begin{aligned}
T_8 &= \frac{0.125}{2}\Bigg[f(0) + 2\sum_{k=1}^{7} f\!\left(\frac{k}{8}\right) + f(1)\Bigg] \\
&= \frac{1}{16}\Bigg[4 + 2\sum_{k=1}^{7} \frac{4}{1+(k/8)^2} + 2\Bigg] \\
&= 3.138988494
\end{aligned}$$

**2. 复合Simpson公式 $S_4$**

将 $[0,1]$ 4等分，步长 $h = 0.25$，每个子区间再用Simpson公式（需使用子区间中点）。计算节点为 $x_k = \dfrac{k}{8},\;k=0,1,\ldots,8$。

$$\begin{aligned}
S_4 &= \frac{h}{6}\Bigg[f(0) + 4\sum_{k=0}^{3} f(x_{k+1/2}) + 2\sum_{k=1}^{3} f(x_k) + f(1)\Bigg] \\
&= \frac{0.25}{6}\Bigg[f(0) + 4\big(f(0.125)+f(0.375)+f(0.625)+f(0.875)\big) \\
&\qquad\qquad + 2\big(f(0.25)+f(0.5)+f(0.75)\big) + f(1)\Bigg] \\
&= 3.141592502
\end{aligned}$$

**3. 结果分析**

| 方法 | 近似值 | 误差 |
|:---:|:---:|:---:|
| 复合梯形 $T_8$ | 3.138988494 | $2.60\times10^{-3}$ |
| 复合Simpson $S_4$ | 3.141592502 | $1.52\times10^{-7}$ |
| 真值 $\pi$ | 3.141592654 | - |

可见在计算量基本相同（都需要在9个点上求函数值）的条件下，Simpson公式的精度远高于梯形公式。

---

### 例2: 复合梯形公式的精度分析

**题目**：若用复合梯形公式计算积分 $\displaystyle\int_0^1 e^x\,dx$，问积分区间要等分多少（即 $n$ 取多少）才能保证结果有五位有效数字？

**解**：

**Step 1: 复合梯形公式的误差公式**

复合梯形公式的误差为：$\displaystyle R_n(f) = -\frac{(b-a)h^2}{12} f''(\xi),\quad \xi\in(a,b),\quad h = \frac{b-a}{n}$

**Step 2: 确定被积函数的二阶导数**

$f(x) = e^x$，则 $f'(x) = e^x$，$f''(x) = e^x$。

在 $[0,1]$ 上，$|f''(x)| = e^x \le e$（单调递增，最大值在 $x=1$ 处）。

**Step 3: 误差上界估计**

$$|R_n(f)| \le \frac{(b-a)h^2}{12} \cdot e = \frac{1 \cdot (1/n)^2}{12} \cdot e = \frac{e}{12n^2}$$

**Step 4: 有效数字条件**

原积分的准确值 $\displaystyle\int_0^1 e^x\,dx = e-1 \approx 1.71828$ 具有一位整数。要使计算结果有五位有效数字，需要绝对误差不超过 $0.5\times10^{-4}$。

即：
$$\frac{e}{12n^2} \le \frac{1}{2}\times10^{-4}$$

**Step 5: 解出 $n$**

$$\frac{e}{12n^2} \le 5\times10^{-5}$$
$$n^2 \ge \frac{e}{6\times10^{-4}} = \frac{e\times10^4}{6}$$

代入 $e \approx 2.71828$：

$$n^2 \ge \frac{2.71828\times10^4}{6} \approx 4530.5$$
$$n \ge \sqrt{4530.5} \approx 67.3$$

故取 $n \ge 68$（等分68份以上），即可保证五位有效数字。

---

### 例3 (Romberg算法): 计算 $\displaystyle\int_0^1\frac{\sin x}{x}\,dx$

**题目**：用Romberg算法计算 $\displaystyle\int_0^1\frac{\sin x}{x}\,dx$，计算到Romberg值。已知函数值如下表：

| $x$ | 0 | 0.125 | 0.25 | 0.375 | 0.5 | 0.625 | 0.75 | 0.875 | 1 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $f(x)$ | 1 | 0.9973978 | 0.9896158 | 0.9767267 | 0.958851 | 0.9361556 | 0.9088516 | 0.8771925 | 0.8414709 |

其中 $f(x) = \dfrac{\sin x}{x}$（$x=0$ 时定义为极限值 $1$）。

**解**：

Romberg算法的基本思想：先计算复合梯形序列 $T_1,T_2,T_4,T_8,\ldots$，然后通过Richardson外推加速得到更高精度的结果。

外推公式：$\displaystyle T_i^{(k)} = \frac{4^k T_{i+1}^{(k-1)} - T_i^{(k-1)}}{4^k - 1}$

其中 $T_i^{(0)}$ 为复合梯形值，$T_i^{(1)}$ 相当于Simpson值，$T_i^{(2)}$ 相当于Cotes值，$T_i^{(3)}$ 为Romberg值。

**Step 1: 计算复合梯形序列**

$$\begin{aligned}
T_1 &= T_0^{(0)} = \frac{1}{2}[f(0)+f(1)] = \frac{1}{2}(1+0.8414709) = 0.9207355 \\
T_2 &= T_1^{(0)} = \frac{T_1}{2} + \frac{1}{2}f(0.5) = \frac{0.9207355}{2} + \frac{1}{2}\times0.958851 = 0.9397933 \\
T_4 &= T_2^{(0)} = \frac{T_2}{2} + \frac{1}{4}[f(0.25)+f(0.75)] \\
&= \frac{0.9397933}{2} + \frac{1}{4}(0.9896158+0.9088516) = 0.9445135 \\
T_8 &= T_3^{(0)} = \frac{T_4}{2} + \frac{1}{8}[f(0.125)+f(0.375)+f(0.625)+f(0.875)] \\
&= \frac{0.9445135}{2} + \frac{1}{8}(0.9973978+0.9767267+0.9361556+0.8771925) = 0.9456909
\end{aligned}$$

**Step 2: Richardson外推 — 第1列（Simpson值）**

$$\begin{aligned}
T_0^{(1)} &= \frac{4T_1^{(0)} - T_0^{(0)}}{3} = \frac{4\times0.9397933 - 0.9207355}{3} = 0.9461459 \\
T_1^{(1)} &= \frac{4T_2^{(0)} - T_1^{(0)}}{3} = \frac{4\times0.9445135 - 0.9397933}{3} = 0.9460869 \\
T_2^{(1)} &= \frac{4T_3^{(0)} - T_2^{(0)}}{3} = \frac{4\times0.9456909 - 0.9445135}{3} = 0.9460830
\end{aligned}$$

**Step 3: Richardson外推 — 第2列（Cotes值）**

$$\begin{aligned}
T_0^{(2)} &= \frac{16T_1^{(1)} - T_0^{(1)}}{15} = \frac{16\times0.9460869 - 0.9461459}{15} \approx 0.9460830 \\
T_1^{(2)} &= \frac{16T_2^{(1)} - T_1^{(1)}}{15} = \frac{16\times0.9460830 - 0.9460869}{15} \approx 0.9460831
\end{aligned}$$

**Step 4: Richardson外推 — 第3列（Romberg值）**

$$T_0^{(3)} = \frac{64T_1^{(2)} - T_0^{(2)}}{63} = \frac{64\times0.9460831 - 0.9460830}{63} \approx 0.9460833$$

**最终Romberg表：**

| $k$ | $T_i^{(0)}$ (梯形) | $T_i^{(1)}$ (Simpson) | $T_i^{(2)}$ (Cotes) | $T_i^{(3)}$ (Romberg) |
|:---:|:---:|:---:|:---:|:---:|
| $i=0$ | 0.9207355 | 0.9461459 | 0.9460830 | 0.9460833 |
| $i=1$ | 0.9397933 | 0.9460869 | 0.9460831 | |
| $i=2$ | 0.9445135 | 0.9460830 | | |
| $i=3$ | 0.9456909 | | | |

积分准确值 $\displaystyle\int_0^1\frac{\sin x}{x}\,dx = \mathrm{Si}(1) \approx 0.9460830704$。Romberg外推结果 $0.9460833$ 已精确到小数点后6位。

---

### 例4 (课上习题): Romberg算法计算 $\pi$

**题目**：利用Romberg算法计算 $\displaystyle\int_0^1\frac{4}{1+x^2}\,dx = \pi$，计算到 $R_1$（Romberg值）。

**解**：

$f(x) = \dfrac{4}{1+x^2}$，$a=0$，$b=1$。

**Step 1: 复合梯形序列**

$$\begin{aligned}
T_1 &= \frac{1}{2}[f(0)+f(1)] = \frac{1}{2}(4+2) = 3 \\
T_2 &= \frac{T_1}{2} + \frac{1}{2}f(0.5) = \frac{3}{2} + \frac{1}{2}\cdot\frac{4}{1+0.25} = 1.5 + \frac{1}{2}\times3.2 = 3.1 \\
T_4 &= \frac{T_2}{2} + \frac{1}{4}\big[f(0.25)+f(0.75)\big] \\
&= \frac{3.1}{2} + \frac{1}{4}\left(\frac{4}{1+0.0625} + \frac{4}{1+0.5625}\right) \\
&= 1.55 + \frac{1}{4}(3.764706 + 2.56) = 1.55 + 1.581177 = 3.131177 \\
T_8 &= \frac{T_4}{2} + \frac{1}{8}\big[f(0.125)+f(0.375)+f(0.625)+f(0.875)\big] \\
&= \frac{3.131177}{2} + \frac{1}{8}\Bigg[\frac{4}{1+0.015625} + \frac{4}{1+0.140625} + \frac{4}{1+0.390625} + \frac{4}{1+0.765625}\Bigg] \\
&= 3.138989
\end{aligned}$$

**Step 2: 外推得到Simpson值**

$$\begin{aligned}
S_1 = \frac{4T_2 - T_1}{3} = \frac{4\times3.1 - 3}{3} = \frac{9.4}{3} = 3.133333 \\
S_2 = \frac{4T_4 - T_2}{3} = \frac{4\times3.131177 - 3.1}{3} = \frac{9.424708}{3} = 3.141569 \\
S_4 = \frac{4T_8 - T_4}{3} = \frac{4\times3.138989 - 3.131177}{3} = \frac{9.424779}{3} = 3.141593
\end{aligned}$$

**Step 3: 外推得到Cotes值**

$$\begin{aligned}
C_1 = \frac{16S_2 - S_1}{15} = \frac{16\times3.141569 - 3.133333}{15} = \frac{47.131771}{15} = 3.142118 \\
C_2 = \frac{16S_4 - S_2}{15} = \frac{16\times3.141593 - 3.141569}{15} = \frac{47.123919}{15} = 3.141595
\end{aligned}$$

**Step 4: 外推得到Romberg值 $R_1$**

$$R_1 = \frac{64C_2 - C_1}{63} = \frac{64\times3.141595 - 3.142118}{63} = \frac{197.919936}{63} = 3.141586$$

$R_1 = 3.141586$ 与 $\pi = 3.141593$ 相比，误差约 $6\times10^{-6}$。

---

### 例5: 用Gauss-Legendre求积公式计算 $\displaystyle\int_0^{\pi/2}\sin t\,dt$

**题目**：用 $n=2$（三点）Gauss-Legendre求积公式计算 $\displaystyle\int_0^{\pi/2}\sin t\,dt$ 的近似值。

**解**：

**Step 1: 区间变换**

Gauss-Legendre求积公式的标准区间为 $[-1,1]$。将 $t\in[0,\pi/2]$ 变换到 $x\in[-1,1]$：

$$t = \frac{b-a}{2}x + \frac{a+b}{2} = \frac{\pi}{4}x + \frac{\pi}{4},\quad dt = \frac{\pi}{4}\,dx$$

则
$$I = \int_0^{\pi/2}\sin t\,dt = \int_{-1}^1 \sin\!\left(\frac{\pi}{4}(x+1)\right)\cdot\frac{\pi}{4}\,dx = \frac{\pi}{4}\int_{-1}^1 f(x)\,dx$$

其中 $f(x)=\sin\!\left(\dfrac{\pi}{4}(x+1)\right)$。

**Step 2: 三点Gauss-Legendre公式 ($n=2$)**

三点Gauss-Legendre公式的节点和系数为：

$$x_0 = -\sqrt{\frac{3}{5}} \approx -0.77459667,\; x_1 = 0,\; x_2 = \sqrt{\frac{3}{5}} \approx 0.77459667$$
$$A_0 = \frac{5}{9},\; A_1 = \frac{8}{9},\; A_2 = \frac{5}{9}$$

**Step 3: 计算近似积分**

$$\begin{aligned}
I &\approx \frac{\pi}{4}\left[A_0 f(x_0) + A_1 f(x_1) + A_2 f(x_2)\right] \\
&= \frac{\pi}{4}\Bigg[\frac{5}{9}\sin\!\left(\frac{\pi}{4}(-0.77459667+1)\right) + \frac{8}{9}\sin\!\left(\frac{\pi}{4}(0+1)\right) + \frac{5}{9}\sin\!\left(\frac{\pi}{4}(0.77459667+1)\right)\Bigg] \\
&= \frac{\pi}{4}\Bigg[\frac{5}{9}\sin(0.17698) + \frac{8}{9}\sin\!\left(\frac{\pi}{4}\right) + \frac{5}{9}\sin(1.39378)\Bigg] \\
&= \frac{\pi}{4}\left(\frac{5}{9}\times0.1760 + \frac{8}{9}\times0.7071 + \frac{5}{9}\times0.9848\right) \\
&= \frac{\pi}{4}(0.09778 + 0.62853 + 0.54711) \\
&= \frac{\pi}{4}\times1.27342 \\
&= 1.000008
\end{aligned}$$

准确值 $\displaystyle\int_0^{\pi/2}\sin t\,dt = 1$，近似值为 $1.000008$，误差仅 $8\times10^{-6}$，精度很高。

---

### 例6: 构造带权 $\sqrt{x}$ 的Gauss型求积公式

**题目**：试构造形如 $\displaystyle\int_0^1 \sqrt{x}\,f(x)\,dx \approx A_0 f(x_0) + A_1 f(x_1)$ 的Gauss型求积公式，并用此公式计算 $\displaystyle\int_0^1 \sqrt{x}\,e^x\,dx$ 的近似值。

**解**：

对于带权 $\rho(x)=\sqrt{x}$ 的积分，构造两点Gauss公式的关键是找到在 $[0,1]$ 上关于权 $\sqrt{x}$ 正交的多项式 $\varphi_2(x)$，其零点即为Gauss点。

**Step 1: 构造正交多项式**

设正交多项式族 $\{\varphi_0,\varphi_1,\varphi_2\}$：
$$\varphi_0(x)=1,\quad \varphi_1(x)=x+a,\quad \varphi_2(x)=x^2+bx+c$$

内积定义：$\langle \varphi_i,\varphi_j\rangle = \displaystyle\int_0^1 \sqrt{x}\,\varphi_i(x)\varphi_j(x)\,dx$。

**(1) 由 $\langle\varphi_1,\varphi_0\rangle=0$ 求 $a$：**

$$\int_0^1 \sqrt{x}\,(x+a)\,dx = \int_0^1 (x^{3/2} + a x^{1/2})\,dx = \left[\frac{2}{5}x^{5/2} + \frac{2a}{3}x^{3/2}\right]_0^1 = \frac{2}{5} + \frac{2a}{3} = 0$$

解得 $a = -\dfrac{3}{5}$，故 $\varphi_1(x) = x - \dfrac{3}{5}$。

**(2) 由 $\langle\varphi_2,\varphi_0\rangle=0$ 和 $\langle\varphi_2,\varphi_1\rangle=0$ 求 $b,c$：**

由 $\langle\varphi_2,\varphi_0\rangle = 0$：
$$\int_0^1 \sqrt{x}\,(x^2+bx+c)\,dx = \frac{2}{7} + \frac{2b}{5} + \frac{2c}{3} = 0 \quad\Rightarrow\quad \frac{1}{7} + \frac{b}{5} + \frac{c}{3} = 0 \tag{1}$$

由 $\langle\varphi_2,\varphi_1\rangle = 0$：
$$\int_0^1 \sqrt{x}\,(x^2+bx+c)\left(x-\frac{3}{5}\right)dx = 0$$

展开被积函数：
$$\sqrt{x}\,\left[x^3 + \left(b-\frac{3}{5}\right)x^2 + \left(c-\frac{3b}{5}\right)x - \frac{3c}{5}\right]$$

逐项积分：
$$\frac{2}{9} + \frac{2}{7}\left(b-\frac{3}{5}\right) + \frac{2}{5}\left(c-\frac{3b}{5}\right) - \frac{2}{3}\cdot\frac{3c}{5} = 0$$

化简：
$$\frac{2}{9} + \frac{2b}{7} - \frac{6}{35} + \frac{2c}{5} - \frac{6b}{25} - \frac{2c}{5} = 0$$

$$\frac{2}{9} - \frac{6}{35} + \frac{2b}{7} - \frac{6b}{25} = 0$$

$$\frac{16}{315} + b\left(\frac{2}{7} - \frac{6}{25}\right) = \frac{16}{315} + \frac{8b}{175} = 0$$

$$\Rightarrow b = -\frac{16}{315}\times\frac{175}{8} = -\frac{10}{9}$$

代入 (1) 式：
$$\frac{1}{7} + \frac{-10/9}{5} + \frac{c}{3} = \frac{1}{7} - \frac{2}{9} + \frac{c}{3} = -\frac{5}{63} + \frac{c}{3} = 0$$

$$\Rightarrow \frac{c}{3} = \frac{5}{63} \;\Rightarrow\; c = \frac{5}{21}$$

因此：
$$\varphi_2(x) = x^2 - \frac{10}{9}x + \frac{5}{21}$$

**Step 2: 求Gauss点**

求解 $\varphi_2(x)=0$：
$$x = \frac{\frac{10}{9} \pm \sqrt{\left(\frac{10}{9}\right)^2 - 4\times\frac{5}{21}}}{2}$$

计算判别式：
$$\Delta = \frac{100}{81} - \frac{20}{21} = \frac{480}{1701} = \frac{160}{567}$$
$$\sqrt{\Delta} = \sqrt{\frac{160}{567}} \approx 0.5312$$

故：
$$x_0 = \frac{\frac{10}{9} + 0.5312}{2} \approx 0.8212,\quad x_1 = \frac{\frac{10}{9} - 0.5312}{2} \approx 0.2899$$

**Step 3: 求求积系数 $A_0,A_1$**

令公式对 $f(x)=1$ 和 $f(x)=x$ 精确成立：

$$\begin{cases}
A_0 + A_1 = \displaystyle\int_0^1 \sqrt{x}\,dx = \frac{2}{3} \\
A_0 x_0 + A_1 x_1 = \displaystyle\int_0^1 x^{3/2}\,dx = \frac{2}{5}
\end{cases}$$

代入 $x_0\approx0.8212$，$x_1\approx0.2899$：

$$\begin{cases}
A_0 + A_1 = \frac{2}{3} \approx 0.6667 \\
0.8212A_0 + 0.2899A_1 = 0.4
\end{cases}$$

由第一式 $A_1 = \frac{2}{3} - A_0$，代入第二式：

$$0.8212A_0 + 0.2899\left(\frac{2}{3} - A_0\right) = 0.4$$
$$0.5313A_0 = 0.2067$$
$$A_0 \approx 0.3891,\quad A_1 = 0.6667 - 0.3891 = 0.2776$$

因此所求公式为：
$$\int_0^1 \sqrt{x}\,f(x)\,dx \approx 0.3891\,f(0.8212) + 0.2776\,f(0.2899)$$

**Step 4: 计算 $\displaystyle\int_0^1 \sqrt{x}\,e^x\,dx$**

取 $f(x)=e^x$：

$$\begin{aligned}
\int_0^1 \sqrt{x}\,e^x\,dx &\approx 0.3891\,e^{0.8212} + 0.2776\,e^{0.2899} \\
&= 0.3891\times2.2735 + 0.2776\times1.3363 \\
&= 0.8846 + 0.3709 \\
&= 1.2555
\end{aligned}$$

---

### 例7: 确定求积公式的系数使代数精度最高

**题目**：试确定求积公式
$$\int_{-1}^1 f(x)\,dx \approx a\,f(-\sqrt{0.6}) + b\,f(0) + c\,f(\sqrt{0.6})$$
中的待定系数 $a,b,c$，使其代数精度尽量高，并指出公式有几次代数精度，判断是否为Gauss型公式。

**解**：

**Step 1: 建立方程组**

令公式对 $f(x)=1,\,x,\,x^2$ 精确成立（三个未知数需三个方程）：

**(1) 代入 $f(x)=1$：**
$$\int_{-1}^1 1\,dx = 2 = a + b + c$$

**(2) 代入 $f(x)=x$：**
$$\int_{-1}^1 x\,dx = 0 = -\sqrt{0.6}\,a + 0 + \sqrt{0.6}\,c = \sqrt{0.6}(-a+c)$$
$$\Rightarrow -a + c = 0 \Rightarrow a = c$$

**(3) 代入 $f(x)=x^2$：**
$$\int_{-1}^1 x^2\,dx = \frac{2}{3} = a(\sqrt{0.6})^2 + c(\sqrt{0.6})^2 = 0.6(a+c) = 1.2a$$
$$\Rightarrow a = \frac{2}{3}\times\frac{1}{1.2} = \frac{5}{9},\quad c = \frac{5}{9}$$

再由 $a+b+c=2$：
$$b = 2 - a - c = 2 - \frac{5}{9} - \frac{5}{9} = \frac{8}{9}$$

故 $a = \dfrac{5}{9},\; b = \dfrac{8}{9},\; c = \dfrac{5}{9}$。

**Step 2: 检验更高次多项式的精确性**

此时求积公式为：
$$\int_{-1}^1 f(x)\,dx \approx \frac{5}{9}\,f(-\sqrt{0.6}) + \frac{8}{9}\,f(0) + \frac{5}{9}\,f(\sqrt{0.6})$$

这恰好是三点Gauss-Legendre求积公式。继续检验：

**(4) 代入 $f(x)=x^3$：**
$$\int_{-1}^1 x^3\,dx = 0,\quad \text{右边} = \frac{5}{9}(-\sqrt{0.6})^3 + \frac{5}{9}(\sqrt{0.6})^3 = 0$$
精确成立。

**(5) 代入 $f(x)=x^4$：**
$$\int_{-1}^1 x^4\,dx = \frac{2}{5} = 0.4$$
$$\text{右边} = \frac{10}{9}\times(\sqrt{0.6})^4 = \frac{10}{9}\times0.36 = 0.4$$
精确成立。

**(6) 代入 $f(x)=x^5$：**
$$\int_{-1}^1 x^5\,dx = 0,\quad \text{右边} = \frac{5}{9}(-\sqrt{0.6})^5 + \frac{5}{9}(\sqrt{0.6})^5 = 0$$
精确成立。

**(7) 代入 $f(x)=x^6$：**
$$\int_{-1}^1 x^6\,dx = \frac{2}{7} \approx 0.285714$$
$$\text{右边} = \frac{10}{9}\times(\sqrt{0.6})^6 = \frac{10}{9}\times0.216 = 0.24 \neq \frac{2}{7}$$
不精确成立。

**Step 3: 结论**

该求积公式对 $f(x)=1,x,x^2,x^3,x^4,x^5$ 均精确成立，对 $f(x)=x^6$ 不精确成立，故代数精度为 $5$。

由于三点公式具有 $5 = 2\times2+1$ 次代数精度，根据Gauss型求积公式的定义，该公式是Gauss型求积公式（即三点Gauss-Legendre公式）。

---

## NA03c 数值积分高斯求积

### 说明

NA03c的内容与NA03b后半部分的高斯求积内容高度重合。此处列出NA03c中出现的例题，与NA03b对应。

### 例1 (同NA03a例1): 梯形公式的代数精度检验

同NA03a例1，结论：梯形公式的代数精度为 $1$。

### 例2 (同NA03b例5): 用Gauss-Legendre公式求解

课件中列出了梯形公式、Simpson公式和高斯公式求解 $\displaystyle\int_0^{\pi/2}\sin t\,dt$ 的对比。详细解答见NA03b例5。

### 例3 (同NA03b例6): 构造带权 $\sqrt{x}$ 的Gauss型求积公式

同NA03b例6。

### 例4 (同NA03b例7): 确定三点求积公式的系数

同NA03b例7。结论：$a=c=5/9,\;b=8/9$，代数精度为 $5$，是Gauss型求积公式。

### 例5 (同NA03b例4): Romberg算法求 $\pi$

同NA03b例4（课上习题）。结论：$R_1 = 3.141586$。

