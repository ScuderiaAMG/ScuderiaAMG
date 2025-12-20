# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 10:13:54 2025

@author: admin
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

B = pd.read_csv("BCHAIN-MKPRU.csv")
G = pd.read_csv("LBMA-GOLD.csv")
# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置为黑体
plt.rcParams['font.size'] = 15#设置字体大小为15号字
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
### 时间序列可视化
plt.figure(figsize=(14,8))
plt.plot(B['Date'], B['Value'],'r.-')
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('比特币(Bitcoin)')
plt.xticks(B['Date'][::100])
plt.gcf().autofmt_xdate() 
plt.show()

plt.figure(figsize=(14,8))
plt.plot(G['Date'], G['USD (PM)'],'b.-')
plt.xlabel('Date')
plt.ylabel('USD (PM)')
plt.title('Gold')
plt.xticks(G['Date'][::100])
plt.gcf().autofmt_xdate() 
plt.show()

# plt.figure(figsize=(14,8))
# sns.lineplot(data=B, x=B['Date'], y='Value')
# plt.xticks(B['Date'][::100])
# plt.gcf().autofmt_xdate() 
# plt.show()

#将比特币和黄金的交易价格按日期合并
# B['Date'] = pd.to_datetime(B['Date'], format='%m/%d/%y')
# G['Date'] = pd.to_datetime(G['Date'], format='%m/%d/%y')

BG = pd.merge(B, G, how="outer", on=["Date"])
##  将双休日的黄金价格取为周五的收盘价（即向前填充）
BG0 = BG.fillna(method = 'ffill', axis=0)
##首个日期无前置价格，故采用个向后填充
BG1 =  BG0.fillna(method = 'bfill', axis=0)





