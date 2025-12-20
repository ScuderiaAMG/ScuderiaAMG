# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 16:45:34 2025

@author: admin
"""

# 1. 导入必要库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler  # SVR对数据缩放敏感，建议归一化
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
# 2. 构造非线性回归数据（y = sin(x) + 少量噪声）
np.random.seed(42)  # 固定随机种子，结果可复现
X = np.linspace(0, 10, 100).reshape(-1, 1)  # 特征X：0到10的100个点，转为二维（sklearn要求）
y = np.sin(X).flatten() + np.random.randn(100) * 0.1  # 目标y：正弦曲线+噪声

# 3. 数据归一化（SVR对特征尺度敏感，必须做！）
scaler_X = StandardScaler()  # 特征缩放器
scaler_y = StandardScaler()  # 目标值缩放器（可选，但建议做）
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

# 4. 初始化并拟合SVR模型
# kernel：核函数（linear=线性, rbf=高斯核/非线性, poly=多项式核）
# C：惩罚系数（越大拟合越贴合训练数据，易过拟合）
# gamma：RBF核的带宽（越小拟合越平滑，越大越贴合）
model = SVR(kernel='rbf', C=10, gamma=0.5)
model.fit(X_scaled, y_scaled)  # 拟合缩放后的数据

# 5. 预测（训练数据+新数据）
# 对训练数据预测（验证拟合效果）
y_pred_scaled = model.predict(X_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()  # 反归一化还原

# 对新数据预测（示例：x=10.5, 11, 11.5）
X_new = np.array([[10.5], [11], [11.5]])
X_new_scaled = scaler_X.transform(X_new)  # 用训练集的缩放器转换新数据
y_new_pred_scaled = model.predict(X_new_scaled)
y_new_pred = scaler_y.inverse_transform(y_new_pred_scaled.reshape(-1, 1)).flatten()

# 6. 输出结果
print(f"新数据 {X_new.flatten()} 的预测值: {y_new_pred.round(2)}")

# 7. 可视化：原始数据 + SVR拟合曲线 + 新预测点
plt.figure(figsize=(10, 6))
plt.scatter(X, y, label='原始数据', alpha=0.6, color='blue')  # 原始数据点
plt.plot(X, y_pred, label='SVR拟合曲线（RBF核）', color='red', linewidth=2)  # SVR拟合结果
plt.scatter(X_new, y_new_pred, label='新预测点', color='green', s=100)  # 新预测值
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.title('SVR（支持向量机回归）示例')
plt.show()
