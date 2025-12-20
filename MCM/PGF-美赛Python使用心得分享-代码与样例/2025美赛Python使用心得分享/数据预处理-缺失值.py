# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 09:19:44 2025

@author: admin
"""

import pandas as pd
import numpy as np

data = pd.read_csv("Salary_Data.csv")#读入数据


# 以numpy去处理空值
data_np = data.to_numpy() #转换为numpy数组
c1, c2 = data_np[:,0:1], data_np[:,1:2] #逐列处理
#用列均值填充空值
c11 = np.nan_to_num(c1, nan=np.nanmean(c1))
c22 = np.nan_to_num(c2, nan=np.nanmean(c2))
#将填充后的列重新拼起来
data_filled = np.concatenate((c11,c22),axis=1)
#直接删除带有空值的行
data_cleared = data_np[~np.isnan(data_np).any(axis=1)]


#以pandas处理空值
c3, c4 = data['Year'], data['Salary']#逐列处理
#用列均值填充空值
c33 = c3.fillna(c3.mean())
c44 = c4.fillna(c4.mean())
#将填充后的列重新拼起来
data_filled_pd = pd.concat([c33, c44],axis=1)
#直接删除带有空值的行
data_cleared_pd = data.dropna(axis=0, how='any')


