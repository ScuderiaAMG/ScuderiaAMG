# 自动控制原理II —— 9.3 线性系统状态空间表达式的建立（知识点总结）

> **来源课件**：Lesson 2 9.3 State Space Establishing(3x45') - 减学时.pdf（共 59 页）
> **章节**：§9.3 State-space Establishing of Linear System（现代控制理论——状态空间模型的建立）
> **说明**：本课件例号沿用原文，其中"例 9-8"在课件中先后出现两次（并联分解实现例与状态空间→传递函数例），编号重复为课件原文如此；例 9-5、例 9-11 在该"减学时"版中被删除。

## 本节主线（总体方法，页1）

建立状态空间表达式（State-space Establishing）的五种一般途径：

1. 从系统的**物理机理**出发（From Physics Mechanism of System）
2. 从系统的**微分方程**出发（From Differential Equations of System）
3. 从系统的**传递函数**出发（From Transfer Functions of System）
4. 从系统的**状态变量图**出发（From State-variable Diagram of System）
5. 对状态空间作**线性变换**（Linear Transformation of State Space）

---

## 9.3.1 由物理机理建立状态空间表达式（页2–7）

### 方法论要点

- 用牛顿定律等物理规律列出系统的运动微分方程；
- 若已知系统的**原始位移与速度**（初始条件），则任一给定输入下系统的解即可确定——这正说明"位移 + 速度"构成足以描述系统行为的状态变量组。

### 例9-2：力—弹簧—阻尼单质量机械系统（页2–3）

由力 $F$、弹簧 $k$（spring）与阻尼器 $f$（damper）组成的机械系统，忽略重力（gravity）。$F(t)$ 为输入，$y(t)$ 为输出，$m$ 为质量。

**第一步——由牛顿定律列方程：**

$$
m \frac{d^2 y}{dt^2} + f \frac{dy}{dt} + k y = F(t)
$$

**第二步——选位移与速度为状态变量：**

$$
x_1 = y, \qquad x_2 = \dot{y} = v
$$

**第三步——写状态方程（输入 $u(t)=F(t)$）：**

$$
\begin{cases}
\dot{x}_1 = x_2 \\[4pt]
\dot{x}_2 = -\dfrac{k}{m} x_1 - \dfrac{f}{m} x_2 + \dfrac{1}{m} u
\end{cases}
$$

**状态空间表达式（State space representation）：**

$$
\boxed{\;
\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \end{bmatrix}
=
\begin{bmatrix} 0 & 1 \\ -\dfrac{k}{m} & -\dfrac{f}{m} \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \end{bmatrix}
+
\begin{bmatrix} 0 \\ \dfrac{1}{m} \end{bmatrix} u,
\qquad
y = \begin{bmatrix} 1 & 0 \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \end{bmatrix}
\;}
$$

> 系统矩阵第一行"$0,\,1$"体现了 $\dot{x}_1=x_2$ 的积分链关系；输出方程取 $y=x_1$。

### 例9-3：双质量—弹簧—阻尼机械系统（页4–5）

无重力、输入为拉力 $F$ 的两质量系统：质量 $m_1$ 与 $m_2$，输出为两质量的位移 $y_1$ 与 $y_2$；$m_1$ 经弹簧 $k_1$、阻尼 $f_1$ 连于固定端，$m_1$ 与 $m_2$ 之间以弹簧 $k_2$、阻尼 $f_2$ 相连，拉力 $F(t)$ 作用于 $m_2$。

**第一步——由牛顿定律列 $m_1$、$m_2$ 的物理关系式：**

$$
m_1 \ddot{y}_1 = -k_1 y_1 - f_1 \dot{y}_1 + k_2 (y_2-y_1) + f_2 (\dot{y}_2-\dot{y}_1)
$$

$$
m_2 \ddot{y}_2 = F(t) - k_2 (y_2 - y_1) - f_2 (\dot{y}_2 - \dot{y}_1)
$$

**第二步——选 4 个相互独立的状态变量：**

$$
x_1 = y_1, \qquad x_2 = \dot{y}_1, \qquad x_3 = y_2, \qquad x_4 = \dot{y}_2
$$

**第三步——状态方程：**

$$
\begin{cases}
\dot{x}_1 = x_2 \\[4pt]
\dot{x}_2 = -\dfrac{k_1+k_2}{m_1}\,x_1 - \dfrac{f_1+f_2}{m_1}\,x_2 + \dfrac{k_2}{m_1}\,x_3 + \dfrac{f_2}{m_1}\,x_4 \\[6pt]
\dot{x}_3 = x_4 \\[4pt]
\dot{x}_4 = \dfrac{k_2}{m_2}\,x_1 + \dfrac{f_2}{m_2}\,x_2 - \dfrac{k_2}{m_2}\,x_3 - \dfrac{f_2}{m_2}\,x_4 + \dfrac{1}{m_2}\,F(t)
\end{cases}
$$

**状态空间表达式（矩阵形式）：**

$$
\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \\ \dot{x}_3 \\ \dot{x}_4 \end{bmatrix}
=
\begin{bmatrix}
0 & 1 & 0 & 0 \\[2pt]
-\dfrac{k_1+k_2}{m_1} & -\dfrac{f_1+f_2}{m_1} & \dfrac{k_2}{m_1} & \dfrac{f_2}{m_1} \\[2pt]
0 & 0 & 0 & 1 \\[2pt]
\dfrac{k_2}{m_2} & \dfrac{f_2}{m_2} & -\dfrac{k_2}{m_2} & -\dfrac{f_2}{m_2}
\end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \\ x_4 \end{bmatrix}
+
\begin{bmatrix} 0 \\ 0 \\ 0 \\ \dfrac{1}{m_2} \end{bmatrix} F
$$

$$
\begin{bmatrix} y_1 \\ y_2 \end{bmatrix}
=
\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \\ x_4 \end{bmatrix}
$$

### 旋转（扭转）机械系统示例（页6–7，图形页）

页 6 为系统结构图；页 7 为由牛顿转动定律列出的两惯量旋转系统方程（平移量 $\to$ 转角：质量 $m\to$ 转动惯量 $J$、位移 $y\to$ 转角 $\theta$、弹簧 $k$、阻尼 $b$）：

$$
J_1 \ddot{\theta}_1 = M_c + M_D - k(\theta_1-\theta_2) - b(\dot{\theta}_1-\dot{\theta}_2)
$$

$$
J_2 \ddot{\theta}_2 = k(\theta_1-\theta_2) + b(\dot{\theta}_1-\dot{\theta}_2)
$$

其中 $M_c$、$M_D$ 为作用于 $J_1$ 上的外力矩（课件符号）。其处理思路与例9-2、例9-3 完全一致：选取转角及其角速度（$\theta_1,\dot{\theta}_1,\theta_2,\dot{\theta}_2$ 或相应独立组合）为状态变量即可写出状态空间表达式——**机理建模时状态变量取独立储能元件（惯性、弹性、阻尼）的特征物理量**。

---

## 9.3.2 由微分方程建立状态空间表达式（页9–20）

### 方法论（页9）

- 先由系统物理机理建立微分/差分方程；
- 再针对方程选取一组状态变量，建立**状态方程**；
- 依据系统输出与状态之间的关系建立**输出方程（输出函数）**。

### 状态变量的选取（页10）

- 状态变量的选取**不唯一**（selection of state variables is not unique）；
- 选取方法：
  1. 选与**初始条件**有关的变量；
  2. 选具有明确物理意义的**独立储能元件特征量**（能量或信息存储元件），例如电感电流 $i$、电容电压 $u_c$、质量（位移）与速度 $v$ 等。

### 情形（1）：$n$ 阶线性微分方程中**不含输入 $u$ 的导数**（页11–13）

设单输入单输出（SISO）控制系统的动态过程由下列方程描述（$y$ 及其导数项为输出各阶导数，$u$ 为输入）：

$$
y^{(n)} + a_1 y^{(n-1)} + \cdots + a_{n-1}\dot{y} + a_n y = b u
$$

若已知输出的初始条件 $y(0), \dot{y}(0), \ldots, y^{(n-1)}(0)$ 及 $t\ge 0$ 的输入 $u(t)$，则系统在任意时刻的行为均可确定。

**选取状态变量：**

$$
x_1 = y,\quad x_2 = \dot{y},\quad \ldots,\quad x_n = y^{(n-1)}
$$

则

$$
\begin{cases}
\dot{x}_1 = x_2 \\[2pt]
\dot{x}_2 = x_3 \\[2pt]
\quad\vdots \\[2pt]
\dot{x}_{n-1} = x_n \\[2pt]
\dot{x}_n = -a_n x_1 - a_{n-1}x_2 - \cdots - a_1 x_n + b u
\end{cases}
$$

**状态空间表达式（即能控标准型/相变量标准型）：**

$$
\dot{\boldsymbol{x}} = A\boldsymbol{x} + B u, \qquad y = C \boldsymbol{x}
$$

其中

$$
\boldsymbol{x} = \begin{bmatrix} x_1 \\ x_2 \\ \vdots \\ x_n \end{bmatrix},\qquad
A = \begin{bmatrix}
0 & 1 & 0 & \cdots & 0 \\
0 & 0 & 1 & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
0 & 0 & 0 & \cdots & 1 \\
-a_n & -a_{n-1} & \cdots & -a_2 & -a_1
\end{bmatrix},\qquad
B = \begin{bmatrix} 0 \\ \vdots \\ 0 \\ b \end{bmatrix},\qquad
C = \begin{bmatrix} 1 & 0 & 0 & \cdots & 0 \end{bmatrix}
$$

（$A$ 为友矩阵/能控标准型矩阵，$B$ 只在最后一行为 $b$，$C$ 只在首位为 1，$D=0$。）

### 状态变量图（方块图）画法（页14）

由上式可画出状态变量图（state variable diagram）：

- 每个**积分器（integrator）的输出对应一个状态变量**；
- 状态方程由各积分器输入/输出的关系确定（输入端按 $-a_1,\ldots,-a_n$ 反馈、$b u$ 前馈相加）；
- 输出方程取系统输出端部分（$y=x_1$）。

### 例9-4：无输入导数的三阶微分方程建模（页15）

设系统动态过程的微分方程为（$u$、$y$ 分别为输入、输出）：

$$
\dddot{y} + 6\ddot{y} + 11\dot{y} + 6 y = 6 u
$$

试求其状态空间表达式。

**解**：选取状态变量 $x_1=y,\ x_2=\dot{y},\ x_3=\ddot{y}$，则

$$
\dot{x}_1 = x_2,\qquad \dot{x}_2 = x_3,\qquad \dot{x}_3 = -6x_1 - 11x_2 - 6x_3 + 6u
$$

写成标准形式 $\dot{\boldsymbol{x}} = A\boldsymbol{x} + Bu,\ y = C\boldsymbol{x}$：

$$
\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \\ \dot{x}_3 \end{bmatrix}
=
\begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & 1 \\ -6 & -11 & -6 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
+
\begin{bmatrix} 0 \\ 0 \\ 6 \end{bmatrix} u,
\qquad
y = \begin{bmatrix} 1 & 0 & 0 \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
$$

### 情形（2）：$n$ 阶线性微分方程中含有输入 $u$ 的导数（页16–17）

微分方程为

$$
y^{(n)} + a_1 y^{(n-1)} + \cdots + a_{n-1}\dot{y} + a_n y
= b_0 u^{(n)} + b_1 u^{(n-1)} + \cdots + b_{n-1}\dot{u} + b_n u
$$

若仍仿照情形（1）取 $x_1=y,\ x_2=\dot{y},\ldots,\ x_n=y^{(n-1)}$（$y^{(n-1)}$ 满足的方程中将 $y^{(n)}$ 用上式代入），则状态方程中**仍然含有输入 $u$ 及其各阶导数**，这**不合理（INCONSEQUENCE）**。

**状态变量选取的原则：**

> 用一阶微分方程组表示的状态方程中，任何一个微分方程（状态方程）都不能含有输入（作用函数）$u$ 的导数。

**分析**：若输入 $u$ 是**有界阶跃信号（Step Function）**，则 $u'$ 为**脉冲函数 $\delta(t)$**，$u^{(i)}\ (i=2,3,\ldots)$ 为**高阶脉冲函数**，状态轨迹将在 $t_0$ 处发生**无穷大的跳变**。因此不能把输出 $y$ 及其导数直接取为状态变量——这样的状态变量组无法仅由已知输入与初始状态确定系统未来的状态。

### 例9-6：双输入双输出耦合系统含输入导数时的建模（页18–20）

某 2 输入/2 输出二阶系统的方程为（$u_1,u_2$ 为输入，$y_1,y_2$ 为输出）：

$$
\ddot{y}_1 + a_1 \dot{y}_1 + a_2 y_2 = b_1 \dot{u}_1 + b_2 u_1 + b_3 u_2
$$

$$
\dot{y}_2 + a_3 y_2 + a_4 y_1 = b_4 u_2
$$

试给出其状态空间描述。

**解（方法：对含输入导数的方程逐次积分、引入新状态变量以消去输入导数）**：

1. 先解出 $y_1,\ y_2$ 的最高阶导数：

$$
\ddot{y}_1 = -a_1 \dot{y}_1 - a_2 y_2 + b_1 \dot{u}_1 + b_2 u_1 + b_3 u_2,\qquad
\dot{y}_2 = -a_3 y_2 - a_4 y_1 + b_4 u_2
$$

2. 注意 $y_1$ 的方程中含有 $\dot{u}_1$，故**对两边积分**并重组，以消去输入导数：

$$
\dot{y}_1 = \int \ddot{y}_1\, dt = -a_1 y_1 + b_1 u_1 + \int\left(-a_2 \dot{y}_2 + b_2 u_1 + b_3 u_2\right) dt
$$

3. 选取状态变量（先取与输出直接对应的两个）：

$$
x_1 = y_1, \qquad x_2 = y_2
$$

4. 令积分项整体为一个新状态变量（**再选一个状态变量**）：

$$
x_3 = \int\left(-a_2 \dot{y}_2 + b_2 u_1 + b_3 u_2\right) dt
\;\Longrightarrow\;
\dot{x}_3 = -a_2 \dot{y}_2 + b_2 u_1 + b_3 u_2
$$

将 $\dot{y}_2 = -a_4 x_1 - a_3 x_2 + b_4 u_2$ 代入并整理，连同由 $y_1$ 方程得到的 $\dot{x}_1$ 式及 $y_2$ 方程，得到**状态方程方程组**：

$$
\dot{x}_1 = -a_1 x_1 + x_3 + b_1 u_1
$$

$$
\dot{x}_2 = -a_4 x_1 - a_3 x_2 + b_4 u_2
$$

$$
\dot{x}_3 = -a_2 x_2 + b_2 u_1 + b_3 u_2
$$

> 注意：课件原页 19 在推导 $x_3$ 时出现的是含 $\dot{y}_2$ 的积分式；经代入消去输入导数后的最终状态方程组以本页所示为准（其中 $x_2 = y_2$、$\dot{y}_2 = -a_4x_1-a_3x_2+b_4u_2$）。此过程正是"通过积分构造新状态变量以消除输入导数"的标准做法，与情形（2）的原则一致。

5. **矩阵形式（Rewrite the equations by the matrixes）：**

$$
\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \\ \dot{x}_3 \end{bmatrix}
=
\begin{bmatrix} -a_1 & 0 & 1 \\ -a_4 & -a_3 & 0 \\ 0 & -a_2 & 0 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
+
\begin{bmatrix} b_1 & 0 \\ 0 & b_4 \\ b_2 & b_3 \end{bmatrix}
\begin{bmatrix} u_1 \\ u_2 \end{bmatrix}
$$

**输出方程（output matrix equation）：**

$$
\begin{bmatrix} y_1 \\ y_2 \end{bmatrix}
=
\begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
$$

> 本例要点：多输入多输出系统建模方法与 SISO 相同；只要方程中含有输入导数，就必须通过"积分—定义新状态"的手段将其消去，而消去的途径可以不止一种，因此所得状态空间表达式**不唯一**（本例直接以输出为前两个状态是可行的选择）。

---

## 9.3.3 由传递函数建立状态空间表达式（页21–41）

### 1. 传递函数 → 状态空间（Transfer Functions to State Space）（页22–25）

系统的传递函数为（首一化分母）：

$$
\frac{Y(s)}{U(s)} = \frac{b_0 s^{n} + b_1 s^{n-1} + \cdots + b_{n-1}s + b_n}{s^{n} + a_1 s^{n-1} + \cdots + a_{n-1}s + a_n}
$$

引入中间变量 $E(s)$（把传递函数看作两级串联）：

$$
U(s) = \left(s^{n} + a_1 s^{n-1} + \cdots + a_{n-1}s + a_n\right) E(s)
$$

$$
Y(s) = \left(b_0 s^{n} + b_1 s^{n-1} + \cdots + b_{n-1}s + b_n\right) E(s)
$$

**选取状态变量（以 $e(t)$ 及其各阶导数为状态）：**

$$
x_1 = e(t),\quad x_2 = \dot{e}(t),\quad \ldots,\quad x_n = e^{(n-1)}(t)
$$

则由积分链关系有

$$
\dot{x}_1 = x_2,\quad \dot{x}_2 = x_3,\ \ldots,\ \dot{x}_{n-1} = x_n
$$

并且

$$
u = \dot{x}_n + a_1 x_n + a_2 x_{n-1} + \cdots + a_{n-1} x_2 + a_n x_1
$$

$$
y = b_0 \dot{x}_n + b_1 x_n + b_2 x_{n-1} + \cdots + b_{n-1} x_2 + b_n x_1
$$

**写成矩阵形式（页24）：**

$$
\dot{\boldsymbol{x}} =
\begin{bmatrix}
0 & 1 & 0 & \cdots & 0 \\
0 & 0 & 1 & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
0 & 0 & 0 & \cdots & 1 \\
-a_n & -a_{n-1} & -a_{n-2} & \cdots & -a_1
\end{bmatrix}
\boldsymbol{x}
+
\begin{bmatrix} 0 \\ \vdots \\ 0 \\ 1 \end{bmatrix} u
$$

输出方程（把 $\dot{x}_n = -a_n x_1 - \cdots - a_1 x_n + u$ 代入 $y$ 的表达式）：

$$
y = b_0\Big(-a_n x_1 - a_{n-1}x_2 - \cdots - a_1 x_n\Big) + b_0 u
+ \Big(b_n,\ b_{n-1},\ \ldots,\ b_1\Big)\boldsymbol{x}
$$

即

$$
y = \left(b_n - b_0 a_n\right)x_1 + \left(b_{n-1} - b_0 a_{n-1}\right)x_2 + \cdots
+ \left(b_1 - b_0 a_1\right)x_n + b_0 u
$$

> 若 $b_0 = 0$，输出方程将大为简化（此时 $D=b_0=0$，无输入直馈项）。此方法适用于微分方程中含有输入导数的情况；课件留作作业：与本课前"微分方程法（情形2）"进行比较。

### 例9-7：由传递函数求状态空间表达式（页25）

某控制系统传递函数为

$$
\frac{Y(s)}{U(s)} = \frac{s^2 + 4s + 1}{s^3 + 9s^2 + 8s}
$$

将其变换为状态空间表达式。

**解**：对照标准式得系数

$$
a_1 = 9,\quad a_2 = 8,\quad a_3 = 0,\quad b_0 = 0,\quad b_1 = 1,\quad b_2 = 4,\quad b_3 = 1
$$

**状态方程：**

$$
\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \\ \dot{x}_3 \end{bmatrix}
=
\begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & 1 \\ 0 & -8 & -9 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
+
\begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix} u
$$

**输出方程：**

$$
y = \begin{bmatrix} 1 & 4 & 1 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
$$

> 自检：$G(s) = C(sI-A)^{-1}B = \dfrac{s^2+4s+1}{s^3+9s^2+8s}$ ✓

### 传递函数的并联分解实现（Parallel Connection of the Transfer Function）（页26–33）

**分母与特征方程**：设 $G(s)$ 分母 $\text{Den}(s)=0$ 有 $n$ 个特征根（characteristic roots）$p_1, p_2, \ldots, p_n$：

$$
\text{Den}(s) = s^n + a_1 s^{n-1} + \cdots + a_{n-1}s + a_n = \prod_{i=1}^{n}(s - p_i)
$$

$\text{Den}(s)=0$ 即系统的**特征方程（Characteristic Equation）**。

#### （a）无重根情况（页26–28）

$G(s)$ 可分解为 $n$ 个分式之和：

$$
G(s) = \sum_{i=1}^{n} \frac{c_i}{s - p_i}
$$

其中 $c_i$ 称为极点 $p_i$ 的**留数（Residue）**：

$$
c_i = \left.(s - p_i)\,G(s)\right|_{s = p_i}
$$

- 页27 图（a）为原 $G(s)$ 方块图，图（b）为按部分分式展开后的**并联连接图**（各支路 $c_i/(s-p_i)$，无重根）；
- **图（b）的状态方程**：选各支路积分环节的输出为状态变量，则状态方程为一组互不耦合的一阶方程（各状态只含自身与输入 $u$），**输出方程为各状态按留数 $c_i$ 加权求和**；
- 其**矩阵表示**中：系统矩阵 $A$ 为**对角矩阵**（对角线元素即各极点 $p_i$，故 $A=\mathrm{diag}(p_1,p_2,\ldots,p_n)$，$B$ 为全 1 列向量或留数向量、$C$ 相应为留数行向量——具体形式取决于把留数放在输入侧还是输出侧，见 9.3.5 的对角标准型（I）与（II）两种写法）。

#### （b）有重根情况（页29–32）

若 $\text{Den}(s) = 0$ 有重根：设 $p_1$ 是唯一的 $q$ 重根（the only $q$ times repeated root），则

$$
G(s) =
\frac{c_{q}}{(s - p_1)^{q}} + \frac{c_{q-1}}{(s - p_1)^{q-1}} + \cdots + \frac{c_1}{s - p_1}
+ \sum_{j = q+1}^{n}\frac{c_j}{s - p_j}
$$

其中

$$
i = 1, 2, \ldots, q \quad(\text{重根} p_1 \text{ 的分式项}),\qquad
j = q+1, q+2, \ldots, n \quad(\text{单根} p_j \text{ 的项})
$$

- 页30 为含重根时的**并联连接图**（重根部分呈级联/链式结构）；
- **选取状态变量为图中各积分环节的输出**（页31）；
- 此时系统矩阵 $A$ 为**约当标准型（Jordan Standard Form）**（重根对应约当块 $J_q(\lambda)$，单根对应对角元），详见 9.3.5 中的约当标准型。

#### 例9-8（第一次出现）：求给定系统的并联连接实现（页33）

> （课件该例的传递函数以图/公式形式给出，文本层未能提取其具体表达式。）

- **解**：先求**分母**（因式分解出极点），作部分分式（留数）展开，再按并联连接图选取积分器输出为状态，写出**并联连接形式的状态方程**，得到对角（无重根）或约当（有重根）形式的系统矩阵 $A$。
- 与例9-7（级联"能控标准型"实现）相比，并联实现得到的是解耦的对角/约当结构，这正是后面 9.3.5 线性变换要导出的标准型。

### 2. 状态空间 → 传递函数（State Space to Transfer Functions）（页34–37）

#### 状态空间与传递函数的比较（页34）

- **状态空间**同时描述系统的**输入/输出关系**与**内部状态变量**的演化；
- **传递函数**只描述系统的**输入/输出关系**；
- 传递函数 → 状态空间：即**系统实现**（system realization）过程，较复杂且**不唯一**；
- 状态空间 → 传递函数：过程简单且**唯一**。

#### SISO 系统：状态空间 → 传递函数（页35）

设 SISO 系统的状态空间表示：

$$
\dot{\boldsymbol{x}} = A\boldsymbol{x} + Bu,\qquad y = C\boldsymbol{x} + Du
$$

其中 $\boldsymbol{x},\dot{\boldsymbol{x}} \in \mathbb{R}^{n}$，$A \in \mathbb{R}^{n\times n}$，$B \in \mathbb{R}^{n\times 1}$，$C \in \mathbb{R}^{1\times n}$，$D$ 为标量。

**假设初始条件为零**，对状态方程两边取拉氏变换：

$$
sX(s) = AX(s) + BU(s) \quad\Longrightarrow\quad X(s) = (sI - A)^{-1}BU(s)
$$

$$
Y(s) = CX(s) + DU(s)
$$

**系统的传递函数为：**

$$
\boxed{\;G(s) = \frac{Y(s)}{U(s)} = C(sI - A)^{-1}B + D\;}
$$

> 特征多项式 $|sI - A|$ 出现在分母中——状态空间与传递函数在极点信息上一致。

#### 例9-8（第二次出现）：SISO 状态空间 → 传递函数（页36–37）

已知系统的状态空间表达式：

$$
\dot{\boldsymbol{x}} =
\begin{bmatrix} 0 & 1 \\ -1 & -3 \end{bmatrix}\boldsymbol{x}
+ \begin{bmatrix} 0 \\ 1 \end{bmatrix} u,
\qquad
y = \begin{bmatrix} 1 & 0 \end{bmatrix}\boldsymbol{x}
$$

求其传递函数。

**解**：先写出相关矩阵 $[A, B, C]$：

$$
A = \begin{bmatrix} 0 & 1 \\ -1 & -3 \end{bmatrix},\qquad
B = \begin{bmatrix} 0 \\ 1 \end{bmatrix},\qquad
C = \begin{bmatrix} 1 & 0 \end{bmatrix}
$$

$$
sI - A =
\begin{bmatrix} s & 0 \\ 0 & s \end{bmatrix}
- \begin{bmatrix} 0 & 1 \\ -1 & -3 \end{bmatrix}
= \begin{bmatrix} s & -1 \\ 1 & s+3 \end{bmatrix}
$$

$$
(sI - A)^{-1} = \frac{1}{s(s+3) + 1}
\begin{bmatrix} s+3 & 1 \\ -1 & s \end{bmatrix}
$$

**传递函数：**

$$
G(s) = C(sI-A)^{-1}B
= \begin{bmatrix} 1 & 0 \end{bmatrix}
\frac{1}{s(s+3)+1}
\begin{bmatrix} s+3 & 1 \\ -1 & s \end{bmatrix}
\begin{bmatrix} 0 \\ 1 \end{bmatrix}
= \frac{1}{s^2 + 3s + 1}
$$

#### MIMO 系统：状态空间 → 传递函数矩阵（页38–39）

$r$ 个输入 $u_1,u_2,\ldots,u_r$、$n$ 个状态变量 $x_1,x_2,\ldots,x_n$、$m$ 个输出 $y_1,y_2,\ldots,y_m$ 的动态方程：

$$
\dot{\boldsymbol{x}} = A\boldsymbol{x} + B\boldsymbol{u},\qquad \boldsymbol{y} = C\boldsymbol{x} + D\boldsymbol{u}
$$

方程形式与 SISO 系统相同，只是各矩阵**维数不同**：

$$
\boldsymbol{x},\ \dot{\boldsymbol{x}} \in \mathbb{R}^{n},\quad \boldsymbol{u} \in \mathbb{R}^{r},\quad \boldsymbol{y} \in \mathbb{R}^{m}
$$

$$
A \in \mathbb{R}^{n\times n},\quad B \in \mathbb{R}^{n\times r},\quad C \in \mathbb{R}^{m\times n},\quad D \in \mathbb{R}^{m\times r}
$$

经拉氏变换，得**传递函数矩阵（Transfer Function Matrix）**：

$$
\boxed{\;G(s) = \frac{Y(s)}{U(s)} = C(sI - A)^{-1}B + D \in \mathbb{R}^{m\times r}\;}
$$

#### 例9-9：MIMO 系统求传递函数矩阵（页40）

动态方程为

$$
\dot{\boldsymbol{x}} =
\begin{bmatrix} 0 & 1 \\ 0 & -2 \end{bmatrix}\boldsymbol{x}
+ \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}\boldsymbol{u},
\qquad
\boldsymbol{y} =
\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}\boldsymbol{x}
$$

求系统的传递函数。

**解**：

$$
A = \begin{bmatrix} 0 & 1 \\ 0 & -2 \end{bmatrix},\quad
B = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix},\quad
C = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix},\quad
D = 0
$$

$$
sI - A = \begin{bmatrix} s & -1 \\ 0 & s+2 \end{bmatrix},\qquad
(sI - A)^{-1} =
\begin{bmatrix} \dfrac{1}{s} & \dfrac{1}{s(s+2)} \\[6pt] 0 & \dfrac{1}{s+2} \end{bmatrix}
$$

由于 $B = C = I$：

$$
G(s) = C(sI - A)^{-1}B = (sI - A)^{-1}
= \begin{bmatrix} \dfrac{1}{s} & \dfrac{1}{s(s+2)} \\[6pt] 0 & \dfrac{1}{s+2} \end{bmatrix}
$$

### 系统矩阵 $A$ 的特征方程与特征值（页41）

系统的**特征方程（Eigen-equation）**为

$$
|\lambda I - A| = 0
$$

展开得多项式（$n$ 阶）：

$$
\lambda^n + a_1 \lambda^{n-1} + a_2 \lambda^{n-2} + \cdots + a_{n-1}\lambda + a_n = 0
$$

解此方程即得系统的 $n$ 个**特征值（Eigenvalue）**，特征值即上述方程的根。

**例（配合例9-4 的 $A$ 矩阵）：** 设

$$
A = \begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & 1 \\ -6 & -11 & -6 \end{bmatrix}
$$

则

$$
|\lambda I - A| = 0
\ \Longrightarrow\
\lambda^3 + 6\lambda^2 + 11\lambda + 6 = 0
\ \Longrightarrow\
(\lambda + 1)(\lambda + 2)(\lambda + 3) = 0
$$

故 $A$ 的 3 个特征值为 $-1$、$-2$ 与 $-3$。

---

## 9.3.4 由状态变量图建立状态空间表达式（页42–44）

### 状态变量图的概念（页42）

- **状态变量图**：由**积分环节、比例环节与求和符号**组成的、描述状态变量之间关系的图形；
- **每个积分环节的输出就是系统的一个状态变量**；
- 由状态变量图可直接"读"出状态方程与输出方程（积分器输入端=该状态的一阶导数，输出端=该状态），因此画图过程实际上就是搭建状态空间结构的过程。

### 例9-10：由闭环传递函数画状态变量图并求状态空间（页43–44）

系统的闭环传递函数为

$$
\frac{Y(s)}{U(s)} = \frac{s^2 + 3s + 2}{s^3 + 7s^2 + 12s}
$$

画出系统的状态变量图，并求其状态空间表达式。

**解**：将闭环传递函数改写并引入中间量 $E(s)$：

$$
\frac{Y(s)}{U(s)} = \frac{s^2 + 3s + 2}{s(s^2 + 7s + 12)},\qquad
Y(s) = (s^2 + 3s + 2)\,E(s),\qquad
U(s) = (s^3 + 7s^2 + 12s)\,E(s)
$$

即

$$
s^3 E(s) = U(s) - 7s^2 E(s) - 12sE(s)
$$

对应的时域微分关系：

$$
y(t) = \ddot{e}(t) + 3\dot{e}(t) + 2e(t),\qquad
\dddot{e}(t) = u(t) - 7\ddot{e}(t) - 12\dot{e}(t)
$$

以积分器输出为状态变量（$x_1 = e,\ x_2 = \dot{e},\ x_3 = \ddot{e}$，图中依次为 $e, \dot{e}, \ddot{e}, \dddot{e}$ 的积分链），得状态空间表达式：

$$
\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \\ \dot{x}_3 \end{bmatrix}
=
\begin{bmatrix} 0 & 1 & 0 \\ 0 & 0 & 1 \\ 0 & -12 & -7 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
+
\begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix} u
$$

$$
y = \begin{bmatrix} 2 & 3 & 1 \end{bmatrix}
\begin{bmatrix} x_1 \\ x_2 \\ x_3 \end{bmatrix}
$$

> 说明：分母有因子 $s$（对应一个 0 极点），故矩阵第三行第一列为 0（$a_3 = 0$）；分子多项式系数 $2,3,1$ 直接进入输出矩阵 $C$。先画状态变量图，再由图中"每个积分器输出为一个状态变量"读出状态方程与输出方程，两者相辅相成。

---

## 9.3.5 状态空间的线性变换（页45–59）

### 回顾与结论（页45）

- 状态空间表达式建立方法回顾：物理机理 / 微分方程 / 传递函数 / 状态变量图；
- **状态变量的选取：不唯一**；
- **状态空间方程：不唯一**；
- 对同一物理系统，各状态空间表达式中**相互独立的状态变量的个数：唯一**（即系统阶数不变）；
- 不同状态空间表达式之间的联系：**线性变换（Linear Transformation）**。

### 状态空间变量的非唯一性（页46–47）

设原系统的状态空间方程为

$$
\dot{\boldsymbol{x}} = A\boldsymbol{x} + B\boldsymbol{u}
$$

将状态变量组 $(x_1, x_2, \ldots, x_n)$ 线性变换为另一组状态变量 $(\bar{x}_1, \bar{x}_2, \ldots, \bar{x}_n)$：

$$
\bar{x}_1 = p_{11} x_1 + p_{12} x_2 + \cdots + p_{1n} x_n
$$

$$
\bar{x}_2 = p_{21} x_1 + p_{22} x_2 + \cdots + p_{2n} x_n
$$

$$
\qquad\vdots
$$

$$
\bar{x}_n = p_{n1} x_1 + p_{n2} x_2 + \cdots + p_{nn} x_n
$$

即

$$
\bar{\boldsymbol{x}} = P\boldsymbol{x},\qquad
P = \begin{bmatrix} p_{11} & p_{12} & \cdots & p_{1n} \\ p_{21} & p_{22} & \cdots & p_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ p_{n1} & p_{n2} & \cdots & p_{nn} \end{bmatrix}
$$

若 $P$ 为**非奇异（non-singular）常数矩阵**（$|P|\ne 0$），则 $\bar{\boldsymbol{x}}$ 同样是该系统的一组状态变量向量。

**证明（课件记法：以 $x = P\bar{x}$ 代入，$\bar{\boldsymbol{x}} = P^{-1}\boldsymbol{x}$ 为新状态）：**

$$
\dot{\bar{\boldsymbol{x}}} = P^{-1}AP\,\bar{\boldsymbol{x}} + P^{-1}B\,\boldsymbol{u}
$$

记

$$
A_1 = P^{-1}AP,\qquad B_1 = P^{-1}B
$$

则

$$
\dot{\bar{\boldsymbol{x}}} = A_1 \bar{\boldsymbol{x}} + B_1 \boldsymbol{u}
$$

$A_1$ 与 $A$ 是**相似矩阵（similar matrices）**，其特征多项式满足

$$
|sI - A_1| = |sI - A|
$$

因此由 $\boldsymbol{x}$ 与 $\bar{\boldsymbol{x}}$ 得到的**状态方程具有相同的特征值**。

**结论（Result）**：对任意控制系统，状态变量的选取是不唯一的；任何经非奇异线性变换（满足变换矩阵非奇异条件 $|P|\ne 0$）得到的状态变量都是该系统合适的状态变量。

### 线性变换的不变性（Invariability）（页48–49）

对完整系统（$\dot{\boldsymbol{x}} = A\boldsymbol{x}+B\boldsymbol{u},\ y = C\boldsymbol{x}+D\boldsymbol{u}$），设 $\boldsymbol{x} = P\bar{\boldsymbol{x}}$，则新系统为

$$
\dot{\bar{\boldsymbol{x}}} = P^{-1}AP\,\bar{\boldsymbol{x}} + P^{-1}B\boldsymbol{u},\qquad
y = CP\,\bar{\boldsymbol{x}} + D\boldsymbol{u}
$$

#### （1）特征方程与特征值的**不变性**

变换后系统的特征方程：

$$
|\lambda I - A_1| = |\lambda I - P^{-1}AP|
= \left|\lambda P^{-1}P - P^{-1}AP\right|
= \left|P^{-1}(\lambda I - A)P\right|
= |P^{-1}|\cdot|\lambda I - A|\cdot|P|
= |\lambda I - A|
$$

**显然，非奇异线性变换前后系统的特征值完全相同**（由 $|sI-A_1| = |sI-A|$ 亦可直接看出）。

#### （2）传递函数矩阵的**不变性**

变换后系统的传递函数矩阵：

$$
G'(s) = CP\left(sI - P^{-1}AP\right)^{-1}P^{-1}B + D
$$

$$
= CP\Big(P^{-1}sIP - P^{-1}AP\Big)^{-1}P^{-1}B + D
= CPP^{-1}\big(sI - A\big)PP^{-1}B + D
= C(sI - A)^{-1}B + D = G(s)
$$

**非奇异线性变换前后，系统的传递函数（矩阵）保持不变。**

### 为什么要做线性变换（页50）

虽然同一系统可以写出**无穷多种**满足非奇异线性变换的状态空间方程，但只有少数几种**标准型（canonical forms）**对我们特别有用：

- **能控标准型（Controllability Canonical Form）**
- **能观标准型（Observability Canonical Form）**
- **对角标准型（Diagonal Canonical Form）**
- **约当标准型（Jordan Canonical Form）**

### 等价变换与系数矩阵之间的关系（页56–57）

**（1）概要**：通过等价变换 $x = P\bar{x}$，把非标准型的状态空间表达式变换为某种标准型：

$$
\dot{\boldsymbol{x}} = A\boldsymbol{x} + B\boldsymbol{u} \ \Bigg\} \quad\overset{x = P\bar{x}}{\underset{\text{等价变换}}{\Longrightarrow}}\quad
\dot{\bar{\boldsymbol{x}}} = A_1\bar{\boldsymbol{x}} + B_1\boldsymbol{u} \ \Bigg\}
y = C_1\bar{\boldsymbol{x}} + D_1\boldsymbol{u}
$$

**（2）系数矩阵之间的关系**：把 $x = P\bar{x}$（$P$ 为 $N\times N$ 非奇异常数矩阵）代入原方程：

$$
P\dot{\bar{\boldsymbol{x}}} = AP\bar{\boldsymbol{x}} + B\boldsymbol{u} \Bigg\} \ \Longrightarrow\ \left\{
\begin{aligned}
\dot{\bar{\boldsymbol{x}}} &= P^{-1}AP\,\bar{\boldsymbol{x}} + P^{-1}B\,\boldsymbol{u} \\
y &= CP\,\bar{\boldsymbol{x}} + D\boldsymbol{u}
\end{aligned}\right.
$$

$$
\boxed{\;A_1 = P^{-1}AP,\qquad B_1 = P^{-1}B,\qquad C_1 = CP,\qquad D_1 = D\;}
$$

**定义（页57）**：

- 满足上述约束关系的系统 $\{A, B, C, D\}$ 与 $\{\bar{A}, \bar{B}, \bar{C}, \bar{D}\}$ 称为**相似系统（Similar Systems）**；
- 相应的动态方程称为**等价动态方程（Equivalent Dynamic Equations）**；
- 上述线性变换称为**等价变换（Equivalent Transformation）**。

### 四种标准型（页51–55）

#### 能控标准型（页51）

$$
\begin{cases}
\dot{\boldsymbol{x}} =
\begin{bmatrix}
0 & 1 & 0 & \cdots & 0 \\
0 & 0 & 1 & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
0 & 0 & 0 & \cdots & 1 \\
-a_n & -a_{n-1} & -a_{n-2} & \cdots & -a_1
\end{bmatrix}
\boldsymbol{x} +
\begin{bmatrix} 0 \\ 0 \\ \vdots \\ 0 \\ 1 \end{bmatrix} u \\[18pt]
y = \begin{bmatrix} c_n & c_{n-1} & \cdots & c_1 \end{bmatrix}\boldsymbol{x}
\end{cases}
$$

> 系统矩阵 $A$ 亦称为**友矩阵（companion matrix）**。此型与 9.3.2/9.3.3 中"直接取 $x_1=y,\ldots$"或"取 $x_i = e^{(i-1)}$"得到的结构一致：$A$ 的右上主对角邻线为 1，末行为 $-a_n,\ldots,-a_1$；$B$ 只有末元为 1。

#### 能观标准型（页52）

$$
\begin{cases}
\dot{\boldsymbol{x}} =
\begin{bmatrix}
0 & 0 & \cdots & 0 & -a_n \\
1 & 0 & \cdots & 0 & -a_{n-1} \\
0 & 1 & \cdots & 0 & -a_{n-2} \\
\vdots & \vdots & \ddots & \vdots & \vdots \\
0 & 0 & \cdots & 1 & -a_1
\end{bmatrix}
\boldsymbol{x} +
\begin{bmatrix} b_n \\ b_{n-1} \\ b_{n-2} \\ \vdots \\ b_1 \end{bmatrix} u \\[18pt]
y = \begin{bmatrix} 0 & 0 & \cdots & 1 \end{bmatrix}\boldsymbol{x}
\end{cases}
$$

> 能观标准型与能控标准型互为"转置对偶"关系（$A$ 的 $a$ 列居最末列、其左下主对角邻线为 1；输入矩阵 $B$ 承载分子多项式系数、输出矩阵 $C$ 只有末元为 1）。

#### 对角标准型（I）——输入不分权，输出加权（页53）

$$
\begin{cases}
\dot{\boldsymbol{x}} =
\begin{bmatrix}
\lambda_1 & & & 0 \\
& \lambda_2 & & \\
& & \ddots & \\
0 & & & \lambda_n
\end{bmatrix}
\boldsymbol{x} +
\begin{bmatrix} 1 \\ 1 \\ \vdots \\ 1 \end{bmatrix} u \\[14pt]
y = \begin{bmatrix} c_1 & c_2 & \cdots & c_n \end{bmatrix}\boldsymbol{x}
\end{cases}
$$

（各状态方程为解耦的一阶方程 $\dot{x}_i = \lambda_i x_i + u$；留数信息含在输出矩阵 $C$ 中。）

#### 对角标准型（II）——输入加权，输出求和（页54）

选取状态变量：令

$$
X_i(s) = \frac{c_i}{s - \lambda_i} U(s)
$$

系统输出为

$$
Y(s) = \sum_{i=1}^{n} X_i(s)
$$

经拉氏反变换得状态空间表达式：

$$
\begin{cases}
\dot{\boldsymbol{x}} =
\begin{bmatrix}
\lambda_1 & & & 0 \\
& \lambda_2 & & \\
& & \ddots & \\
0 & & & \lambda_n
\end{bmatrix}
\boldsymbol{x} +
\begin{bmatrix} c_1 \\ c_2 \\ \vdots \\ c_n \end{bmatrix} u \\[14pt]
y = \begin{bmatrix} 1 & 1 & \cdots & 1 \end{bmatrix}\boldsymbol{x}
\end{cases}
$$

（即 $x_i$ 通道的传递函数为 $c_i/(s-\lambda_i)$，$y = \sum_i x_i$。此即"并联分解实现"在状态空间的表达。）

#### 约当标准型（页55）

以三重根 $\lambda_1$（其余为单根 $\lambda_4,\ldots,\lambda_n$）为例：

$$
\begin{cases}
\dot{\boldsymbol{x}} =
\begin{bmatrix}
\lambda_1 & 1 & 0 & & & \\
0 & \lambda_1 & 1 & & & \\
0 & 0 & \lambda_1 & & & \\
& & & \lambda_4 & & \\
& & & & \ddots & \\
& & & & & \lambda_n
\end{bmatrix}
\boldsymbol{x} +
\begin{bmatrix} 0 \\ 0 \\ 1 \\ \vdots \\ \vdots \\ 1 \end{bmatrix} u \\[20pt]
y = \begin{bmatrix} c_{11} & c_{12} & c_{13} & c_4 & \cdots & c_n \end{bmatrix}\boldsymbol{x}
\end{cases}
$$

其中重根部分的分块矩阵

$$
\begin{bmatrix} \lambda_1 & 1 & 0 \\ 0 & \lambda_1 & 1 \\ 0 & 0 & \lambda_1 \end{bmatrix}
$$

称为**约当块（Jordan Block）**；整个系统矩阵 $A$ 呈**约当标准型（Jordan Standard Form）**（约当块对应重极点，对角元对应单极点；约当块内部相邻上方元素为 1）。

> 约当标准型与页29–32"传递函数并联分解（重根情况）"的实现结果一致：重根极点对应约当块，单根极点对应对角元素。

### 例9-12：由传递函数求能控标准型、能观标准型与对角型（页58–59）

某系统传递函数为

$$
\frac{Y(s)}{U(s)} = \frac{s + 3}{s^2 + 3s + 2}
$$

试分别求其能控标准型、能观标准型与对角标准型。

**解**：分母 $s^2+3s+2 = (s+1)(s+2)$，故 $a_1 = 3,\ a_2 = 2$，特征值 $\lambda_1 = -1,\ \lambda_2 = -2$。

**能控标准型（controllability canonical form）：**

$$
\dot{\boldsymbol{x}}(t) =
\begin{bmatrix} 0 & 1 \\ -2 & -3 \end{bmatrix}
\boldsymbol{x}(t) +
\begin{bmatrix} 0 \\ 1 \end{bmatrix} u(t),
\qquad
y(t) = \begin{bmatrix} 3 & 1 \end{bmatrix}\boldsymbol{x}(t)
$$

**能观标准型（observability canonical form）：**

$$
\dot{\boldsymbol{x}}(t) =
\begin{bmatrix} 0 & -2 \\ 1 & -3 \end{bmatrix}
\boldsymbol{x}(t) +
\begin{bmatrix} 3 \\ 1 \end{bmatrix} u(t),
\qquad
y(t) = \begin{bmatrix} 0 & 1 \end{bmatrix}\boldsymbol{x}(t)
$$

**对角标准型（diagonal canonical form）：**

$$
\dot{\boldsymbol{x}}(t) =
\begin{bmatrix} -1 & 0 \\ 0 & -2 \end{bmatrix}
\boldsymbol{x}(t) +
\begin{bmatrix} 1 \\ 1 \end{bmatrix} u(t),
\qquad
y(t) = \begin{bmatrix} 2 & -1 \end{bmatrix}\boldsymbol{x}(t)
$$

> 自检（对角型）：$G(s) = \dfrac{2}{s+1} - \dfrac{1}{s+2} = \dfrac{s+3}{(s+1)(s+2)}$ ✓（2 与 $-1$ 恰为 $G(s)$ 在极点 $-1$、$-2$ 处的留数）。

---

## 知识点小结（考试要点）

1. **建立状态空间表达式的四条途径**：①物理机理（牛顿定律列微分方程，取位移、速度等储能特征量为状态）；②微分方程；③传递函数；④状态变量图（每个积分器输出 = 一个状态变量）。
2. **状态变量选择原则**：可与初始条件对应或取储能元件特征量（电感电流 $i$、电容电压 $u_c$、位移/速度等）；状态变量选取**不唯一**，但独立状态变量个数 = 系统阶数（唯一）。
3. **情形1（无输入导数）**：$x_1=y,\ldots,x_n=y^{(n-1)}$ 直接得能控标准型
   $A=\begin{bmatrix}0&1&0&\cdots&0\\ \vdots&&&&\vdots\\0&0&\cdots&0&1\\ -a_n&-a_{n-1}&\cdots&-a_2&-a_1\end{bmatrix}$，$B=[0,\cdots,0,b]^T$，$C=[1,0,\cdots,0]$（如例9-4：$A$ 末行 $[-6,-11,-6]$，$B=[0,0,6]^T$）。
4. **情形2（含输入导数）**：若仍取 $y$ 及其导数为状态，输入导数会进入状态方程——**不合理**（阶跃输入的导数会出现 $\delta$ 及高阶脉冲，状态轨迹在 $t_0$ 发生无穷大跳变）；必须通过"**先积分再定义新状态变量**"消去输入导数（见例9-6 的 $x_3 = \int(\cdots)dt$ 手法与所得 3 阶矩阵）。
5. **TF → 状态空间（E(s) 法）**：$U(s)=(\text{分母多项式})E(s)$、$Y(s)=(\text{分子多项式})E(s)$，取 $x_i = e^{(i-1)}$；输出含 $b_0u$ 直馈项 $D=b_0$，$b_0=0$ 时输出方程简化（例9-7：$G(s)=\dfrac{s^2+4s+1}{s^3+9s^2+8s}$，$A=\begin{bmatrix}0&1&0\\0&0&1\\0&-8&-9\end{bmatrix}$、$B=[0,0,1]^T$、$C=[1,4,1]$）。
6. **并联分解（部分分式）实现**：无重根 → $A$ 为**对角矩阵**（对角标准型 I/II）；有 $q$ 重根 → 对应**约当块**、$A$ 为**约当标准型**；留数 $c_i=(s-p_i)G(s)\big|_{s=p_i}$。
7. **状态空间 → 传递函数**：零初值下拉氏变换，$G(s) = C(sI-A)^{-1}B + D$（SISO），$G(s)=C(sI-A)^{-1}B+D$（MIMO，传递函数矩阵 $m\times r$）——该变换**简单且唯一**；实现问题（TF→SS）复杂且不唯一。
8. **特征方程与特征值**：$|\lambda I - A| = 0$（如 $A=\begin{bmatrix}0&1&0\\0&0&1\\-6&-11&-6\end{bmatrix}$ ⇒ $\lambda^3+6\lambda^2+11\lambda+6=0$ ⇒ 特征值 $-1,-2,-3$）。
9. **非奇异线性变换** $x=P\bar{x}$（$|P|\ne 0$）：$\bar{A}=P^{-1}AP$、$\bar{B}=P^{-1}B$、$\bar{C}=CP$、$\bar{D}=D$；变换前后**特征值与传递函数矩阵不变**（$|sI-P^{-1}AP|=|sI-A|$，$G'(s)=G(s)$）；原系统与新系统称**相似系统 / 等价动态方程 / 等价变换**。
10. **四种标准型**（考结构记忆）：能控标准型（友矩阵：1 在主对角上方邻线、$a$ 在末行，$B$ 末元 1）；能观标准型（对偶：$a$ 在末列、1 在主对角下方邻线，$C$ 末元 1）；对角标准型（特征值在对角线）；约当标准型（重根约当块 $\begin{bmatrix}\lambda&1&0\\0&\lambda&1\\0&0&\lambda\end{bmatrix}$）；例9-12 一题三型（能控：$A=\begin{bmatrix}0&1\\-2&-3\end{bmatrix},B=[0,1]^T,C=[3,1]$；能观：$A=\begin{bmatrix}0&-2\\1&-3\end{bmatrix},B=[3,1]^T,C=[0,1]$；对角：$A=\mathrm{diag}(-1,-2),B=[1,1]^T,C=[2,-1]$）。
