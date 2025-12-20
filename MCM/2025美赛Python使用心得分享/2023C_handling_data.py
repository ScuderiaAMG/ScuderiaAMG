# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 10:37:33 2024

@author: admin
"""

import pandas as pd
import matplotlib.pyplot as plt
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

df1 = pd.read_excel("2023C_data1.xlsx")
df2 = pd.read_excel("2023C_data2.xlsx")
###  按单品编码合并两张表
df12 = pd.merge(df1, df2, how='outer', on='单品编码')
###  将各单品每天的销售流水记录放在一组， 按单品编码排序
grouped = df12.groupby(['单品编码','销售日期'],
                       as_index=False)
###  在分好的组内计算总销量，即为各单品每天的总销量
total_sales = grouped['销量(千克)'].sum()
###  计算各单品在所有日子里的总销量
total_sales1 = total_sales.groupby(['单品编码']).sum()
### 将单品销量从高到低排序
total_sales1.sort_values(by=['销量(千克)'],ascending=False,inplace=True)


#####  依次画出总销量排名前四的单品的“销量——时间”趋势图
for i in range(4):
  df = \
  total_sales[total_sales['单品编码']==total_sales1.index[i]]
  df = df.iloc[:,1:]
  df.plot(x='销售日期',y='销量(千克)',
          kind = 'scatter',
          figsize=(14,8),
          fontsize=20)
  plt.title('单品编码: '+str(total_sales1.index[i]))
  plt.savefig('aa'+str(i)+ '.png', dpi=300)
  plt.show()


