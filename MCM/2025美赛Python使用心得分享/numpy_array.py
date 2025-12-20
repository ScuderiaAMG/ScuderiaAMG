# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 09:14:18 2023

@author: admin
"""

import numpy as np

""" 数组的创建 """

# 一维数组

x =  np.array([1.0, 2.0, 3.0] )

# 一维数组只有一个维度，也就是它的长度

print(x.shape)

#  二维数组， 也就是矩阵

y = np.array([ [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]  ])

print('y= \n', y)

# 二维数组有两个维度，分别是矩阵的行数和列数

print('Shape of array y:', y.shape)

# 将一维数组转化为二维数组

x_row = x.reshape( (1,-1) )   # 将x转化为行矩阵

x_column = x.reshape( (-1, 1)) #将x转化为列矩阵

print( ' x =', x)

print( 'x_row =', x_row)

print( 'x_column =', x_column)


""" 数组的索引 """

#索引一维数组
print('\n')
print(x[-1])

#索引二维数组
print('\n')
print('y= \n', y)
print(y[1,2])


"""数组的切片"""

# 取一维数组的部分
print('\n')
print(x[2: 0:-2])

#取二维数组的第一列

print('\n')
print(y[:,0])  
#注意y[:,0]的维度
print(y[:,0].shape)

#如何保证取出的那一列是一个列向量？
# 方法1： reshape 
print('方法1: \n', y[:,0].reshape((-1,1)))

#方法2: 用冒号
print('方法2： \n', y[:,0:1])


"""矩阵的转置、相乘、求逆、特征分解"""

# y的转置
print('y = ', y)
print('y转置:\n', y.T)

# y与y的转置相乘
print('y与y转置相乘:\n ', y @ y.T)

#方阵的求逆
# np.random.seed(1234)
z = np.random.rand(3, 3)
print('z= \n', z)

print('z的逆: \n', np.linalg.inv(z))
print('z的逆:\n', np.linalg.solve(z, np.eye(3)))


#方阵的特征值和特征向量

eig_values, eig_vectors = np.linalg.eig(z)

print('z的特征值：\n', eig_values)
print('z的特征向量：\n', eig_vectors)


"""矩阵的拼接"""

#把两个y肩并肩放置，形成一个更大的矩阵

y1 = np.concatenate( (y, y), axis=1)

print('y = \n', y)
print('y1 = \n', y1)



#把两个y上下堆叠，形成一个更大的矩阵

y2 = np.concatenate( (y, y), axis=0)

print('y = \n', y)
print('y2 = \n', y2)






