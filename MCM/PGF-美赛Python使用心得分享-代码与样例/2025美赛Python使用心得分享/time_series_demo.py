# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 07:59:30 2024

@author: admin
"""

import pandas as pd
###  读取航空公司乘客数据
df = pd.read_csv('AirPassengers.csv',
                 parse_dates = [0],#把第一列转化成Python的时间类型变量
                 index_col = 0)#把第一列作为行索引，是做时间序列分析的必要步骤

from matplotlib.pylab import rcParams
#统一设置画图的尺寸
rcParams['figure.figsize'] = (10, 4) 
import matplotlib.pylab as plt

########## 可视化原始时间序列数据
df.plot()
plt.xlabel('Month')
plt.ylabel('#Passengers')
plt.title('Monthly numbers')
plt.savefig('data.png',dpi=300)
plt.show()

########## 通过ADF检验，判断时间序列是否平稳
from statsmodels.tsa.stattools import adfuller
adf=adfuller(df, autolag='AIC')
print(f'p-value for ADF检验: {adf[1]}\n')
#### p值很大，未通过检验，说明原始序列并不平稳，设法将其
#### 转化为平稳序列，平稳序列才可以用ARIMA模型进行预测


####### 将非平稳序列转化为平稳序列的方法之一：
####### 做对数变换，使得数据最大值和最小值的差距变小
######  数据整体趋于平缓
import numpy as np
df_log = np.log(df)
df_log.plot()
plt.xlabel('Month')
plt.ylabel('log(#Passengers)')
plt.title('Monthly numbers')
plt.savefig('data1.png',dpi=300)
plt.show()

#########  做过对数变换后，p值变小，但仍未通过ADF检验
######  需要采取其他手段将数据平稳化
from statsmodels.tsa.stattools import adfuller
adf=adfuller(df_log, autolag='AIC')
print(f'p-value for ADF检验: {adf[1]}\n')

####### 采用滑动平均， 得到原始数据的基本趋势
df_log_mean = df_log.rolling(12).mean()## 将相邻12个月的数据取平均值
df_log_mean.plot()
plt.xlabel('Month')
plt.ylabel('MA(#Passengers)')
plt.title('Monthly numbers')
plt.savefig('data2.png',dpi=300)
plt.show()

#### 将基本趋势数据从原始时序数据从移除，
#### 得到的数据趋于平稳，可以看到得到的数据
#### 通过了ADF检验， 说明数据是平稳的
df_log1 = df_log - df_log_mean
df_log1.dropna(inplace=True)
df_log1.plot()
plt.xlabel('Month')
plt.ylabel('#Passengers-trend')
plt.title('Monthly numbers')
plt.savefig('data3.png',dpi=300)
plt.show()

adf=adfuller(df_log1, autolag='AIC')
print(f'p-value for ADF检验: {adf[1]}\n')
#### 将非平稳时序数据平稳化的方法除了对数变换、
#### 平滑处理外，还可以通过差分运算
#### 这里采用一阶向前差分， （如果未成功，可以
#### 尝试二阶、三阶等高阶差分）
df_log_diff = df_log - df_log.shift()
df_log_diff.plot()
plt.xlabel('Month')
plt.ylabel('Diff-#Passengers')
plt.title('Monthly numbers')
plt.savefig('data4.png',dpi=300)
plt.show()
df_log_diff.dropna(inplace=True)
####  差分过后，p值明显变下，序列变平稳了一些
adf=adfuller(df_log_diff, autolag='AIC')
print(f'p-value for ADF检验: {adf[1]}\n')


####  之前，为了平稳化，我们从原始时序数据减去了
#### 趋势数据，实际上，还可以进一步减去周期性变化
#### 的数据
#### 下面利用seasonal_decompose对原始时序数据
#### 进行分解， 依次分解为趋势数据、 周期性（季节性）数据
#### 和残差数据。  
from statsmodels.tsa.seasonal import seasonal_decompose
decomposition =seasonal_decompose(df_log,
                                  model='multiplicative',
                                  extrapolate_trend='freq')
trend = decomposition.trend
seasonal = decomposition.seasonal
residual = decomposition.resid
plt.subplot(411)
plt.plot(df_log, label='Original')
plt.legend(loc='best')
plt.subplot(412)
plt.plot(trend, label='Trend')
plt.legend(loc='best')
plt.subplot(413)
plt.plot(seasonal,label='Seasonality')
plt.legend(loc='best')
plt.subplot(414)
plt.plot(residual, label='Residuals')
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('data5.png',dpi=300)
plt.show()

###### 残差数据ADF检验的p值极小，说明
###### 残差数据是极其平稳的
adf=adfuller(residual, autolag='AIC')
print(f'p-value for ADF检验: {adf[1]}\n')


######## 下面利用ARIMA模型对残差数列进行预测
import statsmodels.api as sm

######### 利用arma_order_select_ic函数自动
##### 选择ARIMA模型的超参数
trend_evaluate = sm.tsa.arma_order_select_ic(residual, 
                                             ic=['aic', 'bic'], 
                                             trend='n', 
                                            max_ar=5,
                                            max_ma=5)
####### 两种选择准则（AIC & BIC)下的最优超参数
#### 均为p=1， q=2
print('train AIC', trend_evaluate.aic_min_order)
print('train BIC', trend_evaluate.bic_min_order)

##### 利用ARIMA(1,0,2)模型对残差序列residual
### 在训练输入1949-1至1960-12上进行预测，
### 试图考察训练误差
model = sm.tsa.arima.ARIMA(residual,order=(1,0,2))
arima_res=model.fit()
predict=arima_res.predict("1949/01/01 00:00:00","1960/12/01 00:00:00")
predict = predict * trend * seasonal
ax = predict.plot(color='r')
df_log.plot(ax =ax, color='b')
plt.legend(['y_pred', 'y_true'])
plt.savefig('data6.png',dpi=300)
plt.show()

########### 打印训练误差RSS（即残差的平方和）
RSS = np.sum((predict - df_log.iloc[:,0])**2)
print(f"RSS: {RSS}\n")
