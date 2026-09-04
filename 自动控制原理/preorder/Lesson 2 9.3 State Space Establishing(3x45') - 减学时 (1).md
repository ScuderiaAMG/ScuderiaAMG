# 自动控制原理II —— 9.3 线性系统状态空间表达式的建立（知识点总结）

> **来源课件**：Lesson 2 9.3 State Space Establishing(3x45') - 减学时 (1).pdf（共81页）
> **课程信息**：自动控制原理II（现代控制理论基础部分：状态空间表达式），英文课件；本讲为"9.3 线性系统状态空间表达式的建立（Establishing of State-space of Linear System）"，3×45 分钟减学时压缩版
> **说明**：第9.1~9.2 讲已引入状态空间的基本描述（状态、状态变量、动态方程等）；本讲解决"如何建立"问题。公式中的参数编号、数值均按课件原文复原。

## 本讲总方法论（General Methodology，全课贯穿）

建立/变换状态空间表达式有五条途径：

1. **由系统的物理机理（物理定律）建立**（From Physics Mechanism of System）；
2. **由系统的微分方程建立**（From Differential Equations of System）；
3. **由系统的传递函数建立**（From Transfer Functions of System）；
4. **由系统的状态变量图（结构图）建立**（From State-variable Diagram of System）；
5. **状态空间的线性变换**（Linear Transformation of State space）。

（该清单在本课件第1、8、21页反复出现，作为全章提纲。）

---

## 9.3.1 由系统的物理机理建立状态空间表达式

**总体思想**：对实际物理系统，先按物理定律（牛顿定律、基尔霍夫定律等）列出系统的微分（或差分）方程，再选取一组状态变量，从而把原方程整理成状态方程与输出方程。

### 例 Ex.9-2：力—弹簧—阻尼（质量—弹簧—阻尼器）机械系统

> 无重力（without gravity）的力 $F$、弹簧（spring）$k$、质量 $m$、阻尼器（damper）$f$ 机械系统。$F(t)$ 为输入（Input），$y(t)$ 为输出（Output）。

由牛顿定律：

$$
m\ddot{y} + f\dot{y} + ky = F(t)
$$

若系统原来的位移与速度已知，则在给定输入下系统的解完全确定（据此可选择位移、速度为状态变量）。

**取位移和速度为状态变量：**

$$
x_1 = y,\qquad x_2 = v = \dot{y}
$$

**状态方程（Input 为 $u(t) = F(t)$）：**

$$
\begin{cases}
\dot{x}_1 = x_2 \\[4pt]
\dot{x}_2 = -\dfrac{k}{m}x_1 - \dfrac{f}{m}x_2 + \dfrac{1}{m}u
\end{cases}
$$

**状态空间表达式：**

$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\end{bmatrix}
=
\begin{bmatrix}0 & 1\\ -\frac{k}{m} & -\frac{f}{m}\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\end{bmatrix}
+
\begin{bmatrix}0\\ \frac{1}{m}\end{bmatrix}u,
\qquad
y = \begin{bmatrix}1 & 0\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\end{bmatrix}
$$

> **要点**：把物理上"位置、速度"（独立储能元件的特征量）取为状态变量，一阶微分方程组即为状态方程，输出关系式即为输出方程。

### 例 Ex.9-3：双质量弹簧—阻尼系统（两体机械系统）

> 无重力机构，输入为拉力 $F(t)$，输出为两质量块 $m_1$、$m_2$ 的位移 $y_1$、$y_2$。力学结构为：机架（墙壁）—弹簧 $k_1$、阻尼器 $f_1$—质量 $m_1$—弹簧 $k_2$、阻尼器 $f_2$—质量 $m_2$，拉力 $F$ 作用于 $m_2$（示意图见课件第4~6页，各符号下标以课件图为准）。

由牛顿定律列出 $m_1$、$m_2$ 的受力关系：

$$
m_1\ddot{y}_1 = k_2(y_2-y_1) + f_2(\dot{y}_2-\dot{y}_1) - k_1y_1 - f_1\dot{y}_1
$$

$$
m_2\ddot{y}_2 = F(t) - k_2(y_2-y_1) - f_2(\dot{y}_2-\dot{y}_1)
$$

**选取 4 个独立的状态变量**（两组位移与速度）：

$$
x_1 = y_1,\qquad x_2 = \dot{y}_1,\qquad x_3 = y_2,\qquad x_4 = \dot{y}_2
$$

**状态方程**（二阶力学方程组化为一阶向量方程）：

$$
\begin{cases}
\dot{x}_1 = x_2 \\[4pt]
\dot{x}_2 = -\dfrac{k_1+k_2}{m_1}x_1 - \dfrac{f_1+f_2}{m_1}x_2 + \dfrac{k_2}{m_1}x_3 + \dfrac{f_2}{m_1}x_4 \\[10pt]
\dot{x}_3 = x_4 \\[4pt]
\dot{x}_4 = \dfrac{k_2}{m_2}x_1 + \dfrac{f_2}{m_2}x_2 - \dfrac{k_2}{m_2}x_3 - \dfrac{f_2}{m_2}x_4 + \dfrac{1}{m_2}F(t)
\end{cases}
$$

**矩阵形式：**

$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\\ \dot{x}_4\end{bmatrix}
=
\underbrace{\begin{bmatrix}
0 & 1 & 0 & 0\\
-\frac{k_1+k_2}{m_1} & -\frac{f_1+f_2}{m_1} & \frac{k_2}{m_1} & \frac{f_2}{m_1}\\[2pt]
0 & 0 & 0 & 1\\
\frac{k_2}{m_2} & \frac{f_2}{m_2} & -\frac{k_2}{m_2} & -\frac{f_2}{m_2}
\end{bmatrix}}_{A}
\begin{bmatrix}x_1\\ x_2\\ x_3\\ x_4\end{bmatrix}
+
\underbrace{\begin{bmatrix}0\\0\\0\\ \frac{1}{m_2}\end{bmatrix}}_{B}F(t)
$$

输出方程（两输出 $y_1$、$y_2$ 即状态 $x_1$、$x_3$）：

$$
\begin{bmatrix}y_1\\ y_2\end{bmatrix}
=
\underbrace{\begin{bmatrix}1 & 0 & 0 & 0\\ 0 & 0 & 1 & 0\end{bmatrix}}_{C}
\begin{bmatrix}x_1\\ x_2\\ x_3\\ x_4\end{bmatrix}
$$

> **要点**：4 个储能元件（两弹簧—质量系统有 4 个独立能量存储变量：两个位移与两个速度）对应 4 个独立状态变量，状态方程仍写为 $\dot{x} = Ax + Bu$ 的标准形式。
>
> **备注（原课件第6~7页）**：第6页为纯图形页（相应系统的结构示意图）；第7页再给出一个以图示为主的机理建模补充例（旋转/扭振类系统：含转动惯量 $J$、扭转弹簧刚度 $k$、阻尼 $b$ 与转角 $\theta_1$、$\theta_2$ 及输入力矩 $M(t)$ 等图内标注文字，PDF 文本提取仅为片段）。其建模步骤与 Ex.9-2/Ex.9-3 完全相同：先按（转动）牛顿定律列微分方程，再取各独立转角的位移量与角速度为状态变量。

---

## 9.3.2 由系统的微分方程建立状态空间表达式

### 方法论与状态变量选取原则（第9~10页）

**方法论：**
1. 由系统物理机理建立系统的微分/差分方程；
2. 围绕方程与一组状态变量建立状态方程（一阶微分方程组）；
3. 根据系统输出与状态的关系建立输出方程。

**状态变量选取原则：**
- 状态变量的选择**不唯一**（Section of state variable is not unique）；
- 选取方法：
  1. 选取与初始条件有关的量；
  2. 选取具有明确物理意义的**独立储能元件（能量或信息）的特征量**，例如电感电流 $i$、电容电压 $u_c$、质量 $m$ 与速度 $v$ 等。

### 情形（一）：$n$ 阶线性微分方程中不包含输入 $u$ 的导数（Scenario (1)）

设 SISO 控制系统的动态过程为（$y$ 为输出、$u$ 为输入，输出各阶导数 $y^{(n-1)},\dots,\dot{y},y$）：

$$
y^{(n)} + a_1 y^{(n-1)} + \cdots + a_{n-1}\dot{y} + a_n y = b\,u
$$

若输出初始条件 $y(0),\dot{y}(0),\dots,y^{(n-1)}(0)$ 已知，且 $t\ge 0$ 的输入 $u(t)$ 给定，则系统任意时刻的行为可完全确定（这保证取 $y$ 及其导数为状态可行）。

**选取状态变量：**

$$
x_1 = y,\qquad x_2 = \dot{y},\qquad \cdots,\qquad x_n = y^{(n-1)}
$$

则：

$$
\begin{cases}
\dot{x}_1 = x_2\\
\dot{x}_2 = x_3\\
\quad\vdots\\
\dot{x}_{n-1} = x_n\\
\dot{x}_n = -a_n x_1 - a_{n-1}x_2 - \cdots - a_1 x_n + b\,u
\end{cases}
$$

**状态空间表达式：** $\dot{x} = Ax + Bu,\ \ y = Cx$

$$
x = \begin{bmatrix}x_1\\ x_2\\ \vdots\\ x_n\end{bmatrix},
\qquad
A = \begin{bmatrix}
0 & 1 & 0 & \cdots & 0\\
0 & 0 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \ddots & \vdots\\
0 & 0 & 0 & \cdots & 1\\
-a_n & -a_{n-1} & -a_{n-2} & \cdots & -a_1
\end{bmatrix},
\qquad
B = \begin{bmatrix}0\\ \vdots\\ 0\\ b\end{bmatrix},
$$

$$
C = \begin{bmatrix}1 & 0 & 0 & \cdots & 0\end{bmatrix}
$$

> **说明**：A 为友矩阵（companion matrix）型结构；$C=[1\ 0\ \cdots\ 0]$ 表示"取第一状态（即 $y$）为输出"。这种取法下状态变量图为 $n$ 个积分器串联：每个积分器的输出即对应一个状态变量（第14页图）：
> - 每个积分器的输出对应一个状态变量；
> - 状态方程由积分器输入端的 I/O 关系决定；
> - 输出方程在输出端给出。

### 例 Ex.9-4：由微分方程求状态空间表达式（第15页）

设系统动态过程的微分方程为（$u$、$y$ 分别为输入输出）：

$$
\dddot{y} + 6\ddot{y} + 11\dot{y} + 6y = 6u
$$

试求其状态空间表达式。

**解：** 取状态变量：

$$
x_1 = y,\qquad x_2 = \dot{y},\qquad x_3 = \ddot{y}
$$

得状态方程：

$$
\begin{cases}
\dot{x}_1 = x_2\\
\dot{x}_2 = x_3\\
\dot{x}_3 = -6x_1 - 11x_2 - 6x_3 + 6u
\end{cases}
$$

**标准形式**（$\dot{x} = Ax + Bu,\ y = Cx$）：

$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\end{bmatrix}
=
\begin{bmatrix}0 & 1 & 0\\ 0 & 0 & 1\\ -6 & -11 & -6\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
+
\begin{bmatrix}0\\ 0\\ 6\end{bmatrix}u,
\qquad
y = \begin{bmatrix}1 & 0 & 0\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
$$

（本例题给出的系统矩阵 $A = \begin{bmatrix}0&1&0\\0&0&1\\-6&-11&-6\end{bmatrix}$ 在第45页特征值讨论中被再次引用。）

### 情形（二）：$n$ 阶线性微分方程中包含输入 $u$ 的导数（Scenario (2)）

$n$ 阶线性微分方程的一般形式为：

$$
y^{(n)} + a_1 y^{(n-1)} + \cdots + a_{n-1}\dot{y} + a_n y
= b_0 u^{(n)} + b_1 u^{(n-1)} + \cdots + b_{n-1}\dot{u} + b_n u
$$

**参照情形（一）的直观尝试**：若仍令

$$
x_1 = y,\quad x_2 = \dot{y},\quad \cdots,\quad x_n = y^{(n-1)}
$$

则最后一个状态方程为

$$
\dot{x}_n = y^{(n)} = -a_1x_n - a_2 x_{n-1} - \cdots - a_n x_1 + b_0 u^{(n)} + b_1 u^{(n-1)} + \cdots + b_n u
$$

**问题：状态方程中仍含有输入 $u$ 的导数项，这是不合理的（INCONSEQUENCE，不合理）。**

**状态变量选取的原则**：在用一阶微分方程组表示的状态方程中，**任何微分方程都不能包含输入（作用）函数的导数项**。

**分析（为什么不能直接取输出 $y$ 及其导数为状态）**：若输入 $u$ 为有界阶跃信号（Step Function），则 $u'$ 为脉冲函数 $\delta$，$u^{(i)}\ (i=2,3,\dots)$ 为高阶脉冲函数，状态轨迹将在 $t_0$ 时刻发生**无限跳跃**。因此，不能取输出 $y$ 及其导数为系统的状态变量——这样的一组"状态变量"不能由已知的输入与初始状态确定系统未来的状态。

> **对策思路**：必须通过适当的组合（微分方程经积分后重排）引入新的状态变量，把输入导数吸收进状态定义之中，使状态方程只含 $u$（与 $u$ 的积分）。具体操作见例 Ex.9-6。

### 例 Ex.9-6：双输入—双输出二阶系统的状态空间描述（第18~20页）

> 某 2 输入 / 2 输出二阶系统的方程组为（系数均为字母符号参数 $a$、$b$，输入 $u_1$、$u_2$，输出 $y_1$、$y_2$；其中第一式含输入导数的耦合项）：

$$
\ddot{y}_1 = -a_1\dot{y}_1 - a_2 y_1 + b_1u_1 + b_2u_2 + b_3\dot{u}_2 \ \text{型结构项}
$$

$$
\ddot{y}_2 = -a_3\dot{y}_2 - a_4 y_2 + b_4u_1 + b_4u_2\ \text{型结构项}
$$

（系数下标以课件原式为准确；该例的作用在于演示"输入导数项存在时"的多变量建模法，故未取具体数值。）

**求解要点（"先解最高阶导数，再积分组合定义状态"法）：**

1. **解出最高阶导数**：将 $y_1$、$y_2$ 的最高阶导数分别写成右端各项的组合：
   $$
   \ddot{y}_1 = -a_1\dot{y}_1 - a_2y_1 + (\text{含 } u_1,u_2,\dot u \text{ 的各项}),\qquad
   \ddot{y}_2 = -a_3\dot{y}_2 - a_4y_2 + (\text{含 } u_1,u_2 \text{ 的各项})
   $$
2. **对两边积分**：把包含输入及其导数的积分组合与输出、输出导数的组合重新合并，选为新的状态变量，使得所得状态方程中不再出现 $\dot{u}$ 等输入导数。
3. 由 $y_1$ 方程取 $x_1$（取 $x_1 = y_1$），再取另一状态变量 $x_2 = \dot{y}_1 - \displaystyle\int(\text{输入导数项})\,dt$（即把输入导数项"吸收"到状态中）——课件中具体把这类积分—组合量定义为 $x_2$；由 $y_2$ 方程取 $x_3$，最终得到一组关于 $x_1,x_2,x_3$ 的一阶状态方程：
   $$
   \begin{cases}
   \dot{x}_1 = -a_1 x_1 + b_1u_1 + b_1x_2 + \cdots\ \text{（按课件结构）}\\[4pt]
   \dot{x}_2 = -a_2 x_1 + b_3u_1 + b_4u_2 + \cdots\\[4pt]
   \dot{x}_3 = -a_3 x_1 - a_3x_2 + \cdots
   \end{cases}
   $$
4. **写成矩阵形式** $\dot{x} = Ax + Bu$、$y = Cx$（$A$ 为 $3\times 3$，$B$ 为 $3\times 2$）：
   $$
   \begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\end{bmatrix}
   = A\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
   + B\begin{bmatrix}u_1\\ u_2\end{bmatrix},
   \qquad
   \begin{bmatrix}y_1\\ y_2\end{bmatrix}
   = \begin{bmatrix}1 & 0 & 0\\ 0 & 1 & 0\end{bmatrix}
   \begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
   $$
   输出矩阵方程中 $y_1 = x_1$、$y_2 = x_2$（$A$、$B$ 中各元素为 $a$、$b$ 系数的具体组合，以课件图中积分—求和—连线的结构为准，可直接由上述积分组合核对）。

> **要点**：多输入多输出时方法完全一样，只是状态维数与 $A,B,C,D$ 的维数按"方程总阶数（消去输入导数后所需的积分器数）"确定；本系统最终用 3 个状态变量即可无输入导数地描述。

---

## 9.3.3 由系统的传递函数建立状态空间表达式

本小节含两大方向（第38页对比图）：

- **传递函数 $\rightarrow$ 状态空间**：即系统的**实现（realization）**过程——复杂且**不唯一**；
- **状态空间 $\rightarrow$ 传递函数**：简单且**唯一**。

> 状态空间（动态方程）既描述系统的输入—输出关系，又描述系统的内部状态变量；传递函数只描述输入—输出关系。

### 1. 传递函数到状态空间（Transfer Functions to State Space）

#### （a）引入中间变量 $E(s)$ 的一般方法（第22~24页）

一般 $n$ 阶系统的传递函数：

$$
\frac{Y(s)}{U(s)} = \frac{b_0 s^{n} + b_1 s^{n-1} + \cdots + b_{n-1}s + b_n}{s^{n} + a_1 s^{n-1} + \cdots + a_{n-1}s + a_n}
$$

引入中间量 $E(s)$，令：

$$
E(s) = \frac{U(s)}{s^{n} + a_1 s^{n-1} + \cdots + a_{n-1}s + a_n},
\qquad
Y(s) = \big(b_0 s^{n} + b_1 s^{n-1} + \cdots + b_{n-1}s + b_n\big) E(s)
$$

**选取状态变量**（$e(t)$ 及其各阶导数）：

$$
x_1 = e(t),\qquad x_2 = \dot{e}(t),\qquad \cdots,\qquad x_n = e^{(n-1)}(t)
$$

状态方程：

$$
\begin{cases}
\dot{x}_1 = x_2\\
\dot{x}_2 = x_3\\
\quad\vdots\\
\dot{x}_n = -a_n x_1 - a_{n-1}x_2 - \cdots - a_1 x_n + u
\end{cases}
$$

输出方程（将 $y = b_0e^{(n)} + b_1e^{(n-1)} + \cdots + b_n e$ 代入并整理）：

$$
y = b_0 u + (b_1 - a_1b_0)\,x_n + (b_2 - a_2b_0)\,x_{n-1} + \cdots + (b_n - a_nb_0)\,x_1
$$

写成矩阵形式：

$$
\dot{x} = Ax + Bu,\qquad y = Cx + b_0 u
$$

$$
A = \begin{bmatrix}
0 & 1 & 0 & \cdots & 0\\
0 & 0 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \ddots & \vdots\\
0 & 0 & 0 & \cdots & 1\\
-a_n & -a_{n-1} & -a_{n-2} & \cdots & -a_1
\end{bmatrix},
\qquad
B = \begin{bmatrix}0\\ \vdots\\ 0\\ 1\end{bmatrix},
$$

$$
C = \begin{bmatrix}b_n - a_nb_0,\ \ b_{n-1} - a_{n-1}b_0,\ \ \cdots,\ \ b_1 - a_1b_0\end{bmatrix}
$$

> **注意**：若 $b_0 = 0$（真分式，分子次数低于分母），则输出方程将简化——无非零直馈项 $b_0 u$。课件留作业：与前面"由微分方程建模"（情形一/情形二）的方法相互比较，两种取法对应同一类友矩阵实现。

#### 例 Ex.9-7：传递函数化为状态空间（第25页）

某控制系统的传递函数为：

$$
\frac{Y(s)}{U(s)} = \frac{s^2 + 4s + 1}{s^3 + 9s^2 + 8s}
$$

（即 $b_0=0,\ b_1=1,\ b_2=4,\ b_3=1$；$a_1=9,\ a_2=8,\ a_3=0$）

**解：** 状态方程：

$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\end{bmatrix}
=
\begin{bmatrix}0 & 1 & 0\\ 0 & 0 & 1\\ 0 & -8 & -9\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
+
\begin{bmatrix}0\\ 0\\ 1\end{bmatrix}u
$$

输出方程：

$$
y = \begin{bmatrix}1 & 4 & 1\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
$$

#### （b）传递函数的并联分解（Parallel Connection）——无重根情形（第26~28页）

设 $G(s)$ 分母 $Den(s)=0$ 有 $n$ 个特征根 $p_1,\dots,p_n$（互异，即系统特征方程 $Den(s)=0$ 无重根），则 $G(s)$ 可部分分式展开为 $n$ 项之和：

$$
G(s) = \frac{Y(s)}{U(s)} = \sum_{i=1}^{n}\frac{c_i}{s - p_i}
$$

其中 $c_i$ 称为极点 $p_i$ 的**留数（Residue）**：

$$
c_i = \lim_{s\to p_i}(s - p_i)G(s)
$$

并联结构（图(a)：原传递函数串联结构示意；图(b)：并联连接结构）：系统相当于 $n$ 个一阶惯性环节并联，各环节互不影响。

取各积分器输出为状态变量，则图(b)的状态方程为：

$$
\dot{x}_i = p_i x_i + u,\qquad i = 1,2,\dots,n
$$

输出方程：

$$
y = \sum_{i=1}^{n} c_i x_i
$$

**矩阵表示：**

$$
\dot{x} = \begin{bmatrix}p_1 & & & 0\\ & p_2 & & \\ & & \ddots & \\ 0 & & & p_n\end{bmatrix}x + \begin{bmatrix}1\\ 1\\ \vdots\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}c_1 & c_2 & \cdots & c_n\end{bmatrix}x
$$

> **PS（特别提示）**：此时系统矩阵 $A$ 为**对角矩阵（diagonal matrix）**，状态变量之间完全解耦——这正是"对角标准型"实现的来源。

#### （c）并联分解——有重根情形（第29~32页）

若 $G(s)$ 分母 $Den(s)=0$ 有重根，设 $p_1$ 为唯一的 $q$ 重根，则 $G(s)$ 展开为：

$$
G(s) = \sum_{i=1}^{q}\frac{c_{1i}}{(s-p_1)^{i}} + \sum_{j=q+1}^{n}\frac{c_j}{s - p_j}
$$

其中 $i = 1,2,\dots,q$（重根各项），$j = q+1,\dots,n$（其余互异单根各项）。

并联结构图变为：对应 $p_1$ 的 $q$ 个环节**链式串联后再并联**到其余 $n-q$ 个单根环节上（第30页图）。

取图中积分项的输出为状态变量，则系统矩阵 $A$ 为**约当标准型（Jordan Standard Form）**（第31~32页）：$q$ 重根对应一个 $q\times q$ 的约当块（对角元为 $p_1$、上副对角元为 1），其余互异根对应对角元。

#### 例 Ex.9-8：并联分解示例（第33页）

> 求下列系统的并联连接实现（课件给出其传递函数，具体分母展开数值见课件图）：先对分母求特征根并分解（$Den(s)$ 分解），再按留数公式 $c_i = \lim\limits_{s\to p_i}(s-p_i)G(s)$ 求部分分式系数，画出各一阶环节并联的结构图，取积分器输出为状态即得并联实现状态方程（系统矩阵为对角或约当标准型）。

#### （d）传递函数的串联分解（Serialization，第34~37页）

设分母（极点多项式）与分子（零点多项式）均可因式分解：

$$
Den(s) = \prod_{i=1}^{n}(s - p_i),\qquad Num(s) = b_0\prod_{j=1}^{m}(s - z_j)
$$

其中 $z_j\ (j=1,\dots,m)$ 为 $G(s)$ 的 $m$ 个**零点**，$p_i\ (i=1,\dots,n)$ 为 $n$ 个**极点**，则：

$$
G(s) = \frac{b_0\prod_{j=1}^{m}(s-z_j)}{\prod_{i=1}^{n}(s-p_i)}
$$

若取 $m = n-1$，则系统可看作 $n$ 个一阶环节的串联（图(a)）：

$$
G(s) = b_0\cdot\frac{s-z_1}{s-p_1}\cdot\frac{s-z_2}{s-p_2}\cdots\frac{s-z_{n-1}}{s-p_{n-1}}\cdot\frac{1}{s-p_n}\ \text{型结构}
$$

其中每个含零点的环节可重组为图(b)所示的"反馈积分器 + 直通比例"结构：

$$
\frac{s-z}{s-p} = 1 + \frac{p-z}{s-p}
$$

即每环节 = 比例直通 + 惯性积分器（带反馈 $p$、前馈增益 $p-z$）。把系统结构框图按图(b)重组后，取各积分器的输出为所需的状态变量，即可由各加法点的 I/O 关系写出系统状态方程与矩阵表示（第36~37页）：状态方程为链式一阶方程组，$A$ 为以各一阶环节极点为主对角元的链式（上双对角/约当型）结构矩阵，输入经首环节进入，输出由末环节（或按首环节直通项）合成。

> **要点**：并联分解与串联分解分别给出"对角/约当标准型实现"与"链式（串联）实现"，二者都是由传递函数实现状态空间的常见途径，再次说明**实现不唯一**。

### 2. 状态空间到传递函数（State Space to Transfer Functions）

#### （a）SISO 系统：状态空间 → 传递函数（第39页）

SISO 系统的状态空间表达式：

$$
\dot{x} = Ax + Bu,\qquad y = Cx + Du
$$

其中 $x\in R^{n}$、$x\dot{}\in R^n$、$A\in R^{n\times n}$、$B\in R^{n\times 1}$、$C\in R^{1\times n}$，$D$ 为标量。

设初始条件为零，取拉普拉斯变换：

$$
sX(s) = AX(s) + BU(s) \ \Longrightarrow\  X(s) = (sI - A)^{-1}BU(s)
$$

$$
Y(s) = CX(s) + DU(s) = \big[C(sI-A)^{-1}B + D\big]U(s)
$$

**传递函数为：**

$$
G(s) = \frac{Y(s)}{U(s)} = C(sI - A)^{-1}B + D
$$

#### 例 Ex.9-8（原课件此页沿用了"Ex.9-8"编号，与其后的例 9-8 编号重复，系原稿编号，此处照录）：状态空间 → 传递函数（第40~41页）

已知系统状态空间表达式为：

$$
\dot{x} = \begin{bmatrix}0 & 1\\ -2 & -3\end{bmatrix}x + \begin{bmatrix}0\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}1 & 0\end{bmatrix}x
$$

**解：** 先写出相关矩阵 $[A,\ B,\ C]$：

$$
A = \begin{bmatrix}0 & 1\\ -2 & -3\end{bmatrix},\qquad
B = \begin{bmatrix}0\\ 1\end{bmatrix},\qquad
C = \begin{bmatrix}1 & 0\end{bmatrix}
$$

求 $(sI - A)$ 及其逆：

$$
sI - A = \begin{bmatrix}s & -1\\ 2 & s+3\end{bmatrix},
\qquad
(sI - A)^{-1} = \frac{1}{(s+1)(s+2)}
\begin{bmatrix}s+3 & 1\\ -2 & s\end{bmatrix}
$$

传递函数：

$$
G(s) = C(sI-A)^{-1}B
= \frac{1}{(s+1)(s+2)}
\begin{bmatrix}1 & 0\end{bmatrix}
\begin{bmatrix}s+3 & 1\\ -2 & s\end{bmatrix}
\begin{bmatrix}0\\ 1\end{bmatrix}
= \frac{1}{(s+1)(s+2)}
$$

> **要点**：$(sI-A)^{-1}$ 的分母多项式即 $A$ 的特征多项式，因此**系统极点 = $A$ 的特征值**；传递函数的极点由特征方程 $|sI-A|=0$ 决定。

#### （b）MIMO 系统：状态空间 → 传递函数矩阵（第42~43页）

多输入多输出系统动态方程与 SISO 形式完全相同，只是矩阵维数不同：

$$
\dot{x} = Ax + Bu,\qquad y = Cx + Du
$$

其中 $x\in R^n$、$u\in R^r$、$y\in R^m$，且 $A\in R^{n\times n}$、$B\in R^{n\times r}$、$C\in R^{m\times n}$、$D\in R^{m\times r}$。

拉普拉斯变换得**传递函数矩阵（Transfer Function Matrix）**：

$$
G(s) = \frac{Y(s)}{U(s)} = C(sI - A)^{-1}B + D,\qquad G(s)\in R^{m\times r}
$$

（$y_1,\dots,y_m$ 为系统输出信号，$u_1,\dots,u_r$ 为输入信号，$x_1,\dots,x_n$ 为状态变量。）

#### 例 Ex.9-9：MIMO 系统的传递函数矩阵（第44页）

已知动态方程为：

$$
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\end{bmatrix}
=
\begin{bmatrix}-2 & 0\\ 1 & 0\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\end{bmatrix}
+
\begin{bmatrix}1 & 0\\ 0 & 1\end{bmatrix}
\begin{bmatrix}u_1\\ u_2\end{bmatrix},
\qquad
\begin{bmatrix}y_1\\ y_2\end{bmatrix}
=
\begin{bmatrix}1 & 0\\ 0 & 1\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\end{bmatrix}
$$

（$B = C = I_2$，$D = 0$）

**解：** 写出各矩阵 $A = \begin{bmatrix}-2 & 0\\ 1 & 0\end{bmatrix}$，$B = I_2$，$C = I_2$，$D = 0$。

$$
sI - A = \begin{bmatrix}s+2 & 0\\ -1 & s\end{bmatrix},
\qquad
(sI - A)^{-1} = \frac{1}{s(s+2)}
\begin{bmatrix}s & 0\\ 1 & s+2\end{bmatrix}
$$

传递函数矩阵：

$$
G(s) = C(sI - A)^{-1}B + D
= \frac{1}{s(s+2)}
\begin{bmatrix}s & 0\\ 1 & s+2\end{bmatrix}
= \begin{bmatrix}
\dfrac{1}{s+2} & 0\\[8pt]
\dfrac{1}{s(s+2)} & \dfrac{1}{s}
\end{bmatrix}
$$

> **要点**：MIMO 的传递"函数"是 $m\times r$ 矩阵，各元素均为有理函数；计算方法与 SISO 完全一致。

#### （c）系统矩阵 $A$ 的特征方程与特征值（第45页）

系统的**特征方程为：**

$$
\det(\lambda I - A) = |\lambda I - A| = 0
$$

将行列式展开得多项式：

$$
|\lambda I - A| = \lambda^n + a_1\lambda^{n-1} + \cdots + a_{n-1}\lambda + a_n = 0
$$

求解该方程即得 $A$ 的 $n$ 个**特征值（eigenvalues）**，特征值是方程的解之一。

**例如：**

$$
A = \begin{bmatrix}0 & 1 & 0\\ 0 & 0 & 1\\ -6 & -11 & -6\end{bmatrix}
$$

则

$$
|\lambda I - A| =
\begin{vmatrix}\lambda & -1 & 0\\ 0 & \lambda & -1\\ 6 & 11 & \lambda+6\end{vmatrix}
= \lambda^3 + 6\lambda^2 + 11\lambda + 6
= (\lambda+1)(\lambda+2)(\lambda+3) = 0
$$

3 个特征值为 $-1$、$-2$、$-3$。

> **要点**：矩阵 $A$ 的特征值 = 系统的极点（模态），决定系统自由运动的基本形态；该例 $A$ 与例 Ex.9-4 相同。

---

## 9.3.4 由系统的状态变量图建立状态空间表达式（第46~48页）

**状态变量图（State variable diagram）定义**：由积分环节、比例环节与求和符号组成的状态变量关系图（是状态空间表达式的图解描述）。

- **每个积分环节的输出即系统的一个状态变量**；
- 积分环节个数 = 状态变量个数（系统的阶数）。

### 例 Ex.9-10：由闭环传递函数绘制状态变量图并求状态空间表达式（第47~48页）

系统的闭环传递函数为：

$$
\frac{Y(s)}{U(s)} = \frac{s^2 + 3s + 2}{s^3 + 7s^2 + 12s}
$$

**解：** 把闭环传递函数改写。令中间量 $E(s)$，设：

$$
U(s) = \big(s^3 + 7s^2 + 12s\big)E(s),\qquad
Y(s) = \big(s^2 + 3s + 2\big)E(s)
$$

即

$$
s^3E(s) = U(s) - 7s^2E(s) - 12sE(s)
$$

取拉氏反变换（时域形式）：

$$
\dddot{e}(t) = u(t) - 7\ddot{e}(t) - 12\dot{e}(t)
$$

$$
y(t) = \ddot{e}(t) + 3\dot{e}(t) + 2e(t)
$$

据此绘制状态变量图：用三个积分器串联实现 $E(s)$（首积分器输入端为 $u - 7\ddot e - 12\dot e$ 的和成点），$y$ 由 $\ddot e,\dot e, e$ 按系数 $1,3,2$ 加权求和得到。

取三个积分器的输出为状态变量（$x_1 = e$，$x_2 = \dot e$，$x_3 = \ddot e$），得状态空间表达式：

$$
\begin{cases}
\begin{bmatrix}\dot{x}_1\\ \dot{x}_2\\ \dot{x}_3\end{bmatrix}
=
\begin{bmatrix}0 & 1 & 0\\ 0 & 0 & 1\\ 0 & -12 & -7\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
+
\begin{bmatrix}0\\ 0\\ 1\end{bmatrix}u \\[10pt]
y = \begin{bmatrix}2 & 3 & 1\end{bmatrix}
\begin{bmatrix}x_1\\ x_2\\ x_3\end{bmatrix}
\end{cases}
$$

> **要点**：闭环传递函数先按分母"提出" $E(s)$，分子多项式系数决定了 $C$ 阵（$y = 2x_1 + 3x_2 + x_3$），分母多项式系数决定了反馈加权（$-12\dot e - 7\ddot e$ 等）——这就是"由传递函数出发画状态变量图"的标准步骤。

---

## 9.3.5 状态空间的线性变换（Linear Transformation of State Space）

### 建立方法回顾与变换动机（第49、54页）

- 已学的状态空间方程建立方法：物理机理 / 微分方程 / 传递函数 / 状态变量图；
- **状态变量的选取不唯一** → **状态空间方程不唯一**；
- 同一物理系统不同状态空间表达式中**独立状态变量的个数一致**；
- 不同状态空间表达式之间的联系：**线性变换**。

虽然同一系统满足非奇异线性变换的状态空间方程有无穷多种，但只有少数几类**标准型（canonical form）**对分析和设计有益：

- **能控标准型（Controllability Canonical Form）**；
- **能观标准型（Observability Canonical Form）**；
- **对角标准型（Diagonal Canonical Form）**；
- **约当标准型（Jordan Canonical Form）**。

### 状态空间变量的非唯一性与线性变换定义（第50~51页）

设有一状态空间方程：

$$
\dot{x} = Ax + Bu
$$

对状态变量作线性变换，把 $x_1,x_2,\dots,x_n$ 变换成另一组状态变量 $\bar{x}_1,\bar{x}_2,\dots,\bar{x}_n$：

$$
\begin{cases}
\bar{x}_1 = p_{11}x_1 + p_{12}x_2 + \cdots + p_{1n}x_n\\
\bar{x}_2 = p_{21}x_1 + p_{22}x_2 + \cdots + p_{2n}x_n\\
\quad\vdots\\
\bar{x}_n = p_{n1}x_1 + p_{n2}x_2 + \cdots + p_{nn}x_n
\end{cases}
$$

即

$$
\bar{x} = Px,\qquad
P = \begin{bmatrix}
p_{11} & p_{12} & \cdots & p_{1n}\\
p_{21} & p_{22} & \cdots & p_{2n}\\
\vdots & \vdots & \ddots & \vdots\\
p_{n1} & p_{n2} & \cdots & p_{nn}
\end{bmatrix}
$$

若 $P$ 为**非奇异（非奇异）常数矩阵**（$|P|\ne 0$），则 $\bar{x}$ 同样是系统的状态变量向量。

**证明**（由 $\bar{x} = Px$ 即 $x = P^{-1}\bar{x}$）：

$$
\dot{\bar{x}} = P\dot{x} = PAx + PBu = PA\,P^{-1}\bar{x} + PBu
$$

记

$$
\bar{A} = P A P^{-1},\qquad \bar{B} = P B
$$

则

$$
\dot{\bar{x}} = \bar{A}\bar{x} + \bar{B}u
$$

**结论**：对任一控制系统，状态变量的选取不唯一；凡满足"变换矩阵 $P$ 非奇异"条件的线性变换得到的状态变量，都是系统的合适状态变量。

> **注**：课件采用的记号约定为 $\bar{x} = Px$（$P$ 为变换矩阵）。相应地 $\bar{A} = P A P^{-1}$、$\bar{B} = PB$、$\bar{C} = C P^{-1}$；而在"由 $A$ 化对角/约当"时取 $P$ 的列（或按第63页以特征向量为列）满足 $AP = P\Lambda$，使 $P^{-1}AP = \Lambda$，形式等价。文中公式均按课件中"对偶形式"$\bar{A} = P^{-1}AP$ 或 $PAP^{-1}$ 书写处已核对等价关系（详见第60~61页汇总框：$\bar{A}=P^{-1}AP,\ \bar{B}=P^{-1}B,\ \bar{C}=CP,\ \bar{D}=D$ 与 $x=P\bar{x}$ 的组合）。

### 线性变换的不变性（Invariability，第52~53页）

**(1) 特征方程与特征值的保持**

若 $\bar{x} = Px$（$P$ 非奇异），则变换后的系统 $\bar{A} = PA P^{-1}$ 与 $A$ 相似，其特征多项式相同：

$$
|\lambda I - \bar{A}| = |\lambda I - P A P^{-1}|
= |P(\lambda I - A)P^{-1}|
= |P|\cdot|\lambda I - A|\cdot|P^{-1}|
= |\lambda I - A|
$$

分析结论：**非奇异线性变换前后系统特征值不变**（同 $A_1$ 与 $A$ 为相似矩阵）。故对系统：

$$
\dot{x} = Ax + Bu,\quad y = Cx + Du,\qquad \bar{x} = Px
$$

有

$$
\dot{\bar{x}} = P A P^{-1}\bar{x} + P B u,\qquad
y = C P^{-1}\bar{x} + D u
$$

**(2) 传递函数矩阵的不变性**

变换后系统的传递函数矩阵：

$$
G'(s) = \bar{C}(sI - \bar{A})^{-1}\bar{B} + D
= CP^{-1}\big(sI - P A P^{-1}\big)^{-1}PB + D
$$

$$
= CP^{-1}\big[P(sI - A)P^{-1}\big]^{-1}PB + D
= CP^{-1}P(sI - A)^{-1}P^{-1}PB + D
= C(sI - A)^{-1}B + D = G(s)
$$

结论：**非奇异线性变换前后系统的传递函数（矩阵）不变**。

**等价系统与等价变换（第60~61页）**
- 满足变换关系 $\{A,B,C,D\}$ 与 $\{\bar A,\bar B,\bar C,\bar D\}$ 的系统称为**相似系统（Similar Systems）**；
- 相应的动态方程称为**等价动态方程（Equivalent Dynamic Equations）**；
- 该线性变换称为**等价变换（Equivalent Transformation）**。

总流程：

$$
\dot{x} = Ax + Bu,\ y = Cx + Du \xrightarrow{\ \bar{x} = Px\ }
\begin{cases}
\dot{\bar{x}} = \bar{A}\bar{x} + \bar{B}u\\[2pt]
y = \bar{C}\bar{x} + \bar{D}u
\end{cases}
\qquad
\begin{cases}
\bar{A} = PA P^{-1},\ \bar{B} = PB,\ \bar{C} = C P^{-1},\ \bar{D} = D\\[2pt]
\text{（等价写法：} x = P\bar{x},\ \bar{A} = P^{-1}AP,\ \bar{B}=P^{-1}B,\ \bar{C}=CP,\ \bar{D}=D\text{）}
\end{cases}
$$

### 常用线性变换方法：把 $A$ 化为标准型（第62~74页）

非奇异变换的目的：**把系统矩阵 $A$ 化为标准型**（能控、能观、对角、约当）。

#### (1) 化 $A$ 为对角形（Transform A to Diagonal Form，第62~66页）

**(a) 设 $A$ 有 $n$ 个互异的实特征值 $\lambda_1,\lambda_2,\dots,\lambda_n$**，满足特征方程：

$$
\det(\lambda I - A) = |\lambda I - A| = 0
$$

则可选非奇异变换矩阵 $P$，使

$$
P^{-1}AP = \begin{bmatrix}
\lambda_1 & & & 0\\
& \lambda_2 & &\\
& & \ddots &\\
0 & & & \lambda_n
\end{bmatrix}
$$

$P$ 由 $n$ 个实特征向量组成：

$$
P = \begin{bmatrix}p_1 & p_2 & \cdots & p_n\end{bmatrix}
$$

各特征向量满足方程：

$$
Ap_i = \lambda_i p_i,\qquad \text{或}\qquad (\lambda_i I - A)p_i = 0
$$

#### 例 Ex.9-11：把状态方程化为对角形（第64~66页）

已知

$$
\dot{x} = \begin{bmatrix}1 & 0 & -5\\ 0 & 1 & -4\\ 0 & 0 & 2\end{bmatrix}x + \begin{bmatrix}0\\ 0\\ 1\end{bmatrix}u
$$

**解：** 特征方程

$$
\det(\lambda I - A) = (\lambda - 1)(\lambda - 1)(\lambda - 2) = (\lambda-1)^2(\lambda-2) = 0
$$

3 个特征值为 $\lambda_1 = 1$、$\lambda_2 = 1$（二重根，但对应二维特征子空间）、$\lambda_3 = 2$。

分别求解 $(\lambda_i I - A)p_i = 0$：

- $\lambda_3 = 2$：由
  $$
  (2I - A)p_3 = \begin{bmatrix}1 & 0 & 5\\ 0 & 1 & 4\\ 0 & 0 & 0\end{bmatrix}p_3 = 0
  \ \Longrightarrow\ p_3 = \begin{bmatrix}-5\\ -4\\ 1\end{bmatrix}
  $$
- $\lambda_1 = \lambda_2 = 1$：$A$ 的前两列主元对应取 $p_1 = \begin{bmatrix}1\\0\\0\end{bmatrix}$、$p_2 = \begin{bmatrix}0\\1\\0\end{bmatrix}$。

变换矩阵

$$
P = \begin{bmatrix}p_1 & p_2 & p_3\end{bmatrix}
= \begin{bmatrix}1 & 0 & -5\\ 0 & 1 & -4\\ 0 & 0 & 1\end{bmatrix}
$$

于是

$$
P^{-1}AP = \begin{bmatrix}1 & 0 & 0\\ 0 & 1 & 0\\ 0 & 0 & 2\end{bmatrix}
$$

输入矩阵也作相应变换 $\bar{b} = P^{-1}b$：

$$
\bar{b} = P^{-1}\begin{bmatrix}0\\0\\1\end{bmatrix}
= \begin{bmatrix}5\\4\\1\end{bmatrix}
$$

变换后系统（对角标准型）：

$$
\dot{\bar{x}} = \begin{bmatrix}1 & 0 & 0\\ 0 & 1 & 0\\ 0 & 0 & 2\end{bmatrix}\bar{x}
+ \begin{bmatrix}5\\4\\1\end{bmatrix}u
$$

> **要点**：$A$ 能否对角化取决于是否存在 $n$ 个线性无关的特征向量；本例特征值 1 虽为二重根但其特征子空间维数为 2，仍可对角化。

#### (2) 化能控系统为能控标准型（第67~74页）

单输入线性时不变系统状态方程的**能控标准型**：

$$
\dot{x} = \begin{bmatrix}
0 & 1 & 0 & \cdots & 0\\
0 & 0 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \ddots & \vdots\\
0 & 0 & 0 & \cdots & 1\\
-a_n & -a_{n-1} & -a_{n-2} & \cdots & -a_1
\end{bmatrix}x
+ \begin{bmatrix}0\\ \vdots\\ 0\\ 1\end{bmatrix}u
$$

对应的**能控性矩阵**

$$
S = \begin{bmatrix}b & Ab & A^2b & \cdots & A^{n-1}b\end{bmatrix}
$$

是主对角线元素为 1 的**右下三角矩阵（Right Lower Triangular matrix）**。因此 $\det S \ne 0$，系统能控；此时称 $A,b$ 为能控标准型（能控性矩阵满秩正是系统完全能控的判据，详见 9.5 节）。

**一般能控系统的化标准方法**：设动态系统

$$
\dot{x} = Ax + bu
$$

若其 $A,b$ 不是能控标准型，可经适当变换化到能控标准型。执行变换（$P$ 为待定非奇异阵）：

$$
x = P^{-1}z\ \text{（即} z = Px\text{）}
$$

得

$$
\dot{z} = P A P^{-1}z + P b\,u
$$

**变换矩阵 $P$ 的求法（以行向量 $\tilde p_1$ 为出发点）：**

设 $P = \begin{bmatrix}\tilde p_1\\ \tilde p_2\\ \vdots\\ \tilde p_n\end{bmatrix}$（$\tilde p_i$ 为行向量），$P$ 应满足 $P A P^{-1} = A_c$（能控标准型），即 $P A = A_c P$，等价于行向量递推关系：

$$
\tilde p_1 A = \tilde p_2,\qquad \tilde p_2 A = \tilde p_3,\qquad \cdots,\qquad
\tilde p_n A = -a_n\tilde p_1 - a_{n-1}\tilde p_2 - \cdots - a_1\tilde p_n
$$

即

$$
\tilde p_1 A^{k} = \tilde p_{k+1}\quad (k = 1,\dots,n-1)
$$

再由 $P b$ 为能控标准型的输入列 $e_n = [0,\dots,0,1]^T$ 得（利用 $P = \begin{bmatrix}\tilde p_1\\ \tilde p_1A\\ \vdots\\ \tilde p_1A^{n-1}\end{bmatrix}$）：

$$
\begin{bmatrix}\tilde p_1\\ \tilde p_1A\\ \vdots\\ \tilde p_1A^{n-1}\end{bmatrix}b
=
\begin{bmatrix}\tilde p_1 b\\ \tilde p_1Ab\\ \vdots\\ \tilde p_1 A^{n-1}b\end{bmatrix}
= \begin{bmatrix}0\\ \vdots\\ 0\\ 1\end{bmatrix}
$$

即

$$
\tilde p_1 \begin{bmatrix}b & Ab & \cdots & A^{n-1}b\end{bmatrix}
= \tilde p_1 S = \begin{bmatrix}0 & \cdots & 0 & 1\end{bmatrix}
$$

**因此 $\tilde p_1$ 是能控性矩阵 $S$ 的逆矩阵 $S^{-1}$ 的最后一（第 $n$）行**。

**化能控标准型的步骤（$P^{-1}$ 即为化标准变换阵，按课件记号）：**
1. 求能控性矩阵 $S = \begin{bmatrix}b & Ab & \cdots & A^{n-1}b\end{bmatrix}$；
2. 求逆矩阵
   $$
   S^{-1} = \begin{bmatrix}
   s_{11} & s_{12} & \cdots & s_{1n}\\
   s_{21} & s_{22} & \cdots & s_{2n}\\
   \vdots & \vdots & \ddots & \vdots\\
   s_{n1} & s_{n2} & \cdots & s_{nn}
   \end{bmatrix}
   $$
3. 取出 $S^{-1}$ 的最后一（第 $n$）行构成向量
   $$
   \tilde p_1 = \begin{bmatrix}s_{n1} & s_{n2} & \cdots & s_{nn}\end{bmatrix}
   $$
4. 构造矩阵
   $$
   P = \begin{bmatrix}\tilde p_1\\ \tilde p_1 A\\ \vdots\\ \tilde p_1 A^{n-1}\end{bmatrix}
   $$
5. 则 $P$（或依记号取 $P^{-1}$）即为把非标准型化为能控标准型的变换矩阵。

> **要点**：能控标准型变换完全由 $(A,b)$ 确定，不依赖 $C$；能控性矩阵满秩是变换可行的前提（能观标准型的化法与之对偶，可参照第56页能观标准型形式）。

### SISO 系统由传递函数直接给出的标准型（第75~79页）

给定传递函数（一般 $m<n$，$b_0 = 0$ 或提取直馈项）：

$$
G(s) = \frac{Y(s)}{U(s)} = \frac{b_1 s^{n-1} + b_2 s^{n-2} + \cdots + b_{n-1}s + b_n}{s^n + a_1s^{n-1} + \cdots + a_{n-1}s + a_n}
$$

系统状态空间描述 $\dot{x} = Ax + Bu,\ y = Cx$，可依变换矩阵 $P$ 化成所需标准型。下列标准型可直接写出：

**(1) 能控标准型（Controllability Canonical Form）**

$$
\dot{x} = \begin{bmatrix}
0 & 1 & 0 & \cdots & 0\\
0 & 0 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \ddots & \vdots\\
0 & 0 & 0 & \cdots & 1\\
-a_n & -a_{n-1} & \cdots & -a_1
\end{bmatrix}x
+ \begin{bmatrix}0\\ \vdots\\ 0\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}b_n - a_n b_0 & \cdots & b_2 - a_2b_0 & b_1 - a_1b_0\end{bmatrix}x + b_0u
$$

**(2) 能观标准型（Observability Canonical Form）**——能控标准型的对偶：

$$
\dot{x} = \begin{bmatrix}
0 & 0 & \cdots & 0 & -a_n\\
1 & 0 & \cdots & 0 & -a_{n-1}\\
\vdots & \vdots & \ddots & \vdots & \vdots\\
0 & 0 & \cdots & 1 & -a_1
\end{bmatrix}x
+ \begin{bmatrix}b_n - a_n b_0\\ \vdots\\ b_2 - a_2b_0\\ b_1 - a_1b_0\end{bmatrix}u,
\qquad
y = \begin{bmatrix}0 & 0 & \cdots & 0 & 1\end{bmatrix}x
$$

> **注**：课件第55、56、76、77 页的标准型公式与此一致：能观标准型中 $C = [0\ \cdots\ 0\ 1]$，输入矩阵列为"分子修正系数"，$A = A_c^T$。

**(3) 对角标准型（Diagonal Canonical Form，极点互异时，第57~58、78页）**

若分母多项式 $Den(s)=0$ 的根（极点）互异：$\lambda_i = -p_i\ (i=1,\dots,n)$（$p_i$ 为正时极点位于 $s = -p_i$），传递函数展开为部分分式：

$$
G(s) = \frac{b_1 s^{n-1} + \cdots + b_n}{s^n + a_1s^{n-1} + \cdots + a_n}
= b_0 + \sum_{i=1}^{n}\frac{c_i}{s + p_i}\ \text{型（$c_i$ 为留数）}
$$

**对角标准型（I）：** 取状态变量 $x_i$ 使 $X_i(s) = \dfrac{U(s)}{s + p_i}$ 型（各状态方程独立）：

$$
\dot{x} = \begin{bmatrix}
-p_1 & & & 0\\
& -p_2 & &\\
& & \ddots &\\
0 & & & -p_n
\end{bmatrix}x
+ \begin{bmatrix}1\\ 1\\ \vdots\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}c_1 & c_2 & \cdots & c_n\end{bmatrix}x
$$

**对角标准型（II）：** 也可选取状态变量使

$$
X_i(s) = \frac{c_i}{s + p_i}U(s)
$$

即

$$
\dot{x} = \begin{bmatrix}
-p_1 & & & 0\\
& -p_2 & &\\
& & \ddots &\\
0 & & & -p_n
\end{bmatrix}x
+ \begin{bmatrix}c_1\\ c_2\\ \vdots\\ c_n\end{bmatrix}u,
\qquad
y = \begin{bmatrix}1 & 1 & \cdots & 1\end{bmatrix}x
$$

（$X_i(s)$ 求和给出 $Y(s)$，即输出是各状态之和。）

**(4) 约当标准型（Jordan Canonical Form，存在重根时，第59、79页）**

若分母有重根，例如 3 个重根 $p_1$（$s = -p_1$ 三重极点）而其余极点互异，则 $q\times q$ 的对角元为 $-p_1$、上副对角元为 1 的子块

$$
J_1 = \begin{bmatrix}
-p_1 & 1 & 0 & \cdots & 0\\
0 & -p_1 & 1 & \cdots & 0\\
\vdots & \vdots & \vdots & \ddots & \vdots\\
0 & 0 & \cdots & -p_1 & 1\\
0 & 0 & \cdots & 0 & -p_1
\end{bmatrix}
$$

称为**约当块（Jordan Block）**。整个系统矩阵 $A$ 为约当标准型（约当块按重根排布 + 互异根对角元），部分分式展开为

$$
G(s) = \frac{c_{11}}{(s+p_1)} + \frac{c_{12}}{(s+p_1)^2} + \frac{c_{13}}{(s+p_1)^3} + \cdots + \sum_{j=4}^{n}\frac{c_j}{s + p_j}\ \text{型结构}
$$

状态方程为（三重根对应链式三状态，其余为单状态）：

$$
\dot{x} = \begin{bmatrix}
-p_1 & 1 & 0 & & & 0\\
0 & -p_1 & 1 & & &\\
0 & 0 & -p_1 & & &\\
& & & -p_4 & &\\
& & & & \ddots &\\
0 & & & & & -p_n
\end{bmatrix}x + Bu,\qquad
y = \begin{bmatrix}c_{11} & c_{12} & \cdots & c_n\end{bmatrix}x
$$

（$B$、$C$ 的具体结构依留数 $c_{1i}$ 的选取而定，见第79页图式：重根链第一个积分器接受输入。）

### 例 Ex.9-12：同一传递函数的能控标准型、能观标准型与对角标准型（第80~81页）

某系统传递函数为：

$$
\frac{Y(s)}{U(s)} = \frac{s+3}{s^2 + 3s + 2} = \frac{s+3}{(s+1)(s+2)}
$$

**解：**（比较系数：$n=2$，$b_1 = 1$、$b_2 = 3$，$a_1 = 3$、$a_2 = 2$，$b_0 = 0$）

**① 能控标准型：**

$$
\dot{x} = \begin{bmatrix}0 & 1\\ -2 & -3\end{bmatrix}x
+ \begin{bmatrix}0\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}3 & 1\end{bmatrix}x
$$

**② 能观标准型**（能控标准型的对偶）：

$$
\dot{x} = \begin{bmatrix}0 & -2\\ 1 & -3\end{bmatrix}x
+ \begin{bmatrix}3\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}0 & 1\end{bmatrix}x
$$

**③ 对角标准型：** 先求留数：

$$
\frac{s+3}{(s+1)(s+2)} = \frac{c_1}{s+1} + \frac{c_2}{s+2},
\qquad
c_1 = \frac{s+3}{s+2}\Big|_{s=-1} = 2,\qquad
c_2 = \frac{s+3}{s+1}\Big|_{s=-2} = -1
$$

取对角形式（I）($A$ 为对角阵，$B = [1\ 1]^T$，$C$ 为留数行）：

$$
\dot{x} = \begin{bmatrix}-1 & 0\\ 0 & -2\end{bmatrix}x
+ \begin{bmatrix}1\\ 1\end{bmatrix}u,
\qquad
y = \begin{bmatrix}2 & -1\end{bmatrix}x
$$

（若采用对角形式（II），则为 $\dot{x} = \operatorname{diag}(-1,-2)x + \begin{bmatrix}2\\ -1\end{bmatrix}u$，$y = [1\ 1]x$，二者等价。）

> **要点**：同一传递函数对应三种不同（但相似）的状态空间实现，再次印证"实现不唯一"；三种形式的极点都是 $-1$、$-2$（特征值不变性），传递函数矩阵不变。

---

## 知识点小结（考试要点）

1. **五条建立状态空间表达式的途径**：物理机理、微分方程、传递函数、状态变量图、线性变换（能控/能观/对角/约当标准型）。
2. **机理建模**（Ex.9-2、Ex.9-3）：按牛顿定律列微分方程 → 取独立储能元件特征量（位移—速度、$i_L$、$u_C$ 等）为状态 → 写 $\dot{x}=Ax+Bu$、$y=Cx+Du$；n 个独立储能元件对应 n 个独立状态变量。
3. **由微分方程建模、输入不含导数**（情形一）：取 $x_1=y,\dots,x_n=y^{(n-1)}$，$A$ 为友矩阵、$B=[0\cdots 0\ b]^T$、$C=[1\ 0\cdots 0]$；**输入含导数时不能这样取状态**（阶跃输入导数产生 $\delta$ 脉冲，状态轨迹在 $t_0$ 无限跳变），必须经"积分—组合"把输入导数吸收进新状态变量。
4. **由传递函数到状态空间（实现）**：
   - 中间量 $E(s)$ 法：$E = U/Den(s)$，$x_1=e,\dots,x_n=e^{(n-1)}$；输出含修正系数 $(b_i - a_ib_0)$，$b_0\ne 0$ 时有直馈项；
   - **并联分解**：无重根 → 留数 $c_i=\lim_{s\to p_i}(s-p_i)G(s)$，$A$ 为对角阵；有 $q$ 重根 → $A$ 为约当标准型（约当块），状态解耦/准解耦；
   - **串联分解**：零极点因式分解后按一阶环节串联实现（$\frac{s-z}{s-p} = 1+\frac{p-z}{s-p}$），$A$ 呈链式结构。
5. **状态空间到传递函数**：$G(s) = C(sI-A)^{-1}B + D$（SISO 标量）；$G(s)\in R^{m\times r}$ 为传递函数矩阵（MIMO）；运算前提为零初始条件。该方向简单且唯一，TF→SS 方向复杂且不唯一。
6. **特征方程与特征值**：$|\lambda I - A| = 0$ 展开为 $n$ 次多项式，解出 $n$ 个特征值（如 $A=\begin{bmatrix}0&1&0\\0&0&1\\-6&-11&-6\end{bmatrix}$ → $\lambda = -1,-2,-3$）；特征值即系统极点。
7. **状态变量图**：积分器输出 = 状态变量；由闭环传递函数反推 $E(s)$（分母）与 $Y(s)$（分子），分子系数给 $C$ 阵、分母系数给反馈回路（Ex.9-10）。
8. **线性变换**：$\bar{x} = Px$（$P$ 非奇异）；$\bar{A}=PAP^{-1},\ \bar B=PB,\ \bar C=CP^{-1},\ \bar D=D$（或对偶写法）；变换后**特征值不变、传递函数矩阵不变**（不变性）；相似系统/等价动态方程。
9. **化对角形**：$P=[p_1\cdots p_n]$ 由特征向量组成，$P^{-1}AP = \operatorname{diag}(\lambda_i)$（$n$ 个线性无关特征向量才可对角化，重根但特征子空间足够亦可，Ex.9-11）。
10. **化能控标准型**：能控性矩阵 $S=[b\ Ab\ \cdots\ A^{n-1}b]$ 满秩（系统能控）时，$P^{-1}$ 由 $S^{-1}$ 的最后一行 $\tilde p_1$ 及 $\tilde p_1A,\dots,\tilde p_1A^{n-1}$ 行构成；能观标准型为能控标准型之对偶。
11. **由传递函数直接写标准型**：能控型（$B=e_n$、$C$ 含 $b_i-a_ib_0$）、能观型（$C=e_n^T$、$B$ 为修正系数列）、对角型（$A=\operatorname{diag}$，$B=[1\cdots1]^T$、$C$=留数行，或对偶形式）、约当型（重根对应约当块）。Ex.9-12 同一 $G(s)=\frac{s+3}{(s+1)(s+2)}$ 的三种实现必须熟练掌握。
