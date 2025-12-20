# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 16:32:36 2025

@author: admin
"""
from sklearn import linear_model
import numpy as np
#调用标准线性模型类， 生成模型实例
model = linear_model.LinearRegression()
# 调用模型的成员函数fit()，进行训练
model.fit([[0, 0], [1, 1], [2, 2]], [0, 1, 2])
# 给出测验点
x_test = np.array([[0.5, 0.3]])
# 调用模型的成员函数predict(),进行预测
y_test = model.predict(x_test)
print(y_test)