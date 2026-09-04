# 自动控制原理II —— 线性定常系统状态方程的解（知识点总结）

> **来源课件**：Lesson 3 9.4 State Equation's Solution(1.5x45').pdf（时长 1.5×45 分钟），提取文本共 **25 页**
> **本节主题**：§9.4 线性定常系统状态方程的解 —— 连续系统状态方程的求解（齐次 / 非齐次）、状态转移矩阵 $\Phi(t)=e^{At}$ 的定义、性质与计算、线性离散系统状态空间表达式的建立与求解（连续系统离散化）；包含例题 **Ex.9-13 ~ Ex.9-17**

---

## 引言：动态系统的数学表示与动态分析

### 系统的数学表示（Mathematical Representation）

- 动态系统可用两类数学模型描述：
  - **传递函数（Transfer function）** —— 经典控制理论（外部描述）；
  - **状态空间（State Space）** —— 现代控制理论（内部描述）。
- 状态空间分析的核心是**矩阵运算——状态转移矩阵（State Transition Matrix）**，由此求得系统的**动态响应（Dynamic Response）**。

### 两类动态分析

| 类型 | 内容 |
|------|------|
| 定量分析（Quantitative Analysis） | 求解动态数学模型方程，并对解进行分析 |
| 定性分析（Qualitative Analysis） | 不解方程而直接判定解的定性行为（如稳定性等） |

> 本章（9.4）进行的是**定量分析**：解状态方程 $\dot x=Ax+Bu$，得到系统动态响应。

---

## 9.4 线性定常系统状态方程的解（总体框架）

- 已知**状态方程（模型）**后，任务是**动态分析（求解状态方程）**。
- **解的存在性与唯一性条件**：系统矩阵 $A$ 与输入矩阵 $B$ 中的元素均有界（bounded）。
- 本节的求解路线：
  1. 连续系统齐次状态方程的解（两种方法：幂级数法、拉氏变换法）；
  2. 连续系统非齐次状态方程的解（直接法/积分法、拉氏变换法）；
  3. 状态转移矩阵的性质；
  4. $e^{At}$ 的计算方法（三种）；
  5. 线性离散系统状态空间表达式的建立与求解（连续方程的离散化）。

---

## 9.4.1 线性定常连续系统状态方程的解

### 1. 齐次状态方程的解（自由运动）

设齐次状态方程

$$
\dot x(t)=Ax(t)
$$

课件给出了该齐次状态方程的两类通解求法（即下述幂级数法与拉氏变换法）。

#### （1）幂级数法（Power Series Method）

**基本思想**：假设方程的解是 $t$ 的**向量幂级数**：

$$
x(t)=b_0+b_1t+b_2t^{2}+\cdots+b_k t^{k}+\cdots
$$

其中 $b_0,b_1,\cdots,b_k$ 均为 **$n$ 维向量**。

**求解要点**：对上述幂级数逐项求导，得

$$
\dot x(t)=b_1+2b_2t+3b_3t^{2}+\cdots+k b_k t^{k-1}+\cdots
$$

将 $\dot x(t)$ 与 $x(t)$ 代入 $\dot x=Ax$，并令**同次幂的系数相等（Assume the coefficients with the same power are uniform）**，得递推关系：

$$
\begin{aligned}
b_1&=Ab_0,\\
2b_2&=Ab_1,\quad 3b_3=Ab_2,\ \cdots\ ,\quad k b_k=A b_{k-1}
\end{aligned}
$$

即

$$
b_k=\frac{1}{k!}A^{k}b_0,\qquad k=1,2,3,\cdots
$$

又由 $t=0$ 时代入幂级数知 $b_0=x(0)$，故

$$
x(t)=\left(I+At+\frac{1}{2!}A^{2}t^{2}+\cdots+\frac{1}{k!}A^{k}t^{k}+\cdots\right)x(0)
$$

**定义矩阵指数函数（matrix exponential function）**：

$$
e^{At}=I+At+\frac{A^{2}t^{2}}{2!}+\cdots+\frac{A^{k}t^{k}}{k!}+\cdots
=\sum_{k=0}^{\infty}\frac{A^{k}t^{k}}{k!}
$$

于是齐次状态方程的解为

$$
\boxed{\,x(t)=e^{At}x(0)\,}
$$

其中 $e^{At}$ 称为**状态转移矩阵（state transition matrix），记作 $\Phi(t)$**。

#### （2）拉氏变换法（Laplace transformation method）

**求解要点**：对齐次方程 $\dot x=Ax$ 两边取拉氏变换：

$$
sX(s)-x(0)=AX(s)
$$

整理得

$$
(sI-A)X(s)=x(0)\quad\Longrightarrow\quad X(s)=(sI-A)^{-1}x(0)
$$

取拉氏反变换：

$$
x(t)=L^{-1}\big[(sI-A)^{-1}\big]x(0)
$$

**与幂级数法比较**，得到状态转移矩阵的**闭合形式（closed form，即解析形式 analytic form）**：

$$
\boxed{\ \Phi(t)=e^{At}=L^{-1}\big[(sI-A)^{-1}\big]\ }
$$

> **注意**：该闭合形式是由收敛的幂级数得到的，**收敛性**有保证；它把"无穷级数求和"转化为"矩阵求逆 $+$ 拉氏反变换"，是工程上最常用的计算途径。

#### 讨论：齐次方程解的物理意义

- 齐次状态方程的解描述系统**没有输入 $u(t)$ 作用时的自由运动（freedom motion）**；
- 它仅依赖状态转移矩阵 $e^{A(t-t_0)}$ 完成**初始状态的转移（transition of the initial state）**：

$$
x(t)=e^{At}x(0)
\qquad\text{或}\qquad
x(t)=e^{A(t-t_0)}x(t_0)
$$

> 这就是"状态转移矩阵"名称的由来：$\Phi(t-t_0)=e^{A(t-t_0)}$ 把 $t_0$ 时刻的状态 $x(t_0)$ 转移到 $t$ 时刻的状态 $x(t)$。

### 2. 非齐次状态方程的解

给定非齐次状态方程

$$
\dot x(t)=Ax(t)+Bu(t)
$$

其中 $x(t)\in R^{n}$，$u(t)\in R^{r}$，$A\in R^{n\times n}$，$B\in R^{n\times r}$。

#### （1）直接法（积分法，Direct method / Integral method）

**求解要点**：对方程两边**左乘** $e^{-At}$：

$$
e^{-At}\big[\dot x(t)-Ax(t)\big]=e^{-At}Bu(t)
$$

注意左端恰好是 $e^{-At}x(t)$ 的导数：

$$
\frac{d}{dt}\big[e^{-At}x(t)\big]=e^{-At}Bu(t)
$$

对两边从 $0$ 到 $t$ 积分，并利用 $t=0$ 时 $x(0)$ 已知：

$$
e^{-At}x(t)-x(0)=\int_{0}^{t}e^{-A\tau}Bu(\tau)\,d\tau
$$

整理得

$$
\boxed{\ x(t)=e^{At}x(0)+\int_{0}^{t}e^{A(t-\tau)}Bu(\tau)\,d\tau
=\Phi(t)x(0)+\int_{0}^{t}\Phi(t-\tau)Bu(\tau)\,d\tau\ }
$$

#### （2）拉氏变换法（Laplace transformation method）

**求解要点**：对方程取拉氏变换：

$$
sX(s)-x(0)=AX(s)+Bu(s)
$$

$$
(sI-A)X(s)=x(0)+Bu(s)
$$

$$
X(s)=(sI-A)^{-1}x(0)+(sI-A)^{-1}Bu(s)
$$

取拉氏反变换（由 $e^{At}=L^{-1}\big[(sI-A)^{-1}\big]$，并利用卷积定理）：

$$
x(t)=L^{-1}\big[(sI-A)^{-1}x(0)\big]+L^{-1}\big[(sI-A)^{-1}Bu(s)\big]
$$

得到与直接法完全一致的结论：

$$
\boxed{\ x(t)=e^{At}x(0)+\int_{0}^{t}e^{A(t-\tau)}Bu(\tau)\,d\tau
=\Phi(t)x(0)+\int_{0}^{t}\Phi(t-\tau)Bu(\tau)\,d\tau\ }
$$

**初始时刻为 $t_0$ 的一般形式**：

$$
\boxed{\ x(t)=\Phi(t-t_0)x(t_0)+\int_{t_0}^{t}\Phi(t-\tau)Bu(\tau)\,d\tau\ }
$$

#### 讨论：非齐次方程解的组成

非齐次状态方程的解由**两部分叠加**组成：

1. **初始状态引起的自由运动**：$\Phi(t-t_0)x(t_0)$，称为**零输入响应（zero-input response）**；
2. **输入 $u(t)$ 引起的受控运动**：$\displaystyle\int_{t_0}^{t}\Phi(t-\tau)Bu(\tau)\,d\tau$（当 $t_0=0$ 时为 $\displaystyle\int_{0}^{t}\Phi(t-\tau)Bu(\tau)\,d\tau$），称为**零状态响应（zero-state response）**。

> 注意：卷积积分中的 $\Phi(t-\tau)=e^{A(t-\tau)}$ 体现了"输入 $u(\tau)$ 在 $\tau$ 时刻的作用经状态转移矩阵延迟到 $t$ 时刻"的叠加思想，是线性系统叠加原理的体现。

---

## 9.4.2 状态转移矩阵的性质

设状态转移矩阵 $\Phi(t)=e^{At}$（$A$ 为 $n\times n$ 常数矩阵），则它具有如下 $10$ 条性质：

**1. 初始值（初始状态）**

$$
\Phi(0)=I
$$

**2. 微分关系**

$$
\dot\Phi(t)=A\Phi(t)=\Phi(t)A
$$

即 $\Phi(t)$ 本身满足齐次矩阵微分方程 $\dot\Phi=A\Phi$ 且初值 $\Phi(0)=I$；并且 $A$ 与 $e^{At}$ 可交换。

**3. 组合性（线性关系）**

$$
\Phi(t_1\pm t_2)=\Phi(t_1)\Phi(\pm t_2)=\Phi(\pm t_2)\Phi(t_1)
$$

等价地 $\Phi(t_1+t_2)=\Phi(t_1)\Phi(t_2)=\Phi(t_2)\Phi(t_1)$（同一矩阵 $A$ 的指数矩阵之间恒可交换）。

**4. 可逆性（Reversibility）**

$$
\Phi^{-1}(t)=\Phi(-t)
$$

**5. 状态转移关系（线性关系）**

$$
x(t_2)=\Phi(t_2-t_1)\,x(t_1)
$$

即状态从 $t_1$ 转移到 $t_2$ 只与时间差 $t_2-t_1$ 有关。

**6. 分段性（Segmentation，分解性质）**

$$
\Phi(t_2-t_0)=\Phi(t_2-t_1)\Phi(t_1-t_0)
$$

即转移过程可以分两段完成，中间时刻 $t_1$ 的状态可衔接（可用于分段积分、离散化等）。

**7. 幂次性质**

$$
\big[\Phi(t)\big]^{k}=\Phi(kt)
$$

**8. 与另一矩阵指数的"相加"性质（需满足可交换条件）**

- 若 $AB=BA$（两矩阵可交换），则

$$
e^{At}e^{Bt}=e^{(A+B)t}=e^{Bt}e^{At}
$$

- 若 $AB\neq BA$，则一般有

$$
e^{At}e^{Bt}\neq e^{Bt}e^{At},\qquad e^{At}e^{Bt}\neq e^{(A+B)t}
$$

> **注意**：指数相加公式 $e^{A}e^{B}=e^{A+B}$ 仅当 $AB=BA$ 时成立，这是矩阵指数与标量指数最重要的区别。

**9. 非奇异线性变换下的状态转移矩阵**

若 $\Phi(t)$ 是系统 $\dot x(t)=Ax(t)$ 的状态转移矩阵，则经过**非奇异线性变换 $x=P\bar x$**（$P$ 为非奇异变换阵）后，新系统（状态 $\bar x$，系统矩阵 $P^{-1}AP$）的状态转移矩阵为

$$
\bar\Phi(t)=P^{-1}e^{At}P=e^{\,P^{-1}AP\cdot t}
$$

**10. 两种常见的状态转移矩阵（重要公式）**

- **若 $A$ 为 $n$ 阶对角矩阵** $A=\mathrm{diag}(\lambda_1,\lambda_2,\cdots,\lambda_n)$，则

$$
\Phi(t)=e^{At}=\mathrm{diag}\big(e^{\lambda_1 t},e^{\lambda_2 t},\cdots,e^{\lambda_n t}\big)
=
\begin{bmatrix}
e^{\lambda_1 t}&0&\cdots&0\\
0&e^{\lambda_2 t}&&\vdots\\
\vdots&&\ddots&0\\
0&\cdots&0&e^{\lambda_n t}
\end{bmatrix}
$$

- **若 $A$ 为 $m$ 阶约当（Jordan）矩阵**（特征值 $\lambda$，约当块含 $m$ 重根），则

$$
\Phi(t)=e^{Jt}=e^{\lambda t}
\begin{bmatrix}
1&t&\dfrac{t^{2}}{2!}&\cdots&\dfrac{t^{m-1}}{(m-1)!}\\[8pt]
0&1&t&\ddots&\vdots\\
\vdots&\ddots&\ddots&\ddots&\dfrac{t^{2}}{2!}\\[4pt]
0&\cdots&0&1&t\\
0&\cdots&0&0&1
\end{bmatrix}
$$

即除主对角线与各上对角线上分别出现 $1,\,t,\,\dfrac{t^{2}}{2!},\cdots,\dfrac{t^{m-1}}{(m-1)!}$（均再乘以 $e^{\lambda t}$）外，其余元素为 $0$。

---

## 9.4.3 矩阵指数（状态转移矩阵）$e^{At}$ 的计算

### 方法一：直接法（矩阵幂级数法，Direct method）

对任意常数矩阵 $A$ 和**有限时间 $t$**，无穷级数

$$
e^{At}=I+At+\frac{A^{2}t^{2}}{2!}+\frac{A^{3}t^{3}}{3!}+\cdots+\sum_{k=0}^{\infty}\frac{A^{k}t^{k}}{k!}
$$

**是收敛的**，可逐项计算取近似。此法概念简单，但一般只用于低阶或数值计算。

### 方法二：线性变换法（对角形法与约当形法，Linear transform method）

**（1）对角形法**：若矩阵 $A$ 可通过非奇异线性变换化为对角形 $\Lambda=\mathrm{diag}(\lambda_1,\cdots,\lambda_n)$（即 $A$ 有 $n$ 个线性无关特征向量），则

$$
\boxed{\ e^{At}=P\,e^{\Lambda t}P^{-1}
=P
\begin{bmatrix}
e^{\lambda_1 t}&&\mathbf{0}\\
&\ddots&\\
\mathbf{0}&&e^{\lambda_n t}
\end{bmatrix}
P^{-1}\ }
$$

其中 $P$ 是使 $A$ 对角化的**非奇异线性变换矩阵**（$\Lambda=P^{-1}AP$，$P$ 的列向量为 $A$ 的特征向量）。

**（2）约当形法**：类似地，若矩阵 $A$ 可化为约当形 $J$（特征向量不足 $n$ 个，存在约当块），则

$$
\boxed{\ e^{At}=S\,e^{Jt}S^{-1}\ }
$$

其中 $S$ 为化 $A$ 为约当形 $J=S^{-1}AS$ 的变换矩阵，$e^{Jt}$ 由 9.4.2 第 10 条约当矩阵公式给出（对每个约当块分别计算后组装）。

### 方法三：拉氏变换法（Laplace transform method）

$$
\boxed{\ e^{At}=L^{-1}\big[(sI-A)^{-1}\big]\ }
$$

**求解要点**：关键步骤是求 $(sI-A)$ 的逆矩阵 $(sI-A)^{-1}$（先求伴随矩阵再除以特征多项式 $\det(sI-A)$，或对 $s$ 的函数做部分分式分解后逐项反变换）。当系统矩阵 $A$ 的**阶次较高**时，一般可采用**递推算法（Recursive Algorithm）**计算 $(sI-A)^{-1}$ 或 $e^{At}$。

---

### 例 9-13（Ex.9-13）——分别用线性变换法与拉氏变换法求 $e^{At}$

**题目**：已知系统矩阵

$$
A=\begin{bmatrix}0&1\\0&-2\end{bmatrix}
$$

试用**线性变换法**和**拉氏变换法**求矩阵指数 $e^{At}$。

**求解要点**：

**（线性变换法）**

1. 求特征值：$|\lambda I-A|=0$ 得 $\lambda_1=0,\ \lambda_2=-2$（$A$ 可对角化）；
2. 由特征向量构成变换矩阵

$$
P=\begin{bmatrix}1&1\\0&-2\end{bmatrix}
$$

（两列为 $\lambda_1=0$、$\lambda_2=-2$ 对应的特征向量）；
3. 于是 $e^{\Lambda t}=\mathrm{diag}(1,e^{-2t})$，由 $e^{At}=P e^{\Lambda t}P^{-1}$（其中 $P^{-1}=\begin{bmatrix}1&\tfrac12\\0&-\tfrac12\end{bmatrix}$）算得

$$
e^{At}
=\begin{bmatrix}1&1\\0&-2\end{bmatrix}
\begin{bmatrix}1&0\\0&e^{-2t}\end{bmatrix}
\begin{bmatrix}1&\tfrac12\\0&-\tfrac12\end{bmatrix}
=\boxed{\begin{bmatrix}1&\dfrac{1-e^{-2t}}{2}\\[6pt]0&e^{-2t}\end{bmatrix}}
$$

**（拉氏变换法）**

1. 计算

$$
sI-A=\begin{bmatrix}s&-1\\0&s+2\end{bmatrix}
$$

2. 求逆：

$$
(sI-A)^{-1}
=\begin{bmatrix}\dfrac{1}{s}&\dfrac{1}{s(s+2)}\\[8pt]0&\dfrac{1}{s+2}\end{bmatrix}
$$

3. 逐项拉氏反变换，得

$$
e^{At}=L^{-1}\big[(sI-A)^{-1}\big]
=\boxed{\begin{bmatrix}1&\dfrac{1-e^{-2t}}{2}\\[6pt]0&e^{-2t}\end{bmatrix}}
$$

**结论**：两种方法所得结果完全一致。

---

### 例 9-14（Ex.9-14）——求状态转移矩阵 $\Phi(t)$ 及其逆

**题目**：已知线性定常系统

$$
\begin{bmatrix}\dot x_1\\\dot x_2\end{bmatrix}
=
\begin{bmatrix}0&1\\-2&-3\end{bmatrix}
\begin{bmatrix}x_1\\x_2\end{bmatrix}
\qquad\text{即}\qquad
A=\begin{bmatrix}0&1\\-2&-3\end{bmatrix}
$$

求状态转移矩阵 $\Phi(t)$ 及其逆 $\Phi^{-1}(t)$。

**求解要点**：

1. 采用拉氏变换法：$\Phi(t)=e^{At}=L^{-1}\big[(sI-A)^{-1}\big]$；
2.

$$
sI-A=\begin{bmatrix}s&-1\\2&s+3\end{bmatrix},\qquad
\det(sI-A)=s^{2}+3s+2=(s+1)(s+2)
$$

3.

$$
(sI-A)^{-1}
=
\begin{bmatrix}
\dfrac{s+3}{(s+1)(s+2)} & \dfrac{1}{(s+1)(s+2)}\\[10pt]
\dfrac{-2}{(s+1)(s+2)} & \dfrac{s}{(s+1)(s+2)}
\end{bmatrix}
$$

4. 对各元素做部分分式分解：

$$
\frac{s+3}{(s+1)(s+2)}=\frac{2}{s+1}-\frac{1}{s+2},\qquad
\frac{1}{(s+1)(s+2)}=\frac{1}{s+1}-\frac{1}{s+2}
$$

$$
\frac{-2}{(s+1)(s+2)}=\frac{-2}{s+1}+\frac{2}{s+2},\qquad
\frac{s}{(s+1)(s+2)}=\frac{-1}{s+1}+\frac{2}{s+2}
$$

5. 逐项拉氏反变换得

$$
\Phi(t)=e^{At}=L^{-1}\big[(sI-A)^{-1}\big]
=\boxed{
\begin{bmatrix}
2e^{-t}-e^{-2t} & e^{-t}-e^{-2t}\\[4pt]
-2e^{-t}+2e^{-2t} & -e^{-t}+2e^{-2t}
\end{bmatrix}}
$$

6. 根据可逆性性质 $\Phi^{-1}(t)=\Phi(-t)$，将上式中的 $t$ 换成 $-t$，得

$$
\boxed{\ \Phi^{-1}(t)=\Phi(-t)=
\begin{bmatrix}
2e^{t}-e^{2t} & e^{t}-e^{2t}\\[4pt]
-2e^{t}+2e^{2t} & -e^{t}+2e^{2t}
\end{bmatrix}\ }
$$

> **要点**：求 $\Phi^{-1}(t)$ 不必重新计算，直接利用 $\Phi^{-1}(t)=\Phi(-t)$。

---

### 例 9-15（Ex.9-15）——单位阶跃输入下的时间响应

**题目**：已知系统

$$
\begin{bmatrix}\dot x_1\\\dot x_2\end{bmatrix}
=
\begin{bmatrix}0&1\\-2&-3\end{bmatrix}
\begin{bmatrix}x_1\\x_2\end{bmatrix}
+
\begin{bmatrix}0\\1\end{bmatrix}u
\qquad
A=\begin{bmatrix}0&1\\-2&-3\end{bmatrix},\ \ 
B=\begin{bmatrix}0\\1\end{bmatrix}
$$

输入 $u(t)=1(t)$（$t=0$ 时刻加入的单位阶跃函数），试求系统的时间响应关系 $x(t)$。（$A$、$B$ 同例 9-14/9-15 的 $\Phi(t)$ 已在例 9-14 中求出。）

**求解要点**：

1. 由例 9-14 已知

$$
e^{At}=
\begin{bmatrix}
2e^{-t}-e^{-2t} & e^{-t}-e^{-2t}\\[4pt]
-2e^{-t}+2e^{-2t} & -e^{-t}+2e^{-2t}
\end{bmatrix}
$$

2. 代入非齐次方程解公式（$t_0=0$，$u(\tau)=1(\tau)$）：

$$
x(t)=e^{At}x(0)+\int_{0}^{t}e^{A(t-\tau)}B\,u(\tau)\,d\tau
=e^{At}x(0)+\int_{0}^{t}e^{A(t-\tau)}B\,d\tau
$$

3. 积分项利用公式 $\displaystyle\int_{0}^{t}e^{-\alpha(t-\tau)}d\tau=\frac{1-e^{-\alpha t}}{\alpha}$ 计算（$e^{A(t-\tau)}B$ 取 $e^{A(t-\tau)}$ 的第二列，含 $e^{-(t-\tau)}$ 与 $e^{-2(t-\tau)}$ 项），得分量形式：

$$
x_1(t)=\big(2e^{-t}-e^{-2t}\big)x_1(0)+\big(e^{-t}-e^{-2t}\big)x_2(0)
+\frac{1}{2}-e^{-t}+\frac{1}{2}e^{-2t}
$$

$$
x_2(t)=\big(-2e^{-t}+2e^{-2t}\big)x_1(0)+\big(-e^{-t}+2e^{-2t}\big)x_2(0)
+e^{-t}-e^{-2t}
$$

4. **若初始状态为零** $x(0)=0$（零状态响应），则 $x(t)$ 可简化为

$$
\boxed{\ x_1(t)=\frac{1}{2}-e^{-t}+\frac{1}{2}e^{-2t},\qquad
x_2(t)=e^{-t}-e^{-2t}\ }
$$

> 稳态检验：$t\to\infty$ 时 $x_1\to\dfrac12$、$x_2\to0$，与 $\dot x=Ax+B$、$u=1$ 下平衡点 $x_{\infty}=-A^{-1}B=\big[\tfrac12,\,0\big]^{T}$ 一致。

---

### 例 9-16（Ex.9-16）——由微分方程建立状态空间表达式并求 $\Phi(t)$

**题目**：设系统动态方程为

$$
\ddot y+(a+b)\dot y+aby=\dot u+cu
$$

其中 $a$、$b$、$c$ 均为实常数。试求：
（1）系统的状态空间表达式；
（2）状态转移矩阵 $\Phi(t)$。

**求解要点**：

**（1）状态空间表达式**

- 求传递函数（零初始条件下取拉氏变换）：

$$
G(s)=\frac{Y(s)}{U(s)}
=\frac{s+c}{s^{2}+(a+b)s+ab}
=\frac{s+c}{(s+a)(s+b)}
$$

- 对 $(s+a)(s+b)$ 两根形式做**部分分式分解**：

$$
\frac{s+c}{(s+a)(s+b)}
=
\frac{\dfrac{c-a}{b-a}}{s+a}
+
\frac{\dfrac{c-b}{a-b}}{s+b}
$$

- 按**并联分解**取状态变量（两条支路的输出作为状态），得状态方程与输出方程：

$$
\dot x=\begin{bmatrix}-a&0\\0&-b\end{bmatrix}x+\begin{bmatrix}1\\1\end{bmatrix}u
$$

$$
y=\begin{bmatrix}\dfrac{c-a}{b-a}&\dfrac{c-b}{a-b}\end{bmatrix}x
$$

即 $A=\begin{bmatrix}-a&0\\0&-b\end{bmatrix}$（对角阵），$B=\begin{bmatrix}1\\1\end{bmatrix}$，$C=\begin{bmatrix}\dfrac{c-a}{b-a}&\dfrac{c-b}{a-b}\end{bmatrix}$，$D=0$。

**（2）状态转移矩阵**

- 因为 $A$ 已为对角阵，直接用拉氏变换法验证：

$$
sI-A=\begin{bmatrix}s+a&0\\0&s+b\end{bmatrix}
\ \Longrightarrow\ 
(sI-A)^{-1}
=
\begin{bmatrix}
\dfrac{1}{s+a}&0\\[8pt]
0&\dfrac{1}{s+b}
\end{bmatrix}
$$

- 逐项反变换（$L^{-1}\Big[\dfrac{1}{s+a}\Big]=e^{-at}$，$L^{-1}\Big[\dfrac{1}{s+b}\Big]=e^{-bt}$）：

$$
\boxed{\ \Phi(t)=L^{-1}\big[(sI-A)^{-1}\big]
=
\begin{bmatrix}
e^{-at}&0\\[2pt]
0&e^{-bt}
\end{bmatrix}\ }
$$

> **要点**：系统矩阵为对角阵（特征值 $\lambda_1=-a$，$\lambda_2=-b$）时，状态转移矩阵即为以 $e^{\lambda_i t}$ 为对角元的对角阵——这正是性质 10（一）的直接应用。

---

## 9.4.4 线性离散系统状态空间表达式的建立与求解

### 1. 离散时间线性系统的状态空间描述

**线性定常离散系统（time-invariant）**：

$$
x(k+1)=Ax(k)+Bu(k),\qquad y(k)=Cx(k)+Du(k)
$$

**线性时变离散系统（time-variant）**：

$$
x(k+1)=A(k)x(k)+B(k)u(k),\qquad y(k)=C(k)x(k)+D(k)u(k)
$$

其中各矩阵的维数与含义：

| 矩阵 | 维数 | 含义 |
|------|------|------|
| $A$ | $n\times n$ | 系统矩阵 |
| $B$ | $n\times p$ | 输入矩阵 |
| $C$ | $q\times n$ | 输出矩阵 |
| $D$ | $q\times p$ | 传递矩阵（直传矩阵） |

### 2. 线性定常 MIMO 离散系统的状态空间表达式与结构图

多输入多输出（MIMO）线性定常离散系统的结构图以**单位延迟算子 $z^{-1}$** 为核心环节：

```
u(k) ──→(+)──→ [ B ] ──→(+)──→ [ z^{-1} ] ──→ x(k) ──→ [ C ] ──→(+)──→ y(k)
            ↑                  ↑                              ↑
            └────── [ A ] ◄────┘                              └──── D ◄── u(k)
```

- 主通道：$u(k)$ 经 $B$ 加权后与 $Ax(k)$ 相加得到 $x(k+1)$；$x(k+1)$ 经单位延迟 $z^{-1}$ 变为 $x(k)$；
- 反馈支路：$A$ 将 $x(k)$ 反馈到加法器构成 $x(k+1)=Ax(k)+Bu(k)$；
- 前向（直传）支路：$Cx(k)$ 与 $Du(k)$ 相加得到输出 $y(k)=Cx(k)+Du(k)$。

### 3. 连续系统状态空间表达式的离散化（Discretization）

**问题**：对连续定常系统

$$
\dot x=Ax+Bu
$$

在采样周期 $T$ 下建立离散状态方程。

**求解要点（推导步骤）**：

1. **假设**：输入在采样间隔内保持为常数（相当于零阶保持器），即对 $t\in[kT,\,(k+1)T]$，$u(t)=u(kT)=u(k)$ 为常量；
2. 取连续方程解的 $t_0=kT$、$t=(k+1)T$ 形式：

$$
x\big((k+1)T\big)=\Phi(T)x(kT)
+\int_{kT}^{(k+1)T}\Phi\big((k+1)T-\tau\big)B\,u(\tau)\,d\tau
$$

3. 因 $u(\tau)=u(k)$ 为常数可提出积分号外：

$$
x\big((k+1)T\big)=\Phi(T)x(kT)
+\left[\int_{kT}^{(k+1)T}\Phi\big((k+1)T-\tau\big)B\,d\tau\right]u(k)
$$

4. **变量替换（Variable replacement）**：令 $\tau'=(k+1)T-\tau$（$d\tau'=-d\tau$），积分限相应变为 $\tau'=T\to 0$，故

$$
\int_{kT}^{(k+1)T}\Phi\big((k+1)T-\tau\big)B\,d\tau
=
\int_{0}^{T}\Phi(\tau)B\,d\tau
\ \triangleq\ G(T)
$$

5. 于是得到**离散系统状态方程**：

$$
\boxed{\ x(k+1)=\Phi(T)x(k)+G(T)u(k)\ }
$$

其中用简记 $x(k)=x(kT)$，且

$$
\boxed{\ \Phi(T)=\Phi(t)\big|_{t=T}=e^{AT}\ },\qquad
\boxed{\ G(T)=\int_{0}^{T}\Phi(\tau)B\,d\tau\ }
$$

- $\Phi(T)$ 与连续系统状态转移矩阵 $\Phi(t)=e^{At}$ 的关系：**把 $\Phi(t)$ 在 $t=T$ 处取值**，即 $\Phi(T)=\Phi(t)\big|_{t=T}$；
- **离散系统的输出方程**保持原连续形式：

$$
y(k)=Cx(k)+Du(k)
$$

> **注意**：离散化后系统矩阵变为 $\Phi(T)=e^{AT}$，输入矩阵变为 $G(T)=\int_0^{T}\Phi(\tau)B\,d\tau$；二者均与采样周期 $T$ 有关，$T$ 不同则离散模型不同。

---

### 例 9-17（Ex.9-17）——连续系统的离散化（$T=1$ s）

**题目**：取采样周期 $T=1$ s，由下列连续系统求其离散状态方程：

$$
\dot x=
\begin{bmatrix}0&1\\-2&-3\end{bmatrix}x
+
\begin{bmatrix}0\\1\end{bmatrix}u
$$

**求解要点**：

1. 由例 9-15 已知该系统状态转移矩阵

$$
\Phi(t)=e^{At}=
\begin{bmatrix}
2e^{-t}-e^{-2t} & e^{-t}-e^{-2t}\\[4pt]
-2e^{-t}+2e^{-2t} & -e^{-t}+2e^{-2t}
\end{bmatrix}
$$

2. 令 $t=T=1$（$e^{-1}\approx0.3679$，$e^{-2}\approx0.1353$）求 $\Phi(T)$：

$$
\Phi(1)=
\begin{bmatrix}
2e^{-1}-e^{-2} & e^{-1}-e^{-2}\\[4pt]
-2e^{-1}+2e^{-2} & -e^{-1}+2e^{-2}
\end{bmatrix}
=
\boxed{\begin{bmatrix}0.6004&0.2325\\-0.4651&-0.0972\end{bmatrix}}
$$

3. 求 $G(T)=\displaystyle\int_{0}^{T}\Phi(\tau)B\,d\tau$（$T=1$，取 $\Phi(\tau)$ 的第二列逐项积分）：

$$
G(1)=\int_{0}^{1}
\begin{bmatrix}
e^{-\tau}-e^{-2\tau}\\
-e^{-\tau}+2e^{-2\tau}
\end{bmatrix}d\tau
=
\begin{bmatrix}
\big(1-e^{-1}\big)-\tfrac12\big(1-e^{-2}\big)\\[4pt]
-\big(1-e^{-1}\big)+\big(1-e^{-2}\big)
\end{bmatrix}
=
\boxed{\begin{bmatrix}0.1998\\0.2325\end{bmatrix}}
$$

4. 因此 $T=1$ s 时系统的**离散状态方程**为

$$
\boxed{\ x(k+1)=
\begin{bmatrix}0.6004&0.2325\\-0.4651&-0.0972\end{bmatrix}x(k)
+
\begin{bmatrix}0.1998\\0.2325\end{bmatrix}u(k)\ }
$$

> **要点**：由连续模型离散化时，先算 $\Phi(t)=e^{At}$，再取 $t=T$ 得 $\Phi(T)$，最后对 $\Phi(\tau)B$ 在 $[0,T]$ 上积分得 $G(T)$——两步均为解析运算，代入数值即得离散模型。

---

## 知识点小结（考试要点）

1. **齐次状态方程的解**：$\dot x=Ax$ 的解为 $x(t)=e^{At}x(0)=\Phi(t)x(0)$（自由运动）；两种求法——幂级数法（比较同次幂系数得 $b_k=\dfrac1{k!}A^{k}b_0$，定义 $e^{At}=\sum_{k=0}^{\infty}\dfrac{A^{k}t^{k}}{k!}$）与拉氏变换法。
2. **状态转移矩阵的闭合形式**：$\Phi(t)=e^{At}=L^{-1}\big[(sI-A)^{-1}\big]$（收敛的解析形式），是计算 $e^{At}$ 的核心公式。
3. **非齐次状态方程的解**（直接法/积分法与拉氏变换法结果一致）：
$$
x(t)=e^{At}x(0)+\int_{0}^{t}e^{A(t-\tau)}Bu(\tau)\,d\tau
=\underbrace{\Phi(t-t_0)x(t_0)}_{\text{零输入响应}}+\underbrace{\int_{t_0}^{t}\Phi(t-\tau)Bu(\tau)\,d\tau}_{\text{零状态响应}}
$$
   自由运动、零输入响应与零状态响应三概念必须分清；解存在唯一性要求 $A$、$B$ 元素有界。
4. **状态转移矩阵十大性质**（9.4.2，考试常考推导与证明）：
   - $\Phi(0)=I$；$\dot\Phi=A\Phi=\Phi A$；$\Phi(t_1\pm t_2)=\Phi(t_1)\Phi(\pm t_2)=\Phi(\pm t_2)\Phi(t_1)$；
   - **$\Phi^{-1}(t)=\Phi(-t)$**（求逆直接用，如例 9-14）；
   - $x(t_2)=\Phi(t_2-t_1)x(t_1)$；分段性 $\Phi(t_2-t_0)=\Phi(t_2-t_1)\Phi(t_1-t_0)$；$[\Phi(t)]^{k}=\Phi(kt)$；
   - $e^{At}e^{Bt}=e^{(A+B)t}=e^{Bt}e^{At}$ **当且仅当 $AB=BA$**（交换条件，注意矩阵与标量的区别）；
   - 非奇异变换 $x=P\bar x$ 后 $\bar\Phi(t)=P^{-1}e^{At}P=e^{P^{-1}AP\,t}$；
   - $A$ 对角阵 $\Rightarrow\Phi=\mathrm{diag}(e^{\lambda_1 t},\cdots,e^{\lambda_n t})$；$A$ 为 $m$ 阶约当阵 $\Rightarrow\Phi=e^{Jt}=e^{\lambda t}\times$（含 $1,t,\dfrac{t^2}{2!},\cdots,\dfrac{t^{m-1}}{(m-1)!}$ 的上三角阵）。
5. **$e^{At}$ 的三种计算方法**：直接法（矩阵幂级数，收敛）、线性变换法（对角形 $e^{At}=Pe^{\Lambda t}P^{-1}$ 与约当形 $e^{At}=Se^{Jt}S^{-1}$）、拉氏变换法（$e^{At}=L^{-1}[(sI-A)^{-1}]$，高阶用递推算法）。例 9-13 说明两法结果一致。
6. **典型例题题型**：
   - 例 9-13：给定 $A$ 求 $e^{At}$（线性变换法与拉氏变换法对照）；
   - 例 9-14：拉氏法求 $\Phi(t)$，再用 $\Phi^{-1}(t)=\Phi(-t)$ 求逆；
   - 例 9-15：阶跃输入下解非齐次方程（关键积分 $\int_0^{t}e^{-\alpha(t-\tau)}d\tau=\dfrac{1-e^{-\alpha t}}{\alpha}$，零初态化简）；
   - 例 9-16：微分方程 $\Rightarrow$ 传递函数 $\Rightarrow$ 部分分式并联实现状态空间 $\Rightarrow$ 对角阵 $\Phi(t)=\mathrm{diag}(e^{-at},e^{-bt})$；
   - 例 9-17：离散化数值计算（$T=1$ s）。
7. **离散系统状态空间表达式**：定常 $x(k+1)=Ax(k)+Bu(k)$ 与 时变 $A(k),B(k),C(k),D(k)$ 两套形式；矩阵维数 $A_{n\times n}$、$B_{n\times p}$、$C_{q\times n}$、$D_{q\times p}$；MIMO 结构图以 $z^{-1}$ 为单位延迟环节。
8. **连续系统离散化（重点公式）**：$x(k+1)=\Phi(T)x(k)+G(T)u(k)$，其中 $\Phi(T)=\Phi(t)\big|_{t=T}=e^{AT}$，$G(T)=\int_{0}^{T}\Phi(\tau)B\,d\tau$（输入在采样间隔内保持常数）；输出方程 $y(k)=Cx(k)+Du(k)$ 不变；$\Phi(T)$、$G(T)$ 均与采样周期 $T$ 有关。
