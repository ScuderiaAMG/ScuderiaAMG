# Deep Learning in Java

一个全面的深度学习与计算机科学Java实现项目，包含从基础到高级的各种算法和概念。

## 📁 项目结构

```
deep_learning/
├── 01_basics/                    # 深度学习基础
│   ├── Perceptron.java          # 感知器实现
│   ├── ActivationFunctions.java # 激活函数集合
│   └── NeuronDemo.java          # 神经元模型演示
│
├── 02_intermediate/              # 中级深度学习
│   ├── NeuralNetwork.java       # 多层神经网络
│   ├── BackpropagationDemo.java # 反向传播算法
│   └── LossFunctions.java       # 损失函数集合
│
├── 03_advanced/                  # 高级深度学习
│   ├── CNN.java                 # 卷积神经网络
│   ├── RNN.java                 # 循环神经网络
│   └── LSTM.java                # 长短期记忆网络
│
├── 04_data_science/              # 数据科学
│   ├── DataPreprocessing.java   # 数据预处理工具
│   └── Statistics.java          # 统计学工具
│
├── 05_machine_learning/          # 机器学习
│   ├── LinearRegression.java    # 线性回归
│   ├── KNN.java                 # K近邻算法
│   └── DecisionTree.java        # 决策树
│
├── 06_reinforcement_learning/    # 强化学习
│   └── QLearning.java           # Q-Learning算法
│
├── 07_algorithms/                # 算法
│   ├── SortingAlgorithms.java   # 排序算法集合
│   └── GraphAlgorithms.java     # 图算法
│
├── 08_computer_vision/           # 计算机视觉
│   └── ImageProcessing.java     # 图像处理基础
│
├── 09_nlp/                       # 自然语言处理
│   ├── TextProcessing.java      # 文本处理
│   └── WordEmbeddings.java      # 词嵌入
│
├── 10_databases/                 # 数据库
│   └── DatabaseOperations.java  # 数据库操作
│
├── 11_software_engineering/      # 软件工程
│   ├── DesignPatterns.java      # 设计模式
│   └── TestingDemo.java         # 测试框架
│
└── 12_math_and_optimization/     # 数学与优化
    ├── MatrixOperations.java    # 矩阵运算
    └── GradientDescent.java     # 梯度下降算法
```

## 🚀 快速开始

### 编译和运行

```bash
# 进入项目目录
cd deep_learning

# 编译单个文件
javac -d out 01_basics/Perceptron.java

# 运行
java -cp out deep_learning.basics.Perceptron
```

### 使用Maven (推荐)

```xml
<build>
    <sourceDirectory>src</sourceDirectory>
</build>
```

## 📚 模块说明

### 01_basics - 深度学习基础

**感知器 (Perceptron)**
- 最简单的神经网络模型
- 支持二分类问题
- 演示学习过程

**激活函数**
- Sigmoid: 输出范围(0,1)，适合二分类
- Tanh: 输出范围(-1,1)，zero-centered
- ReLU: 最常用，解决梯度消失
- Leaky ReLU: 解决神经元死亡问题
- Softmax: 多分类输出层

**神经元模型**
- 单个神经元的计算过程
- 前向传播演示

### 02_intermediate - 中级深度学习

**多层神经网络**
- 支持任意层数和神经元数量
- ReLU隐藏层 + Sigmoid输出层
- He权重初始化

**反向传播**
- 详细的数学推导
- 梯度计算过程
- 权重更新演示

**损失函数**
- MSE (均方误差): 回归问题
- MAE (平均绝对误差): 回归问题
- Binary Cross Entropy: 二分类
- Categorical Cross Entropy: 多分类
- Huber Loss: 结合MSE和MAE

### 03_advanced - 高级深度学习

**CNN (卷积神经网络)**
- 2D卷积操作
- 最大池化/平均池化
- 多通道卷积
- ReLU激活

**RNN (循环神经网络)**
- 序列数据处理
- 隐藏状态传递
- 序列生成

**LSTM (长短期记忆网络)**
- 遗忘门、输入门、输出门
- 细胞状态
- 解决长期依赖问题

### 04_data_science - 数据科学

**数据预处理**
- Z-Score标准化
- Min-Max归一化
- 独热编码 (One-Hot)
- 标签编码 (Label Encoding)
- 缺失值处理
- 训练集/测试集分割

**统计学**
- 描述统计 (均值、方差、标准差)
- 相关性分析
- 百分位数、IQR
- 正态分布
- 偏度、峰度

### 05_machine_learning - 机器学习

**线性回归**
- 梯度下降优化
- R²评分
- 多特征支持

**KNN (K近邻)**
- 欧氏距离
- 多数投票
- 混淆矩阵

**决策树**
- ID3算法
- 信息增益
- 递归构建

### 06_reinforcement_learning - 强化学习

**Q-Learning**
- ε-贪婪策略
- Q表更新
- 网格世界示例

### 07_algorithms - 算法

**排序算法**
- 冒泡排序 O(n²)
- 选择排序 O(n²)
- 插入排序 O(n²)
- 快速排序 O(n log n)
- 归并排序 O(n log n)
- 堆排序 O(n log n)

**图算法**
- BFS (广度优先搜索)
- DFS (深度优先搜索)
- Dijkstra最短路径
- 环检测
- 拓扑排序

### 08_computer_vision - 计算机视觉

**图像处理**
- 灰度转换
- 二值化
- 图像卷积
- 均值滤波/高斯滤波
- Sobel边缘检测
- 图像旋转/缩放

### 09_nlp - 自然语言处理

**文本处理**
- 分词
- 停用词过滤
- 词干提取
- 词频统计
- TF-IDF
- N-gram
- 简单情感分析

**词嵌入**
- Word2Vec概念
- 余弦相似度
- 词向量运算

### 10_databases - 数据库

**数据库操作**
- JDBC连接
- CRUD操作
- 批量插入
- 条件查询
- 统计查询
- 事务处理

### 11_software_engineering - 软件工程

**设计模式**
- 单例模式 (Singleton)
- 工厂模式 (Factory)
- 观察者模式 (Observer)
- 策略模式 (Strategy)
- 建造者模式 (Builder)

**测试框架**
- 自定义注解
- 断言方法
- 测试运行器
- TDD演示

### 12_math_and_optimization - 数学与优化

**矩阵运算**
- 矩阵加法/减法/乘法
- 转置
- 行列式
- 逆矩阵
- Hadamard积

**梯度下降**
- 基础SGD
- 动量梯度下降
- AdaGrad
- Adam优化器

## 🎯 学习路径

### 初学者
1. 01_basics - 理解神经网络基础
2. 05_machine_learning - 学习经典ML算法
3. 07_algorithms - 掌握基本算法

### 中级
1. 02_intermediate - 深入神经网络
2. 04_data_science - 数据处理技能
3. 09_nlp - 自然语言处理入门

### 高级
1. 03_advanced - CNN/RNN/LSTM
2. 06_reinforcement_learning - 强化学习
3. 08_computer_vision - 计算机视觉

## 📖 参考资源

- Deep Learning Book (Ian Goodfellow)
- Pattern Recognition and Machine Learning
- Reinforcement Learning: An Introduction
- Java Documentation

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
