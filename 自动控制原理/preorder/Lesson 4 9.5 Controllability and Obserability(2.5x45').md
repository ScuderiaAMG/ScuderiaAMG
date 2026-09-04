# 自动控制原理II —— 9.5 线性时不变系统的能控性与能观性（Controllability and Observability，知识点总结）

> **来源课件**：Lesson 4 9.5 Controllability and Obserability(2.5x45').txt（对应PPT课件共72页）
> **课程信息**：自动控制原理II，本讲主题为 9.5 线性时不变系统的能控性与能观性（Linear time-invariant system 的 Controllability and Observability，时长 2.5×45′）
> **整理说明**：课件文字提取后公式元素顺序被打乱，本总结依据自动控制原理（现代控制理论：能控性与能观性）专业知识将公式复原为标准写法，内容（例题编号、数值、结论）忠实于课件；个别矩阵元素若因提取乱序与课件原稿有出入，以课件原稿为准。

## 本节内容总览

- 背景知识（能控性与能观性问题的提出）
- 线性连续系统能控性与能观性的概念
- 线性连续系统能控性与能观性的判据
- 对偶原理（Duality Principle）
- 传递函数描述下的能控/能观条件（零极点对消）
- 线性时不变离散系统的能控性与能观性
- 连续线性时不变系统的结构分解（能控分解、能观分解、卡尔曼标准分解）

---

## 一、背景知识（Background knowledge）

**提出背景**：20 世纪 60 年代，**Kalman** 从状态空间描述出发提出了能控性与能观性问题。在现代控制理论中，需要考虑：在系统的状态方程与输出方程描述下，**输入是否影响全部状态、输出是否反映全部状态**。

- **能控性（Controllability）**：系统的输入能够影响系统的所有状态，从而实现对系统的控制（system input affects all the states to achieve the control）。
- **能观性（Observability）**：系统的输出能够反映系统的所有状态，从而实现对系统的观测（system output can reflect all the states to achieve the observation）。
- 能控性与能观性只对**状态空间（SS）描述**有意义，传递函数（TF）表示不讨论此问题（For SS only, rather than TF representation）。

### 引例 1：例9-19（状态方程系统）

> **例9-19**：已知系统状态方程（二阶），分析其能控性与能观性。

将状态方程展开为微分方程组后可见：

- 由输入 $u(t)$ 的作用，状态变量 $x_1$、$x_2$ 均可由初始值转移到零 → **两个状态均能控**；
- 输出 $y$ 只能反映状态 $x_2$，与 $x_1$ 没有联系（输出方程中不含 $x_1$）→ **系统不完全能观**（incomplete observable）。

> 结论要点：输入—状态的关系决定能控性；输出—状态的关系决定能观性。二者是互相独立的概念。

### 引例 2：例9-20(a)——电桥电路（定性分析）

> **例9-20(a)**：桥式电路（bridge circuit）中，选择状态变量为电感电流 $i_L$ 与电容电压 $u_c$，输入为 $u$，输出为 $y = u_c$。即
> $$
> x_1 = i_L,\qquad x_2 = u_c,\qquad y = u_c
> $$

分析（当电桥平衡等条件使 $x_2$ 不受输入驱动时）：

- 若 $x_2(t_0)=0$ 且 $x_2(t)\equiv 0\ (t\ge t_0)$，则输入 $u$ 不能控制状态 $x_2$ → **$x_2$ 不可控（uncontrollable）**；
- 又因 $y = u_c \equiv 0$，输出无法反映 $x_1$（即 $i_L$）的变化 → **$x_1$ 不可观（unobservable）**。

（该例的完整定量求解——列写电路方程、求能控性矩阵——见后文"例9-20(a) 的求解"。）

### 引例 3：例9-20(b) 与例9-21(a)

- **例9-20(b)**（电路图见课件 P5）：分析两种 RC 网络的能控性与能观性，详细求解见后文。
- **例9-21(a)**（信号流图见课件 P6）：分析图示信号流图系统的能控性与能观性。

---

## 二、9.5.1 线性时不变连续系统的能控性

### 1. 能控性的定义

考虑状态方程
$$
\dot{x}(t) = A(t)x(t) + B(t)u(t),\qquad x(t)\in\mathbb{R}^{n},\ u(t)\in\mathbb{R}^{r},\ A(t)\in\mathbb{R}^{n\times n},\ B(t)\in\mathbb{R}^{n\times r},\ t\in T
$$

**（1）状态能控性（State Controllability）**：若对初始时刻 $t_0\in T$ 上的某个非零初始状态 $x(t_0)=x_0$，存在某一时刻 $t_1\in T$、$t_1>t_0$ 及一个不受约束的控制 $u(t)$，能使状态由 $x(t_0)=x_0$ 转移到 $x(t_1)=0$，则称状态 $x_0$ 在 $t_0$ 时刻是**能控的**。

**（2）系统能控性（System Controllability）**：若在 $t_0\in T$ 时刻，状态空间中全部非零初始状态都能控，则称系统在 $t_0$ 时刻**能控**。

**（3）不完全能控（Incomplete Controllable）**：若状态空间中有一个或一些非零状态变量不可控，则称系统**不完全能控**。

**重要性质**：线性**时不变**系统的能控性与初始时刻 $t_0$ 无关（The controllability of linear time-invariable system has no relation to the initial time $t_0$）。

### 2. 凯莱—哈密顿定理（Cayley–Hamilton Theorem）及其推论

**定理**：设 $n\times n$ 矩阵 $A$ 的特征多项式为
$$
f(\lambda) = \det(\lambda I - A) = \lambda^{n} + a_{n-1}\lambda^{n-1} + \cdots + a_1\lambda + a_0
$$
则矩阵 $A$ 也满足它自己的特征多项式：
$$
f(A) = A^{n} + a_{n-1}A^{n-1} + \cdots + a_1 A + a_0 I = 0
$$

**证明思路**（重点理解）：记伴随矩阵 $(\lambda I-A)\cdot\mathrm{adj}(\lambda I-A) = \det(\lambda I-A)I = f(\lambda)I$。伴随矩阵 $\mathrm{adj}(\lambda I-A)$ 的元素均为 $\lambda$ 的多项式，故可将伴随矩阵分解为 $n$ 个矩阵之和：
$$
\mathrm{adj}(\lambda I-A) = B_{n-1}\lambda^{n-1} + B_{n-2}\lambda^{n-2} + \cdots + B_1\lambda + B_0
$$
其中 $B_{n-1},\dots,B_0$ 为 $n$ 阶常数矩阵。代入后比较方程两端 $\lambda$ 的同次幂系数，得递推式
$$
B_{n-1}=I,\quad B_{n-2}=B_{n-1}A + a_{n-1}I,\ \dots\ ,\quad B_0 = B_1 A + a_1 I,\quad B_0 A + a_0 I = 0
$$
分别右乘 $A^{n-1}, A^{n-2}, \dots, A, I$，并将各式相加，左端逐项相消，即得 $f(A)=A^n + a_{n-1}A^{n-1}+\cdots+a_1 A + a_0 I = 0$。

**推论1**：矩阵 $A$ 的 $k$ 次幂（$k>n$）可用 $A$ 的 $(n-1)$ 次多项式表示：
$$
A^{k} = \sum_{m=0}^{n-1} \alpha_m A^{m},\qquad k \ge n
$$

**推论2**：矩阵指数 $e^{At}$ 可用 $A$ 的 $(n-1)$ 次多项式表示：
$$
e^{At} = \sum_{m=0}^{n-1} \alpha_m(t)\, A^{m}
$$
（这是后面推导能控性、能观性代数判据的核心工具。）

### 3. 状态能控性的代数判据（时不变系统）

**推导过程**：设终态为状态空间原点、初始时刻 $t_0=0$。状态方程的解为
$$
x(t_1) = e^{At_1}x(0) + \int_{0}^{t_1} e^{A(t_1-\tau)}Bu(\tau)\,d\tau = 0
$$
即
$$
x(0) = -\int_{0}^{t_1} e^{-A\tau}Bu(\tau)\,d\tau
$$
由推论2，将 $e^{-A\tau}$ 展开为 $A$ 的多项式：
$$
e^{-A\tau} = \sum_{k=0}^{n-1}\alpha_k(\tau)A^{k}
$$
代入得
$$
x(0) = -\sum_{k=0}^{n-1} A^{k}B\int_{0}^{t_1}\alpha_k(\tau)u(\tau)\,d\tau
= -\sum_{k=0}^{n-1} A^{k}B\,\beta_k
= -[\,B\ \ AB\ \ \cdots\ \ A^{n-1}B\,]
\begin{bmatrix}\beta_0\\ \beta_1\\ \vdots\\ \beta_{n-1}\end{bmatrix}
$$
其中 $\beta_k = \displaystyle\int_{0}^{t_1}\alpha_k(\tau)u(\tau)\,d\tau$ 为标量（单输入情形）。若系统能控，则上述关于任意初始状态 $x(0)$ 的方程应有唯一解，等价于 $n\times n$ 矩阵
$$
Q = [\,B\ \ AB\ \ \cdots\ \ A^{n-1}B\,]
$$
满足 $\mathrm{rank}(Q)=n$。此时可由 $\beta_k$ 反解出对应的控制输入 $u(t)$，使系统在有限时间区间 $(0,t_1)$ 内由任意初始状态 $x(0)$ 转移到原点。

> **状态能控性的代数判据（充要条件）**：
> $$
> \mathrm{rank}\,Q = \mathrm{rank}[\,B\ \ AB\ \ \cdots\ \ A^{n-1}B\,] = n
> $$
> 即 $n\times n$（或多输入情形 $n\times nr$）能控性矩阵 $Q$ **满秩** ⟺ 系统能控。

**多输入推广（Extensive result）**：对于 $r$ 维控制向量 $u$，状态方程为 $\dot{x}=Ax+Bu$，$x\in\mathbb{R}^n$，$u\in\mathbb{R}^r$，$A\in\mathbb{R}^{n\times n}$，$B\in\mathbb{R}^{n\times r}$，能控条件为 $n\times nr$ 能控性矩阵
$$
Q = [\,B\ \ AB\ \ \cdots\ \ A^{n-1}B\,]
$$
满足 $\mathrm{rank}(Q)=n$，等价于 $Q$ 中有 $n$ 个列向量线性无关。

**能控性矩阵（Controllability Matrix）**：$Q = [\,B\ \ AB\ \ \cdots\ \ A^{n-1}B\,]$。

### 例9-22：判断下列两系统的能控性

**系统1**（二阶）：构造能控性矩阵 $Q=[B\ \ AB]$，计算得
$$
\det Q = \det[B\ \ AB] = 0
$$
$Q$ 为奇异矩阵 → **系统不可控（uncontrollable）**。

**系统2**（三阶）：构造能控性矩阵 $Q = [B\ \ AB\ \ A^{2}B]$（3×3），经计算矩阵的第 2 行与第 3 行线性相关：
$$
\mathrm{rank}\,Q = 2 < 3 = n
$$
→ **系统不可控**。

### 例9-20(a) 的求解（桥式电路的能控性定量分析，对应课件 P19–P20）

电路方程：设 $x_1 = i_L$（电感电流）、$x_2 = u_c$（电容电压）。由电路列写动态微分方程（含电流 $i_1\sim i_4$ 的回路/节点方程），**消去中间变量 $i_1,i_2,i_3,i_4$**，得状态方程（系数为 $R_1\sim R_4$、$L$、$C$ 的组合）：
$$
\dot{x}_1 = \frac{\cdots}{L(\cdots)}x_1 + \frac{\cdots}{L(\cdots)}x_2 + \frac{\cdots}{L(\cdots)}u,\qquad
\dot{x}_2 = \frac{\cdots}{C(\cdots)}x_1 + \frac{\cdots}{C(\cdots)}x_2 + \frac{\cdots}{C(\cdots)}u
$$

- 构造能控性矩阵 $S=[b\ \ Ab]$（即 $Q_c$）。一般情形（不平衡条件成立）下：$\mathrm{rank}\,S = 2 = n$ → **系统能控**；
- 当电路参数满足使某些系数组合为零（电桥平衡）的条件时，状态方程退化，$\mathrm{rank}\,S < n$ → **系统不能控**（对应引例中"$x_2$ 不可控"的结论）；课件同时结合输出 $y=u_c$ 指出此时系统也不完全能观（$x_1=i_L$ 不可观）。

### 例9-20(b) 的求解（两种 RC 网络的能控性）

**电路 (a)**：两个独立的一阶 RC 支路（同一电源 $u$ 分别经 $R_1$、$R_2$ 向 $C_1$、$C_2$ 充电），状态变量取 $x_1 = u_{c1} = \dfrac{1}{C_1}\displaystyle\int i_1\,dt$，$x_2 = u_{c2} = \dfrac{1}{C_2}\displaystyle\int i_2\,dt$，其状态方程为
$$
\dot{x}_1 = -\frac{1}{R_1C_1}x_1 + \frac{1}{R_1C_1}u,\qquad
\dot{x}_2 = -\frac{1}{R_2C_2}x_2 + \frac{1}{R_2C_2}u
$$

- 若 $R_1C_1 \ne R_2C_2$：$\mathrm{rank}[b\ \ Ab]=2=n$ → **系统能控**；
- 若 $R_1=R_2$、$C_1=C_2$（从而 $R_1C_1=R_2C_2$）：$\mathrm{rank}[b\ \ Ab]=1<n$ → **系统不能控**。

**电路 (b)**：两电容 $C_1$、$C_2$ 所在节点间经电阻 $R_3$ 耦合（电路中共涉及电流 $i_1\sim i_4$），消去中间变量后其状态方程为（形如）
$$
\dot{x}_1 = -\Big(\frac{1}{R_1C_1}+\frac{1}{R_3C_1}\Big)x_1 + \frac{1}{R_3C_1}x_2 + \frac{1}{R_1C_1}u
$$
$$
\dot{x}_2 = \frac{1}{R_3C_2}x_1 - \Big(\frac{1}{R_2C_2}+\frac{1}{R_3C_2}\Big)x_2 + \frac{1}{R_2C_2}u
$$

- 若 $R_1\ne R_2$ 且 $C_1\ne C_2$：$\mathrm{rank}[b\ \ Ab]=2=n$ → **系统能控**；
- 若 $R_1=R_2$、$C_1=C_2$：$\mathrm{rank}[b\ \ Ab]=1<n$ → **系统不能控**（此时"差模"状态 $x_1-x_2$ 不受输入激励，仅能自由衰减）。

> 电路类例题的共同思想：列出微分方程 → 选状态变量 → 消中间变量 → 构造 $[b\ \ Ab]$ → 用秩/行列式判断。参数对称（时间常数相等）往往导致某一模态不可控。

### 4. 输出能控性（Output Controllability）

考虑线性时不变系统的状态空间描述
$$
\dot{x} = Ax + Bu,\qquad y = Cx + Du
$$
其中 $x\in\mathbb{R}^n$，$u\in\mathbb{R}^r$，$y\in\mathbb{R}^m$，$A\in\mathbb{R}^{n\times n}$，$B\in\mathbb{R}^{n\times r}$，$C\in\mathbb{R}^{m\times n}$，$D\in\mathbb{R}^{m\times r}$。

**定义**：若存在不受约束的控制 $u(t)$，能在有限时间区间 $t_0\le t\le t_1$ 内使任意初始输出 $y(t_0)$ 转移到任意最终输出 $y(t_1)$，则称系统**输出能控**。

**输出能控的充要条件**：$m\times(n+1)r$ 维**输出能控性矩阵**
$$
Q' = [\,CB\ \ \ CAB\ \ \ \cdots\ \ \ CA^{n-1}B\ \ \ D\,]
$$
满足 $\mathrm{rank}(Q')=m$。

> 注意：输出能控性矩阵中多出直接传递矩阵 $D$ 一项；其秩条件针对输出维数 $m$，而非状态维数 $n$。

---

## 三、9.5.2 线性连续系统的能观性

**动机**：实际工程中，系统的状态 $x(t)$ 往往不能全部测量、甚至完全无法测量。一种可行的途径是通过输出 $y(t)$ 来反映（重构）状态 $x(t)$——这正是系统的**能观性**。

### 1. 能观性的定义

考虑零输入系统
$$
\dot{x}=Ax,\qquad y=Cx
$$

**完全能观（Completely Observable）**：对初始时刻 $t_0\in T$，存在有限时刻 $t_1\in T$、$t_1>t_0$，对一切 $t\in[t_0,t_1]$，系统的初始状态 $x(t_0)$ 可由输出 $y(t)$ **唯一确定**，则称系统在 $[t_0,t_1]$ 上**完全能观**。若在 $t>t_0$ 的整个时间域 $[t_0,\infty)$ 上系统能观，则称系统在 $t_0$ 以后能观。

**不完全能观（Incompletely Observable / Unobservable）**：若在 $[t_0,t_1]$ 上，全部初始状态 $x_i(t_0)\ (i=1,2,\dots,n)$ 中至少有一个状态不能由 $y(t)$ 完全确定，则称系统在 $[t_0,t_1]$ 上**不完全能观（不可观）**。

### 2. 状态能观性的代数判据（时不变系统）

考虑一般系统
$$
\dot{x}=Ax+Bu,\qquad y=Cx+Du
$$
其响应为
$$
x(t) = e^{At}x(0) + \int_0^t e^{A(t-\tau)}Bu(\tau)\,d\tau,\qquad
y(t) = Ce^{At}x(0) + C\int_0^t e^{A(t-\tau)}Bu(\tau)\,d\tau + Du(t)
$$
由于 $A,B,C,D$ 与输入 $u(t)$ 均已知，上式右端含输入的部分已知，可从量测值 $y(t)$ 中扣除。故讨论能观性充要条件时只需考虑**零输入系统**。

对零输入系统 $y(t) = Ce^{At}x(0)$，由凯莱—哈密顿定理推论 2 将 $e^{At}$ 写成 $A$ 的 $(n-1)$ 次多项式：
$$
e^{At} = \sum_{k=0}^{n-1}\alpha_k(t)A^{k}\ \Longrightarrow\ 
y(t) = \sum_{k=0}^{n-1}\alpha_k(t)\,CA^{k}x(0)
$$
若系统能观，则在 $t_0\le t\le t_1$ 内给定输出 $y(t)$，可由上式**唯一确定** $x(0)$；这等价于要求 $x(0)$ 的系数矩阵各列线性无关，即
$$
\begin{bmatrix}C\\ CA\\ \vdots\\ CA^{n-1}\end{bmatrix} x(0) \ \text{可由} \ y(t)\ \text{唯一解出}
$$

**状态能观性的代数判据（充要条件）**：$nm\times n$ 维**能观性矩阵**
$$
R = \begin{bmatrix}C\\ CA\\ \vdots\\ CA^{n-1}\end{bmatrix}
\qquad\text{（或其转置}\ R^{T}=[\,C^{T}\ \ A^{T}C^{T}\ \ \cdots\ \ (A^{T})^{n-1}C^{T}\,]\text{）}
$$
满足
$$
\mathrm{rank}\,R = n \qquad \text{（即 } \mathrm{rank}\,R^{T}=n\text{）}
$$
⟺ 系统能观。单输出情形下常写成 $R = [C^T\ \ A^TC^T]^T$（即 $\begin{bmatrix}C\\ CA\end{bmatrix}$）等具体形式。

### 例9-23：判断下列系统的能控性与能观性

系统为
$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\end{bmatrix}
=
\begin{bmatrix}1 & 1\\ 2 & -1\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\end{bmatrix}
+
\begin{bmatrix}0\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}1 & 0\end{bmatrix}\begin{bmatrix}x_1\\ x_2\end{bmatrix}
$$

**解**：

- **状态能控性矩阵**：$Q = [B\ \ AB]=\begin{bmatrix}0 & 1\\ 1 & -1\end{bmatrix}$，$\mathrm{rank}\,Q = 2 = n$ → **状态完全能控**。
- **输出能控性矩阵**：$Q' = [CB\ \ CAB]$：$CB = 0$，$CA=[1\ \ 1]$，$CAB = 1$，故 $Q'=[0\ \ 1]$，$\mathrm{rank}\,Q'=1=m$ → **输出完全能控**。
- **能观性矩阵**：$R = \begin{bmatrix}C\\ CA\end{bmatrix}=\begin{bmatrix}1 & 0\\ 1 & 1\end{bmatrix}$，$\mathrm{rank}\,R=2=n$ → **系统能观**。

---

## 四、传递函数描述下的能控性与能观性条件

**核心结论**：能控性能观性也可以用传递函数描述。系统**状态能控且能观**的充要条件是**传递函数中没有可约因子（零极点对消，No Cancellation）**：
$$
G(s) = C(sI-A)^{-1}B = \frac{k(s-z_1)(s-z_2)\cdots(s-z_i)}{(s-p_1)(s-p_2)\cdots(s-p_j)},\qquad z_i \ne p_j
$$
若传递函数出现对消，则系统**不可控或不可观，甚至同时不可控且不可观**。也就是说：**可约的传递函数没有足够的信息完整描述该动态系统**。

### 例9-24：考察传递函数

$$
\frac{Y(s)}{U(s)} = \frac{s+2.5}{(s+2.5)(s-1)}
$$

分子、分母含有可约因子 $(s+2.5)$，故系统状态**不可控或不可观**。将传递函数化为状态方程（一组状态变量的选取下）：

**实现1**（能控标准型——可控但不可观）：
$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\end{bmatrix}
=
\begin{bmatrix}0 & 1\\ 2.5 & -1.5\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\end{bmatrix}
+
\begin{bmatrix}0\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}2.5 & 1\end{bmatrix}x
$$
其能观性矩阵
$$
\begin{bmatrix}C\\ CA\end{bmatrix} = \begin{bmatrix}2.5 & 1\\ 2.5 & 1\end{bmatrix}
$$
两行相同，$\mathrm{rank}\begin{bmatrix}C\\ CA\end{bmatrix}=1<2$ → **状态不可观**。

**实现2**（能观标准型——可观但不可控）：换一组状态变量得另一状态空间
$$
\dot{x} = \begin{bmatrix}0 & 2.5\\ 1 & -1.5\end{bmatrix}x + \begin{bmatrix}2.5\\ 1\end{bmatrix}u,\qquad y = \begin{bmatrix}0 & 1\end{bmatrix}x
$$
其能控性矩阵 $[B\ \ AB]$ 中 $B$ 与 $AB$ 成比例：$\mathrm{rank}[B\ \ AB]=1<2$ → **状态不可控**。

> **结论**：若传递函数出现可约因子（零极点对消），则**选取不同的状态变量建立状态空间时，将分别表现出不可控或不可观**。

### 例9-25：分析下列系统的能观性

$$
\dot{x} = Ax + Bu,\qquad y = Cx
$$
其中
$$
A = \begin{bmatrix}0 & 1 & 0\\ 0 & 0 & 1\\ -6 & -11 & -6\end{bmatrix},\qquad
B = \begin{bmatrix}0\\ 0\\ 1\end{bmatrix},\qquad
C = \begin{bmatrix}4 & 5 & 1\end{bmatrix}
$$

**解**：能观性矩阵为
$$
R = \begin{bmatrix}C\\ CA\\ CA^{2}\end{bmatrix}
= \begin{bmatrix}4 & 5 & 1\\ -6 & -7 & -1\\ 6 & 5 & -1\end{bmatrix}
$$
计算得 $\det R = 0$（$\mathrm{rank}\,R = 2 < 3$）→ **系统不可观**。

传递函数验证：分别考察中间环节 $X_1(s)$ 的传递函数
$$
\frac{X_1(s)}{U(s)} = \frac{1}{(s+1)(s+2)(s+3)},\qquad
\frac{Y(s)}{X_1(s)} = (s+1)(s+4)
$$
于是
$$
\frac{Y(s)}{U(s)} = \frac{(s+1)(s+4)}{(s+1)(s+2)(s+3)}
$$
注意其中存在**可约因子（可约因子）$(s+1)$** → 系统不可观，即某些非零初始状态 $x(0)$ 不能被 $y(t)$ 量测到。

> 结论重申：系统能控**且**能观 ⟺ 其传递函数无可约因子；可约的传递函数不具有描述动态系统的完整信息。

---

## 五、9.5.3 对偶原理（Duality Principle）——R.E. Kalman

**目的**：揭示能控性与能观性之间的关系。考虑系统 $S_1$ 与 $S_2$：

**系统 $S_1$**：
$$
\dot{x} = Ax + Bu,\qquad y = Cx
$$
其中 $x\in\mathbb{R}^n$，$u\in\mathbb{R}^r$，$y\in\mathbb{R}^m$，$A\in\mathbb{R}^{n\times n}$，$B\in\mathbb{R}^{n\times r}$，$C\in\mathbb{R}^{m\times n}$。

**系统 $S_2$（$S_1$ 的对偶系统，Dually System）**：
$$
\dot{z} = A^{T}z + C^{T}v,\qquad \eta = B^{T}z
$$
其中 $z\in\mathbb{R}^n$，$v\in\mathbb{R}^m$，$\eta\in\mathbb{R}^r$，$A^T\in\mathbb{R}^{n\times n}$，$C^T\in\mathbb{R}^{n\times m}$，$B^T\in\mathbb{R}^{r\times n}$。

**对偶原理**：系统 $S_1$ 状态**能观/能控** ⟺ 系统 $S_2$ 状态**能控/能观**。即二者能控性与能观性互换：$(A,B,C)\ \longleftrightarrow\ (A^{T},C^{T},B^{T})$。

**对偶原理的证明思路**：$S_1$ 状态能控 ⟺ $\mathrm{rank}[B\ \ AB\ \ \cdots\ \ A^{n-1}B] = n$（$n\times nr$ 能控性矩阵）；$S_1$ 状态能观 ⟺ 能观性矩阵 $R^T = [C^T\ \ A^TC^T\ \ \cdots\ \ (A^T)^{n-1}C^T]$ 的秩为 $n$。可见 $S_1$ 的能观性矩阵恰是 $S_2$ 的能控性矩阵，反之亦然。

> **应用**：由对偶原理，一个系统的能观性可以通过**其对偶系统的状态能控性**来判断，反之亦然。

---

## 六、9.5.4 线性连续系统能控性与能观性的判据汇总

### （一）能控性判据（Controllability Criterion）

**判据 1（代数判据）**：线性时不变连续系统 $\dot{x}=Ax+Bu$（$x\in\mathbb{R}^n$，$u\in\mathbb{R}^r$）**状态完全能控**的充要条件是能控性矩阵
$$
Q_c = [\,B\ \ \ AB\ \ \ A^{2}B\ \ \ \cdots\ \ \ A^{n-1}B\,]
$$
满秩，即 $\mathrm{rank}\,Q_c = n$。

**能控标准型（Controllable Canonical Form）**：
$$
A = \begin{bmatrix}
0 & 1 & 0 & \cdots & 0\\
0 & 0 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \ddots & \vdots\\
0 & 0 & 0 & \cdots & 1\\
-a_0 & -a_1 & -a_2 & \cdots & -a_{n-1}
\end{bmatrix},
\qquad
B = \begin{bmatrix}0\\ 0\\ \vdots\\ 0\\ 1\end{bmatrix}
$$

**例9-26**：对系统（二阶，矩阵同前式结构），构造能控性矩阵
$$
Q_c = [B\ \ AB] = \begin{bmatrix}0 & 1\\ 1 & -1\end{bmatrix}
$$
$\det Q_c \ne 0$，$\mathrm{rank}\,Q_c = 2 = n$ → **系统能控**。

**例9-27**：分析下列**3 阶 2 输入**系统的能控性（系统状态方程与 $Q_c=[B\ \ AB\ \ A^2B]$ 见课件）。经计算，能控性矩阵 $Q_c$（3×6）的秩不足 3（存在线性相关的行/列）→ **系统不可控**。

> 注：$Q_c$ 的秩只需算到 $n$ 即可判定；多输入时 $Q_c$ 为 $n\times nr$ 阵，存在 $n$ 个线性无关列即满秩。

**判据 2（对角标准型判据）**：若线性时不变系统具有**互异特征值**，则系统能控的充要条件是：经非奇异变换得到的**对角标准型**中，**输入矩阵 $\bar{B}$ 没有全零行**：
$$
\dot{x} = \begin{bmatrix}\lambda_1 & & & 0\\ & \lambda_2 & &\\ & & \ddots &\\ 0 & & & \lambda_n\end{bmatrix}x + \bar{B}u
$$

**例9-28**：判断下列对角标准型系统的能控性（特征值 $\lambda = -7,-5,-1$ 互异）：

| 情形 | 输入矩阵 $\bar{B}$ | 判定 |
|------|--------------------|------|
| (1) | $\bar{B} = \begin{bmatrix}2\\ 5\\ 7\end{bmatrix}$ | 无全零行 → **能控**（√） |
| (2) | $\bar{B} = \begin{bmatrix}0\\ 5\\ 7\end{bmatrix}$ | 第 1 行为全零行 → **不能控**（×） |
| (3) | $\bar{B} = \begin{bmatrix}0 & 1\\ 4 & 0\\ 5 & 7\end{bmatrix}$（双输入） | 各行均非全零 → **能控**（√） |
| (4) | $\bar{B} = \begin{bmatrix}0 & 0\\ 4 & 0\\ 5 & 7\end{bmatrix}$（双输入） | 第 1 行为全零行 → **不能控**（×） |

**判据 3（约当标准型判据）**：对约当标准型
$$
\dot{x} = \begin{bmatrix}J_1 & & 0\\ & \ddots &\\ 0 & & J_k\end{bmatrix}x + \bar{B}u
$$
系统能控的充要条件是：与**每个约当块 $J_i$（$i=1,2,\dots,k$）的最后一行**相对应的 $\bar{B}$ 中的那些行的元素**不全为零**。

> 注意：若存在两个约当块具有**相同的特征值**，则该简单结论不成立（需合并处理后另行判断）。

**例9-29**：分析下列约当标准型系统的能控性（系统（1）、（2）的约当形均为 $\lambda=-4$ 的二阶约当块加 $\lambda=-3$ 的一阶块）：
$$
\dot{x} = \begin{bmatrix}-4 & 1 & 0\\ 0 & -4 & 0\\ 0 & 0 & -3\end{bmatrix}x + \bar{B}u
$$

- **系统(1)**：单输入，$\bar{B}$ 中与 $\lambda=-4$ 约当块末行（第 2 行）及 $\lambda=-3$ 块末行（第 3 行）对应的元素均不为零 → **能控**（√）；
- **系统(2)**：双输入，$\bar{B}$ 中与某约当块末行对应的行（如第 2 行）出现全零 → **不能控**（×）。

### （二）能观性判据（Observability Criterion）

**判据 1（代数判据）**：线性时不变连续系统状态**完全能观**的充要条件是能观性矩阵
$$
Q_o = \begin{bmatrix}C\\ CA\\ \vdots\\ CA^{n-1}\end{bmatrix}
\qquad \left(\text{即}\ Q_o^T = [\,C^T\ \ \ (CA)^T\ \ \ \cdots\ \ \ (CA^{n-1})^T\,]\right)
$$
满秩，即 $\mathrm{rank}\,Q_o = n$。

**能观标准型（Observable Canonical Form）**：
$$
A = \begin{bmatrix}
0 & 0 & \cdots & 0 & -a_0\\
1 & 0 & \cdots & 0 & -a_1\\
0 & 1 & \cdots & 0 & -a_2\\
\vdots & \vdots & \ddots & \vdots & \vdots\\
0 & 0 & \cdots & 1 & -a_{n-1}
\end{bmatrix},
\qquad
C = \begin{bmatrix}0 & 0 & \cdots & 0 & 1\end{bmatrix}
$$

**例9-30**：由给定的 $A$ 与 $C$ 分析系统的能观性（课件给出系统矩阵与输出矩阵，按能观性矩阵秩判定为**能观**）。

**例9-31**：判断下列系统的能观性。已知
$$
A = \begin{bmatrix}-4 & 5\\ 1 & 0\end{bmatrix},\qquad C = \begin{bmatrix}1 & -1\end{bmatrix}
$$

**解**：先求 $CA$：
$$
CA = \begin{bmatrix}1 & -1\end{bmatrix}\begin{bmatrix}-4 & 5\\ 1 & 0\end{bmatrix} = \begin{bmatrix}-5 & 5\end{bmatrix}
$$
能观性矩阵
$$
Q_o = \begin{bmatrix}C\\ CA\end{bmatrix} = \begin{bmatrix}1 & -1\\ -5 & 5\end{bmatrix}
$$
两行成比例（第 2 行 $= -5\times$ 第 1 行），$\mathrm{rank}\,Q_o = 1 < 2 = n$ → **系统不可观**。

**判据 2（对角标准型判据）**：若线性时不变连续系统具有**互异特征值**，则系统能观的充要条件是：对角标准型中**输出矩阵 $\bar{C}$ 没有全零列**：
$$
\dot{x} = \begin{bmatrix}\lambda_1 & & 0\\ & \ddots &\\ 0 & & \lambda_n\end{bmatrix}x,\qquad y = \bar{C}x
$$

**例9-32**：判断系统的能观性。系统为对角标准型：
$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\end{bmatrix}
= \begin{bmatrix}-7 & 0 & 0\\ 0 & -5 & 0\\ 0 & 0 & -1\end{bmatrix}\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix},\qquad
y_1 = 2x_1,\quad y_2 = 3x_2 + x_3
$$
即输出矩阵 $\bar{C}=\begin{bmatrix}2 & 0 & 0\\ 0 & 3 & 1\end{bmatrix}$，各列均非全零 → **系统能观**（√）。

**判据 3（约当标准型判据）**：在约当标准型
$$
\dot{x} = \begin{bmatrix}J_1 & & 0\\ & \ddots &\\ 0 & & J_k\end{bmatrix}x,\qquad y = \bar{C}x
$$
下，系统能观的充要条件是：与**每个约当块 $J_i$（$i=1,2,\dots,k$）的第一行**相对应的 $\bar{C}$ 中的那些**列**的元素**不全为零**。

> 注意：若存在两个约当块具有**相同的特征值**，则该简单结论不成立。

**例9-33**：判断下列约当标准型系统的能观性。

**系统(1)**（$\lambda=2$ 的三阶约当块与 $\lambda=3$ 的一阶块，双输出）：
$$
\dot{x} = \begin{bmatrix}
2 & 1 & 0 & 0\\
0 & 2 & 1 & 0\\
0 & 0 & 2 & 0\\
0 & 0 & 0 & 3
\end{bmatrix}x,\qquad
y_1 = x_1 + x_2,\quad y_2 = x_2 + x_4
$$
输出矩阵各列中，与 $\lambda=2$ 约当块首行对应的第 1 列 $\begin{bmatrix}1\\ 0\end{bmatrix}$、与 $\lambda=3$ 块（首行为第 4 行）对应的第 4 列 $\begin{bmatrix}0\\ 1\end{bmatrix}$ 均非全零 → **完全能观**（√）。

**系统(2)**（$\lambda=1$ 的一阶块与 $\lambda=2$ 的二阶约当块，单输出）：
$$
\dot{x} = \begin{bmatrix}1 & 0 & 0\\ 0 & 2 & 1\\ 0 & 0 & 2\end{bmatrix}x,\qquad y = \bar{C}x
$$
其输出矩阵 $\bar{C}$ 中与 $\lambda=1$ 约当块首行（第 1 行）对应的列（或相应首行列）出现全零，无法由 $y$ 确定相应状态 → **不完全能观**（×）。

---

## 七、9.5.5 线性时不变离散系统的能控性与能观性

离散系统状态方程：
$$
x(k+1) = Ax(k) + Bu(k),\qquad y(k) = Cx(k) + Du(k)
$$
其中 $x\in\mathbb{R}^n$，$A$ 为 $n\times n$ 非奇异矩阵，$B\in\mathbb{R}^{n\times r}$，$C\in\mathbb{R}^{m\times n}$，$D\in\mathbb{R}^{m\times r}$，$y\in\mathbb{R}^m$，$u\in\mathbb{R}^r$。

### 1. 能控性判据（Criterion of Controllability）

**定义**：若存在一列不受约束的控制向量 $u(0),u(1),\dots,u(n-1)$，能使系统由 $x(0)$ 转移到 $x(n)=0$，则称系统能控。

状态方程的解为
$$
x(k) = A^{k}x(0) + \sum_{i=0}^{k-1}A^{k-1-i}Bu(i)
$$
令 $k=n$、$x(n)=0$，并左乘 $A^{-n}$：
$$
x(0) = -\sum_{i=0}^{n-1}A^{-1-i}Bu(i)
= -[\,A^{-1}B\ \ \ A^{-2}B\ \ \ \cdots\ \ \ A^{-n}B\,]
\begin{bmatrix}u(0)\\ u(1)\\ \vdots\\ u(n-1)\end{bmatrix}
$$
由解的存在唯一性定理，多输入线性离散系统能控的充要条件为
$$
\mathrm{rank}[\,A^{-1}B\ \ \ A^{-2}B\ \ \ \cdots\ \ \ A^{-n}B\,] = n
$$
或等价地（因 $A^{-n}$ 非奇异，秩不变，仅列顺序换）
$$
\mathrm{rank}[\,A^{n-1}B\ \ \ \cdots\ \ \ AB\ \ \ B\,] = n
\qquad\Longleftrightarrow\qquad
\mathrm{rank}\,Q_d = \mathrm{rank}[\,B\ \ \ AB\ \ \ \cdots\ \ \ A^{n-1}B\,] = n
$$
**输出完全能控判据**：离散系统输出能控的充要条件为
$$
\mathrm{rank}\,Q_d^{o} = \mathrm{rank}\,[\,CB\ \ \ CAB\ \ \ \cdots\ \ \ CA^{n-1}B\ \ \ D\,] = m
$$

**例9-34**：时不变离散系统状态方程（3 阶双输入，矩阵见课件），判断其能控性。

**解**：能控性矩阵的秩
$$
\mathrm{rank}[B\ \ AB\ \ A^{2}B] = 3 = n
$$
→ **系统能控**。

> 注：多输入时不变离散系统的能控性矩阵为 $n\times nr$ 维，能控条件是其秩为 $n$；计算秩达到 $n$ 即可停止计算。

### 2. 能观性判据（Criterion of Observability）

考虑零输入离散系统
$$
x(k+1) = Ax(k),\qquad y(k) = Cx(k)
$$

**定义**：若在有限的采样周期数内，输出 $y(k)$ 能确定初始状态向量 $x(0)$，则系统能观。

若系统能观，则有
$$
x(k) = A^{k}x(0)\ \Longrightarrow\ y(k) = CA^{k}x(0)
$$
即由 $k=0,1,\dots,n-1$ 可得
$$
y(0) = Cx(0),\qquad y(1) = CAx(0),\qquad \cdots,\qquad y(n-1) = CA^{n-1}x(0)
$$
这是 $n$ 个矩阵方程；因 $y(k)$ 为 $m$ 维向量，共 $nm$ 个代数方程，含未知量 $x_1(0),x_2(0),\dots,x_n(0)$。要从这 $nm$ 个方程中唯一解出 $x_i(0)$，$nm\times n$ 系数矩阵的秩应为 $n$，即
$$
\mathrm{rank}\begin{bmatrix}C\\ CA\\ \vdots\\ CA^{n-1}\end{bmatrix} = n
$$
由于矩阵与其转置的秩相同，也可写作
$$
\mathrm{rank}\,R_d = \mathrm{rank}\,[\,C^T\ \ \ A^TC^T\ \ \ \cdots\ \ \ (A^T)^{n-1}C^T\,] = n
$$

**例9-35**：判断下列两系统的能观性。

**系统 $S_1$**（观测矩阵为 2 行）：
$$
x(k+1) = \begin{bmatrix}2 & 0 & 3\\ -1 & -2 & 0\\ 0 & 1 & 2\end{bmatrix}x(k),\qquad
y(k) = \begin{bmatrix}1 & 0 & 0\\ 0 & 1 & 0\end{bmatrix}x(k)
$$

**解**：构造能观性矩阵并求秩，计算表明其中存在 3 个线性无关的行向量，$\mathrm{rank}=3=n$ → **系统 1 能观**。

**系统 $S_2$**：
$$
x(k+1) = \begin{bmatrix}1 & 0 & 1\\ 0 & 2 & 1\\ 0 & 0 & 3\end{bmatrix}x(k) + Bu(k),\qquad y(k) = \begin{bmatrix}1 & 0 & 0\end{bmatrix}x(k)
$$

**解**：能观性矩阵 $\begin{bmatrix}C\\ CA\\ CA^2\end{bmatrix}$ 的第 2、3 列（即状态 $x_2,x_3$ 对应的列）均为零向量，$\mathrm{rank}<3=n$ → **系统 2 不可观**。

> 考试技巧：判断能观性不必算满 $n$ 行——单输出系统算至秩达 $n$ 即可；利用行/列全零可直接看出秩亏。

---

## 八、9.5.6 连续线性时不变系统的结构分析（结构分解）

### 1. 能控分解（Controllable Decomposition）

**问题**：系统 $\dot{x}=Ax+Bu$，$y=Cx$ 不完全能控（能控性矩阵的秩 $r<n$）。

**做法**：从能控性矩阵 $Q_c$ 中选出 $r$ 个线性无关列，再任取 $n-r$ 个列（与其线性无关）构成非奇异变换阵 $T^{-1}$，令
$$
x = T\tilde{x},\qquad \tilde{x} = T^{-1}x = \begin{bmatrix}\tilde{x}_{c}\\ \tilde{x}_{\bar{c}}\end{bmatrix}
$$
则变换后系统的动态方程为
$$
\begin{bmatrix}\dot{\tilde{x}}_{c}\\ \dot{\tilde{x}}_{\bar{c}}\end{bmatrix}
=
\begin{bmatrix}A_{11} & A_{12}\\ 0 & A_{22}\end{bmatrix}
\begin{bmatrix}\tilde{x}_{c}\\ \tilde{x}_{\bar{c}}\end{bmatrix}
+
\begin{bmatrix}B_1\\ 0\end{bmatrix}u,\qquad
y = \begin{bmatrix}C_1 & C_2\end{bmatrix}\tilde{x}
$$
其中
$$
T^{-1}AT = \begin{bmatrix}A_{11} & A_{12}\\ 0 & A_{22}\end{bmatrix},\qquad
T^{-1}B = \begin{bmatrix}B_1\\ 0\end{bmatrix},\qquad
CT = \begin{bmatrix}C_1 & C_2\end{bmatrix}
$$

**分解结果**：
- **能控子系统**（$r$ 维，$\tilde{x}_c$）：$\dot{\tilde{x}}_c = A_{11}\tilde{x}_c + A_{12}\tilde{x}_{\bar{c}} + B_1u$，$(A_{11},B_1)$ 完全能控；
- **不能控子系统**（$n-r$ 维，$\tilde{x}_{\bar c}$）：$\dot{\tilde{x}}_{\bar c} = A_{22}\tilde{x}_{\bar c}$（无输入作用）。

**例9-36**：对系统（3 阶，$A,b,c$ 由课件给出）进行能控分解。

**解**：
$$
\mathrm{rank}[\,b\ \ \ Ab\ \ \ A^{2}b\,] = 2 < 3
$$
→ 系统不完全能控。取变换阵（前两列为 $b$、$Ab$，第三列任取与它们线性无关的列）：
$$
T^{-1} = \begin{bmatrix}1 & 0 & 1\\ 0 & 3 & 0\\ 1 & 0 & 0\end{bmatrix},\qquad
T = \begin{bmatrix}0 & 0 & 1\\ 1 & 0 & -3\\ 0 & 1 & 0\end{bmatrix}\text{（具体以课件为准）}
$$
经变换后：
- **能控子系统**（2 维）的动态方程为 $\dot{\tilde{x}}_{c1} = \cdots + \begin{bmatrix}\cdots\end{bmatrix}u$，$y = \cdots$（$2\times2$ 块 $A_{11}$ 与 $B_1$ 完全能控）；
- **不能控子系统**（1 维）的动态方程为 $\dot{\tilde{x}}_2 = \lambda\tilde{x}_2$（无输入）。

### 2. 能观分解（Observable Decomposition）

**问题**：系统 $\dot{x}=Ax+Bu$，$y=Cx$ 不完全能观（能观性矩阵秩 $l<n$）。

**做法**：取能观性矩阵中 $l$ 个线性无关行与任取的 $n-l$ 行构成非奇异变换 $T^{-1}$：
$$
\tilde{x} = T^{-1}x = \begin{bmatrix}\tilde{x}_{o}\\ \tilde{x}_{\bar{o}}\end{bmatrix}
$$
变换后
$$
T^{-1}AT = \begin{bmatrix}A_{11} & 0\\ A_{21} & A_{22}\end{bmatrix},\qquad
T^{-1}B = \begin{bmatrix}B_1\\ B_2\end{bmatrix},\qquad
CT = \begin{bmatrix}C_1 & 0\end{bmatrix}
$$
即
$$
\begin{bmatrix}\dot{\tilde{x}}_{o}\\ \dot{\tilde{x}}_{\bar o}\end{bmatrix}
=
\begin{bmatrix}A_{11} & 0\\ A_{21} & A_{22}\end{bmatrix}
\begin{bmatrix}\tilde{x}_{o}\\ \tilde{x}_{\bar o}\end{bmatrix}
+
\begin{bmatrix}B_1\\ B_2\end{bmatrix}u,\qquad
y = \begin{bmatrix}C_1 & 0\end{bmatrix}\tilde{x}
$$

**分解结果**：
- **能观子系统**（$l$ 维）：$\dot{\tilde{x}}_o = A_{11}\tilde{x}_o + B_1u$，$y_o = C_1\tilde{x}_o$，$(A_{11},C_1)$ 完全能观；
- **不能观子系统**（$n-l$ 维）：$\dot{\tilde{x}}_{\bar o} = A_{21}\tilde{x}_o + A_{22}\tilde{x}_{\bar o} + B_2u$（其状态不出现在输出中）。

**例9-38（能观分解部分）**：系统动态方程为
$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\end{bmatrix}
=
\begin{bmatrix}-1 & 0 & 1\\ 1 & 3 & 0\\ 0 & -1 & 2\end{bmatrix}x
+
\begin{bmatrix}1\\ 1\\ 1\end{bmatrix}u,\qquad
y = \begin{bmatrix}1 & 0 & 1\end{bmatrix}x
$$

**解**：能观性矩阵
$$
Q_o = \begin{bmatrix}C\\ CA\\ CA^2\end{bmatrix}
$$
经计算 $\mathrm{rank}\,Q_o = 2 < 3$ → 系统不完全能观，能观部分维数为 2。选取变换矩阵（前两行取 $Q_o$ 的 2 个线性无关行，第 3 行任取线性无关向量）
$$
T^{-1} = \begin{bmatrix}0 & 1 & 2\\ 1 & 2 & 3\\ 0 & 0 & 1\end{bmatrix},\qquad
T = \begin{bmatrix}1 & 2 & -1\\ 1 & 1 & 0\\ 2 & 0 & 1\end{bmatrix}\ \text{（具体数值以课件为准）}
$$
线性变换后的新系统为（$A = T^{-1}AT$，$B = T^{-1}B$，$C = CT$），其中**能观子系统**（2 维）的状态方程为（见课件），不能观部分（1 维）不含在输出中。

### 3. 按能控性与能观性的标准分解（卡尔曼结构分解）

**思想**：对既不完全能控、又不完全能观的系统 $(A,B,C)$，先按能控性分解，再分别对能控子系统与不能控子系统按能观性分解：
$$
x = T_c\begin{bmatrix}x_{c}\\ x_{\bar c}\end{bmatrix}\ \longrightarrow\ 
\begin{bmatrix}x_{co}\\ x_{c\bar o}\end{bmatrix} = T_{co,1}^{-1}x_c,\qquad
\begin{bmatrix}x_{\bar co}\\ x_{\bar c\bar o}\end{bmatrix} = T_{co,2}^{-1}x_{\bar c}
$$
最后综合得到四个子状态：**能控能观**（$x_{co}$）、**能控但不可观**（$x_{c\bar o}$）、**不能控但能观**（$x_{\bar c o}$）、**既不能控又不可观**（$x_{\bar c\bar o}$）。

经总变换 $T^{-1}$ 后，系统动态为
$$
\begin{bmatrix}\dot{x}_{co}\\ \dot{x}_{c\bar o}\\ \dot{x}_{\bar c o}\\ \dot{x}_{\bar c\bar o}\end{bmatrix}
=
\begin{bmatrix}
A_{11} & 0 & A_{13} & 0\\
A_{21} & A_{22} & A_{23} & A_{24}\\
0 & 0 & A_{33} & 0\\
0 & 0 & A_{43} & A_{44}
\end{bmatrix}
\begin{bmatrix}x_{co}\\ x_{c\bar o}\\ x_{\bar c o}\\ x_{\bar c\bar o}\end{bmatrix}
+
\begin{bmatrix}B_1\\ B_2\\ 0\\ 0\end{bmatrix}u,\qquad
y = \begin{bmatrix}C_1 & 0 & C_3 & 0\end{bmatrix}x
$$

四个子系统的动态方程：

- **能控且能观子系统**（$x_{co}$）：
  $$
  \dot{x}_{co} = A_{11}x_{co} + A_{13}x_{\bar c o} + B_1u,\qquad y_{co} = C_1x_{co}
  $$
- **能控但不可观子系统**（$x_{c\bar o}$）：
  $$
  \dot{x}_{c\bar o} = A_{21}x_{co} + A_{22}x_{c\bar o} + A_{23}x_{\bar c o} + A_{24}x_{\bar c\bar o} + B_2u
  $$
  （其输出部分不出现）
- **不能控但能观子系统**（$x_{\bar c o}$）：
  $$
  \dot{x}_{\bar c o} = A_{33}x_{\bar c o},\qquad y_{\bar c o} = C_3x_{\bar c o}
  $$
- **既不能控又不能观子系统**（$x_{\bar c\bar o}$）：
  $$
  \dot{x}_{\bar c\bar o} = A_{43}x_{\bar c o} + A_{44}x_{\bar c\bar o}
  $$

> 实用注记：直接计算总的变换矩阵 $T_{co}^{-1}$ 比较麻烦（complicated），常规做法是**分步分解**——先做能控分解，再对可控与不可控子系统分别做能观分解，逐步分离出四个子系统。

**例9-38（能控能观标准分解部分）**：系统同前（不完全能控且不完全能观），对其进行能控与能观分解。

**解**：

**(1) 能控分解**：构造分解矩阵
$$
T_c^{-1} = \begin{bmatrix}1 & 1 & 0\\ 0 & 1 & 1\\ 0 & 0 & 1\end{bmatrix}\ \text{（取能控性矩阵的线性无关列等构成）}
$$
分解后系统为（能控部分 2 维、不能控部分 1 维）：
$$
\dot{x}_c = \begin{bmatrix}\cdots\end{bmatrix}x_c + \begin{bmatrix}1\\ 1\end{bmatrix}u,\qquad y = \begin{bmatrix}\cdots\end{bmatrix}x_c
$$
其中**不能控子系统为一维且能观**，即它是"不能控但能观"子系统。

**(2) 对能控子系统做能观分解**：能观分解矩阵为
$$
T_{co}^{-1} = \begin{bmatrix}1 & 1\\ 0 & 1\end{bmatrix},\qquad T_{co} = \begin{bmatrix}1 & -1\\ 0 & 1\end{bmatrix}
$$
分解后得到能控且能观的 1 维子系统与能控但不可观的 1 维子系统。

**(3) 合成**：综合上述两次变换，总的能控能观标准分解式为
$$
x = T_c\,T_{co}\,\tilde{x},\qquad
T_{co,总} = \begin{bmatrix}T_{co} & 0\\ 0 & I\end{bmatrix},\qquad
T = T_c\,T_{co,总} = \begin{bmatrix}1 & 0 & 0\\ 1 & 1 & 0\\ 1 & 1 & 1\end{bmatrix}\text{（形如，具体以课件为准）}
$$
最终四个子系统中：能控能观子系统（1 维）即系统的"最小实现"部分，能控不可观、不可控能观、不可控不可观子系统依次分离。

> 结构分解的核心意义：只有**能控且能观**子系统才完整地反映输入—输出（传递函数）行为；它对应于传递函数不可约（无零极点对消）的最小部分。传递函数可约性、能控性/能观性丢失与结构分解三者相互印证。

---

## 知识点小结（考试要点）

1. **概念对**：能控性 = 输入影响所有状态；能观性 = 输出反映所有状态；仅对状态空间描述有意义；时不变系统的能控性/能观性与初始时刻 $t_0$ 无关。
2. **状态能控定义**：非零 $x(t_0)=x_0$ 经无约束控制 $u(t)$ 在有限时间转移到 $x(t_1)=0$（原点）；系统能控 = 状态空间中所有非零状态都能控。
3. **凯莱—哈密顿定理**：$f(A)=A^n+a_{n-1}A^{n-1}+\cdots+a_0I=0$；推论 1：$A^k\ (k>n)$ 可表为 $A$ 的 $(n-1)$ 次多项式；推论 2：$e^{At}=\sum_{m=0}^{n-1}\alpha_m(t)A^m$（能控/能观判据推导的根基）。
4. **能控性代数判据（重点）**：$\mathrm{rank}[B\ \ AB\ \ \cdots\ \ A^{n-1}B]=n$。推导链：终态原点方程 → $x(0)=-\int_0^{t_1}e^{-A\tau}Bu\,d\tau$ → 用 $e^{-A\tau}$ 多项式展开 → $x(0)=-\sum A^kB\beta_k$ → 唯一解 ⟺ 满秩。
5. **输出能控性**：$\mathrm{rank}[CB\ \ CAB\ \ \cdots\ \ CA^{n-1}B\ \ D]=m$（注意含 $D$，目标秩为 $m$）。
6. **能观性定义**：$x(t_0)$ 由 $[t_0,t_1]$ 上的 $y(t)$ 唯一确定 ⟺ 完全能观；至少一个状态不能确定 ⟺ 不完全能观。
7. **能观性代数判据（重点）**：$\mathrm{rank}\,[C^T\ \ A^TC^T\ \ \cdots\ \ (A^T)^{n-1}C^T]=n$ 或 $\mathrm{rank}\begin{bmatrix}C\\ CA\\ \vdots\\ CA^{n-1}\end{bmatrix}=n$。推导链：$y(t)=Ce^{At}x(0)=\sum\alpha_k(t)CA^kx(0)$ → 唯一解 ⟺ 满秩。讨论能观性只需考察零输入系统。
8. **传递函数判据**：状态能控且能观 ⟺ 传递函数无零极点对消（无可约因子）；有对消时系统不可控或不可观（选不同状态变量会分别显现），可约传递函数信息不完全。
9. **对偶原理（Kalman）**：$(A,B,C)$ 的对偶系统为 $(A^T,C^T,B^T)$；原系统能观 ⟺ 对偶系统能控，原系统能控 ⟺ 对偶系统能观。
10. **三类判据**：
    - 判据 1（代数判据）：$Q_c=[B\ \ AB\ \cdots\ A^{n-1}B]$ 满秩 ↔ 能控；$Q_o$ 满秩 ↔ 能观；
    - 判据 2（互异特征值对角标准型）：输入矩阵 $\bar B$ **无全零行** ↔ 能控；输出矩阵 $\bar C$ **无全零列** ↔ 能观；
    - 判据 3（约当标准型）：每个约当块**末行**对应的 $\bar B$ 行不全为零 ↔ 能控；每个约当块**首行**对应的 $\bar C$ 列不全为零 ↔ 能观；两约当块特征值相同则该简单结论不成立。
11. **能控标准型 / 能观标准型**：能控标准型 $A$ 为下置伴随（companion）矩阵、$B=[0\ \cdots\ 0\ 1]^T$；能观标准型为其转置结构、$C=[0\ \cdots\ 0\ 1]$。
12. **离散系统**（$A$ 非奇异）：能控 ⟺ $\mathrm{rank}[A^{-1}B\ \ \cdots\ \ A^{-n}B]=n$ 或 $\mathrm{rank}[B\ \ AB\ \cdots\ A^{n-1}B]=n$；能观 ⟺ $\mathrm{rank}\begin{bmatrix}C\\ CA\\ \vdots\\ CA^{n-1}\end{bmatrix}=n$（$nm$ 个代数方程解 $n$ 个初始状态，唯一解要求秩 $n$）；输出能控：$\mathrm{rank}[CB\ \cdots\ CA^{n-1}B\ \ D]=m$。多输入能控矩阵 $n\times nr$，秩算到 $n$ 即可停。
13. **结构分解（卡尔曼分解）**：能控分解 $\begin{bmatrix}A_{11}&A_{12}\\ 0&A_{22}\end{bmatrix},\ \begin{bmatrix}B_1\\ 0\end{bmatrix}$；能观分解 $\begin{bmatrix}A_{11}&0\\ A_{21}&A_{22}\end{bmatrix},\ \begin{bmatrix}C_1&0\end{bmatrix}$；综合分解把系统分离为能控能观、能控不可观、不可控能观、不可控不可观四个子系统；只有能控能观子系统对应传递函数的不可约部分。实际计算总变换阵复杂，应**分步分解**（先能控、后能观）。
