# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 08:11:07 2025

@author: admin
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


# 定义网格范围和分辨率
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
# 定义 Z 值为函数 f(X, Y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111, projection='3d')
# 绘制曲面图，设置颜色映射
surf = ax.plot_surface(X, Y, Z, cmap='viridis')
# 添加颜色条
fig.colorbar(surf)
# 设置坐标轴标签
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
plt.show()

