# 自动控制原理II —— 控制系统状态空间分析：9.1～9.2 基本概念（知识点总结）

> **来源课件**：Lesson 1 9.1~9.2 Basic Concept(2x45')（PPT 共 26 页，本讲 2×45′；文本提取稿：`自动控制原理/preorder/_tmp_txt/Lesson 1 9.1~9.2 Basic Concept(2x45').txt`）
> **所属章节**：第 9 章 控制系统的状态空间分析（Chapter 9 Analysis of Control Systems in State Space）
> **主讲**：刘Sir（liulei@mail.hust.edu.cn）
> **本讲范围**：9.1 引言（Introduction）与 9.2 状态空间与状态方程（State-Space and State-Equation）——现代控制理论（状态空间法）的基本概念

## 第9章 控制系统的状态空间分析（章节总览）

| 小节 | 主题 |
|---|---|
| 9.1 | Introduction 引言（为什么需要现代控制理论） |
| 9.2 | State-Space and State-Equation 状态空间与状态方程（**本讲重点**） |
| 9.3 | State-Space Establishing of Linear System 线性系统状态空间的建立 |
| 9.4 | Solving the Linear Time-Invariant State Equation 线性定常状态方程的求解 |
| 9.5 | Controllability and Observability 能控性与能观性 |
| 9.6 | Feedback Structure and State-Observers 反馈结构与状态观测器 |

本讲（Lesson 1，2×45′）只讲授 9.1、9.2 两节，属于状态空间法的入门与基本概念部分。

---

## 9.1 引言（Introduction）

### 9.1.1 经典控制实例引入：瓦特蒸汽机调速系统

课件以瓦特蒸汽机调速系统图片开篇，涉及：

- **Mr. J. Watt（瓦特）** 与 **离心调速器（Centrifugal Governor）**；
- 系统构成：**蒸汽机（Steam Engine）— 调速器（Governor）— 蒸汽阀（Steam Valve）— 负载（Load）**；
- 原理简介：由蒸汽机带动调速器旋转，调速器通过飞球离心力感受转速，进而调节**蒸汽阀**开度以稳定转速，这是经典反馈控制思想的早期工程原型。

### 9.1.2 为什么要学习现代控制理论（Why Modern Control Theory?）

课件给出三大理由：

1. **结果与过程（Result and Process）**
   经典控制理论回答的是：**Why feedback?（为何要反馈？）** 与 **How feedback?（如何反馈？）** 这类输入—输出层面的问题；但它无法回答 **What about the intermediate states?（系统内部中间状态如何变化？）**，即无法观测与控制系统的内部动态过程（课件图中以加减比较环节示意反馈闭环，但对中间状态无能为力）。

2. **内部关系与耦合（Internal relationship and Coupling，耦合）**
   实际系统内部各变量之间存在相互耦合，多输入多输出（MIMO）情形下必须研究内部变量关系。

3. **航天科学的要求（Aerospace science requirement）**
   航天等高新技术领域对控制系统提出了高精度、高可靠性的新要求，经典方法难以胜任。

多变量系统示意（系统以 $p$ 维输入、$q$ 维输出、$n$ 个内部变量描述）：

```
u1, u2, …, up （输入）  →  系统内部：x1, x2, …, xn （状态）  →  y1, y2, …, yq （输出）
```

- **应用领域（Areas）**：航空航天科学（Aerospace Science）、机器人学（Robotics）、工业（Industry）等。
- **状态空间方法带来的益处（Benefit）**：提供了新的数学工具（Mathematical Tools）、理论基础（Theory Foundation）与研究方法（Research Method）。
- **核心思想**：不仅考察系统的**外部信息（External Information）**——即输入、输出变量（Input & Output Variable）；而且考察系统的**内部信息（Internal Information）**——即**状态变量（State Variable）**。

---

## 9.2 状态空间与状态方程（State-Space and State-Equation）

### 9.2.1 基本概念（Concepts）

课件按 1—8 逐条给出下列概念：

**（1）状态（State）**
在**时间域**中，用来描述系统运动及其运动信息的一组变量的**集合（set）**。

**（2）状态变量（State-variable）**
描述系统“状态”的**最小的一组变量**。直观地，系统的状态所包含的信息足以确定系统**未来的行为**；在 $n$ 阶微分方程描述的系统中，应有 **$n$ 个独立的状态变量**。

> **注意（Attention）**：
> - 状态变量是描述系统动态运动的**充要条件**（NSC —— Necessary and Sufficient Condition，必要充分条件）；
> - **状态变量的选取不唯一（State-variable is not unique）**。

**（3）状态向量（State-vector）**
由 $n$ 个状态变量 $x_1(t), x_2(t), \ldots, x_n(t)$ 构成向量以描述被观测的状态：

$$
X(t) = \big[x_1(t),\ x_2(t),\ \ldots,\ x_n(t)\big]^{T}
$$

**（4）状态空间（State-space）**
以状态变量 $x_1(t), x_2(t), \ldots, x_n(t)$ 为基（坐标）张成的 **$n$ 维空间**。

**（5）状态轨迹（State-locus，状态轨线）**
在某一特定时刻 $t_0$，状态 $x(t_0)$ 是状态空间中的**一个点**；在一段时间 $t$ 内，状态 $x(t)$ 的运动将在状态空间中描绘出一条**轨迹（轨线）**，称为状态轨迹。

**（6）状态方程（State-equation）**
两个或两个以上状态函数之间的数学关系，即**状态变量与输入之间**的动态关系：

$$
\dot x(t) = f\big[x(t),\ u(t),\ t\big]\qquad\text{（连续系统）}
$$

$$
x(k+1) = f\big[x(k),\ u(k),\ k\big]\qquad\text{（离散系统）}
$$

**（7）输出方程（Output-equation）**
描述**输出与状态**之间、以及**输出与输入**之间关系的方程：

$$
y(t) = g\big[x(t),\ u(t),\ t\big]\qquad\text{（连续系统）}
$$

$$
y(k) = g\big[x(k),\ u(k),\ k\big]\qquad\text{（离散系统）}
$$

**（8）状态空间表达式（State-space Representation）**
用**状态方程 + 输出方程**共同表示系统：

$$
\begin{cases}
\dot x(t) = f\big[x(t),\ u(t),\ t\big]\\[2pt]
y(t) = g\big[x(t),\ u(t),\ t\big]
\end{cases}\ \text{（连续）},\qquad
\begin{cases}
x(k+1) = f\big[x(k),\ u(k),\ k\big]\\[2pt]
y(k) = g\big[x(k),\ u(k),\ k\big]
\end{cases}\ \text{（离散）}
$$

### 9.2.2 线性系统的状态空间表达式

若 $f$、$g$ 为**线性函数**，即为线性系统：

- **线性时变系统（Linear Time-Varying System）**：

$$
\begin{cases}
\dot X(t) = A(t)\,x(t) + B(t)\,u(t)\\[2pt]
Y(t) = C(t)\,x(t) + D(t)\,u(t)
\end{cases}
$$

- **线性定常系统（Linear Time-Invariant System，LTI）**：

$$
\begin{cases}
\dot X(t) = A\,x(t) + B\,u(t)\\[2pt]
Y(t) = C\,x(t) + D\,u(t)
\end{cases}
$$

> **特点**：
> - **状态方程**：一阶微分方程（向量形式，实际为一阶微分方程组）；
> - **输出方程**：代数方程（algebraic equation，向量形式）。

#### 状态空间表达式中各矩阵的名称与含义

| 矩阵 | 英文名称 | 中文名称 |
|---|---|---|
| $A$ | State Matrix（Systems matrix, coefficients matrix） | **状态矩阵**（系统矩阵、系数矩阵） |
| $B$ | Input Matrix（Control Matrix） | **输入矩阵**（控制矩阵） |
| $C$ | Observing Matrix（Output Matrix） | **观测矩阵**（输出矩阵） |
| $D$ | Feedforward Matrix（Directly Transfer Matrix） | **前馈矩阵**（直接传递矩阵） |

线性定常系统可简记为四元组 **$\{A,\ B,\ C,\ D\}$**。其结构关系（Relationship Chart）为：输入 $u$ 经 $B$ 进入系统，状态 $x$ 由 $A$ 构成自身动态回路并经 $C$ 映射为输出 $y$，输入经 $D$ 直接前馈叠加到输出：

```
u(t) ──►[B]──► ⊕ ──► ∫ ──► x(t) ──►[C]──► ⊕ ──► y(t)
               ▲    (ẋ = Ax + Bu)            ▲
               │                              │
               └──────[A]◄── x(t)  ◄──[D]────┘
                                           （D：u 直接前馈）
```

即：$u$ 经 $B$ 后与状态反馈项 $Ax$ 求和得 $\dot x$，经积分器得状态 $x$；$x$ 经 $C$ 得输出的主通道，$u$ 再经 $D$ 前馈直接加到输出端。

#### 状态方程：输入与状态的关系（单输入线性定常系统）

展开为 $n$ 个一阶微分方程：

$$
\begin{cases}
\dot x_1(t) = a_{11}x_1(t) + a_{12}x_2(t) + \cdots + a_{1n}x_n(t) + b_1u(t)\\[2pt]
\dot x_2(t) = a_{21}x_1(t) + a_{22}x_2(t) + \cdots + a_{2n}x_n(t) + b_2u(t)\\[2pt]
\qquad\qquad\qquad\vdots\\[2pt]
\dot x_n(t) = a_{n1}x_1(t) + a_{n2}x_2(t) + \cdots + a_{nn}x_n(t) + b_nu(t)
\end{cases}
$$

其中**常系数 $a_{11}, \ldots, a_{nn}$ 与 $b_1, \ldots, b_n$ 由系统本身的特性决定**。

矩阵表示：

$$
\dot x(t) = A\,x(t) + b\,u(t)
$$

其中

$$
x = \begin{bmatrix}x_1\\ x_2\\ \vdots\\ x_n\end{bmatrix},\qquad
A = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n}\\ a_{21} & a_{22} & \cdots & a_{2n}\\ \vdots & \vdots & \ddots & \vdots\\ a_{n1} & a_{n2} & \cdots & a_{nn} \end{bmatrix},\qquad
b = \begin{bmatrix}b_1\\ b_2\\ \vdots\\ b_n\end{bmatrix}
$$

#### 多输入（MIMO）线性定常系统的状态方程

展开为（$i = 1, 2, \ldots, n$；系统有 $p$ 个输入 $u_1, \ldots, u_p$）：

$$
\dot x_i = a_{i1}x_1 + a_{i2}x_2 + \cdots + a_{in}x_n + b_{i1}u_1 + b_{i2}u_2 + \cdots + b_{ip}u_p
$$

矩阵表示：

$$
\dot x(t) = A\,x(t) + B\,u(t)
$$

其中 $x$ 为 $n$ 维状态向量，$u$ 为 $p$ 维输入向量，$A$ 为 $n \times n$ 矩阵，$B$ 为 $n \times p$ 输入矩阵。

#### 输出方程：输出与状态、输出与输入的关系

> **输出由系统的任务决定（Output is decided by system task）**——选择哪些变量作为输出取决于实际需要。

**（1）单输出（单输入）线性定常系统的一般形式：**

$$
y(t) = c_1x_1(t) + c_2x_2(t) + \cdots + c_nx_n(t) + d\,u(t)
$$

矩阵表示：

$$
y(t) = c\,x(t) + d\,u(t),\qquad c = \begin{bmatrix}c_1 & c_2 & \cdots & c_n\end{bmatrix}
$$

其中常系数 $c_1, c_2, \ldots, c_n$ 与 $d$ 也与系统特性有关。

**（2）多输入多输出（MIMO）系统输出方程的一般形式**（$q$ 个输出 $y_1, \ldots, y_q$，$p$ 个输入）：

$$
\begin{cases}
y_1 = c_{11}x_1 + \cdots + c_{1n}x_n + d_{11}u_1 + \cdots + d_{1p}u_p\\[2pt]
y_2 = c_{21}x_1 + \cdots + c_{2n}x_n + d_{21}u_1 + \cdots + d_{2p}u_p\\[2pt]
\qquad\qquad\qquad\vdots\\[2pt]
y_q = c_{q1}x_1 + \cdots + c_{qn}x_n + d_{q1}u_1 + \cdots + d_{qp}u_p
\end{cases}
$$

矩阵表示：

$$
y = C\,x + D\,u
$$

其中 $C$ 为 $q \times n$ 观测矩阵（输出矩阵），$D$ 为 $q \times p$ 前馈矩阵。

> **维数小结**：状态向量 $x$ 为 $n$ 维，输入向量 $u$ 为 $p$ 维，输出向量 $y$ 为 $q$ 维；$A:n\times n$，$B:n\times p$，$C:q\times n$，$D:q\times p$。

#### 状态空间分析方法的优点（Advantages）

1. **计算（Computing）**：用计算机求解**一阶微分方程组**比求解高阶微分方程更容易；
2. **表示（Representation）**：利用**向量矩阵**简化微分方程的数学表示；
3. **适用范围（Field）**：适用于多输入多输出（MIMO）系统、定常（时不变）系统、随机过程与采样系统等；
4. **特殊性（Special）**：状态空间表示法的使用**不限于线性元件与零初始条件**的系统（即对非线性、非零初始条件情形同样适用）。

### 9.2.3 例题（Examples）：RLC 电路状态空间模型的建立

**例 9-1** 求 RLC 串联电路的状态空间模型（State-space model）。

电路：电压源 $e_i(t)$ 与电阻 $R$、电感 $L$、电容 $C$ 串联成回路，回路电流为 $i(t)$：

```
   ┌─────── R ─────── L ─────── C ───────┐
   │                                      │
  u(t) = ei(t)              回路电流 i(t)   │
   │                                      │
   └──────────────────────────────────────┘
```

设 $e_i(t)$ 为输入：$u(t)$，$i(t)$ 为输出：$y(t)$，并选取适当的状态变量 $i(t)$ 与 $\int i(t)\,dt$。

**物理关系（Physics relationship）**——由基尔霍夫电压定律（KVL）：

$$
L\frac{di}{dt} + Ri + \frac{1}{C}\int i\,dt = e_i(t) = u(t)
$$

**第 1 组状态变量：**

$$
x_1(t) = i(t),\qquad x_2(t) = \int i(t)\,dt
$$

**状态方程：** 将 $L\dfrac{di}{dt} + Ri + \dfrac{1}{C}\int i\,dt = u$ 改写为：

$$
\dot x_1(t) = -\frac{R}{L}x_1(t) - \frac{1}{LC}x_2(t) + \frac{1}{L}u(t)
$$

$$
\dot x_2(t) = x_1(t)
$$

**输出方程：** 因 $y(t) = i(t) = x_1(t)$，故

$$
y(t) = \begin{bmatrix}1 & 0\end{bmatrix}\begin{bmatrix}x_1(t)\\ x_2(t)\end{bmatrix}
$$

**矩阵形式（状态空间表达式）：**

$$
\dot x(t) = A\,x(t) + B\,u(t),\qquad y(t) = C\,x(t)
$$

$$
A = \begin{bmatrix} -\dfrac{R}{L} & -\dfrac{1}{LC}\\[4pt] 1 & 0\end{bmatrix},\qquad
B = \begin{bmatrix} \dfrac{1}{L}\\[4pt] 0\end{bmatrix},\qquad
C = \begin{bmatrix} 1 & 0\end{bmatrix}
$$

课件在此处注明 “Not the end!!!!” —— 即第 1 组状态变量并非唯一选择。

**第 2 组状态变量（另选一组）：**

$$
x_1 = \frac{1}{C}\int i\,dt\ \text{（电容电压 } u_C\text{）},\qquad
x_2 = Ri + \frac{1}{C}\int i\,dt = Ri + u_C\ \text{（电阻、电容支路总电压）}
$$

由电路关系（此时 $i = \dfrac{x_2 - x_1}{R}$，$\dfrac{di}{dt} = \dfrac{u - x_2}{L}$）得：

$$
\dot x_1 = \frac{i}{C} = -\frac{1}{RC}x_1 + \frac{1}{RC}x_2
$$

$$
\dot x_2 = R\frac{di}{dt} + \frac{i}{C}
= -\frac{1}{RC}x_1 + \left(\frac{1}{RC} - \frac{R}{L}\right)x_2 + \frac{R}{L}u
$$

输出方程（$y = i = \dfrac{x_2 - x_1}{R}$）：

$$
y = \begin{bmatrix}-\dfrac{1}{R} & \dfrac{1}{R}\end{bmatrix}x
$$

对应矩阵：

$$
A = \begin{bmatrix} -\dfrac{1}{RC} & \dfrac{1}{RC}\\[4pt] -\dfrac{1}{RC} & \dfrac{1}{RC} - \dfrac{R}{L}\end{bmatrix},\qquad
B = \begin{bmatrix} 0\\[4pt] \dfrac{R}{L}\end{bmatrix},\qquad
C = \begin{bmatrix} -\dfrac{1}{R} & \dfrac{1}{R}\end{bmatrix}
$$

**两组状态空间表达式对比：**

| 选取 | 状态变量 | 状态空间表达式（$A$、$B$、$C$） |
|---|---|---|
| 第 1 组 | $x_1 = i$，$x_2 = \int i\,dt$ | $A=\begin{bmatrix}-R/L & -1/(LC)\\ 1 & 0\end{bmatrix}$，$B=\begin{bmatrix}1/L\\ 0\end{bmatrix}$，$C=[1\ \ 0]$ |
| 第 2 组 | $x_1 = \dfrac{1}{C}\int i\,dt$，$x_2 = Ri + \dfrac{1}{C}\int i\,dt$ | $A=\begin{bmatrix}-1/(RC) & 1/(RC)\\ -1/(RC) & 1/(RC)-R/L\end{bmatrix}$，$B=\begin{bmatrix}0\\ R/L\end{bmatrix}$，$C=[-1/R\ \ 1/R]$ |

同一系统（输入 $u$、输出 $y=i$ 完全相同），两组不同的状态变量得到两组**形式上不同**的状态方程与输出方程（矩阵）。

**结论（Conclusion）：状态空间表达式是不唯一的（State-space is non-unique）。**
- **状态变量不唯一**（State-variable is not unique）；
- **状态方程不唯一**（State-equation is not unique）；
- 不同的状态方程对应于不同的状态变量选取（Different state-equations with different state-variables）。

**两组状态变量之间的变换关系：**

第 1 组与第 2 组状态变量之间满足非奇异线性变换关系，例如本例中

$$
x_1^{(2)} = u_C = \frac{1}{C}x_2^{(1)},\qquad
x_2^{(2)} - x_1^{(2)} = Ri = R\,x_1^{(1)}
$$

一般地，**用任意不同的非奇异矩阵（nonsingular matrix，非奇异阵）$P$ 对状态作线性变换，均可得到一组新的状态变量**，即

$$
\tilde x = P\,x\qquad\text{（$P$ 为非奇异矩阵）}
$$

因此，状态变量的选取有**无穷多种（Infinite groups of state-variables）**，状态空间表达式也随之有无穷多种等价形式。

> 说明：课件第 25～26 页内容与本页重复（同一结论的再次排版展示）。

---

## 知识点小结（考试要点）

1. **基本概念（务必辨析清楚）**：状态 = 描述系统运动及其信息的一组变量（时间域）；状态变量 = 能确定系统未来行为的**最小**一组变量，$n$ 阶系统有 $n$ 个独立状态变量；状态变量是描述系统动态运动的**充要条件（NSC）**且**不唯一**；状态向量 $X(t)=[x_1,\ldots,x_n]^T$；由全部状态变量张成的 $n$ 维空间为状态空间；$t_0$ 时刻状态为状态空间中的一个点，随时间推移描绘**状态轨迹**。
2. **状态方程**描述状态变量与输入的关系（连续：$\dot x = f[x,u,t]$，一阶微分方程；离散：$x(k+1)=f[x(k),u(k),k]$）；**输出方程**描述输出与状态、输入的关系（$y = g[x,u,t]$，**代数方程**）；两者合称**状态空间表达式**。
3. **线性系统**（$f,g$ 为线性函数）：时变系统 $\dot x = A(t)x + B(t)u$、$y = C(t)x + D(t)u$；**定常（LTI）系统 $\dot x = Ax + Bu$、$y = Cx + Du$**，必须熟练默写。
4. **矩阵名称**：$A$ 状态矩阵（系统矩阵、系数矩阵）；$B$ 输入矩阵（控制矩阵）；$C$ 观测矩阵（输出矩阵）；$D$ 前馈矩阵（直接传递矩阵）。LTI 系统记为 $\{A,B,C,D\}$。**维数**：$A:n\times n$、$B:n\times p$、$C:q\times n$、$D:q\times p$（$x$ 为 $n$ 维、$u$ 为 $p$ 维、$y$ 为 $q$ 维）。
5. **系数含义**：状态方程系数 $a_{ij}$、$b_i$ 与输出方程系数 $c_i$、$d$ 均由**系统本身的特性**决定；输出变量的选取由**系统任务**决定。
6. **状态空间表达式的不唯一性**：不同的状态变量 ↔ 不同的状态方程；任意两组状态变量之间相差**非奇异线性变换 $\tilde x = Px$**；非奇异矩阵 $P$ 有无穷多个，故状态变量有无穷多种取法。
7. **例 9-1（RLC 电路）**：物理方程 $L\dfrac{di}{dt} + Ri + \dfrac{1}{C}\int i\,dt = u$；第 1 组取 $x_1=i$、$x_2=\int i\,dt$ 得 $A=\begin{bmatrix}-R/L & -1/(LC)\\ 1 & 0\end{bmatrix}$、$B=[1/L,\ 0]^T$、$C=[1,\ 0]$；换一组状态变量（如电容电压组合）得到形式不同但等价的 $A,B,C$。要求能由给定的状态变量写出状态空间表达式。
8. **状态空间分析方法的优点**：一阶方程组便于计算机求解；向量矩阵使表示简洁；适用于 MIMO、定常系统、随机过程与采样系统等；不限于线性元件与零初始条件。
