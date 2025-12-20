

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# 读取CSV数据
raw_data = pd.read_csv("Salary_Data1.csv")
data = raw_data.values  # 将数据框转化为易于操作的矩阵
x = data[:,0].reshape((-1,1))  # 输入数据，即工作年限
y = data[:,1].reshape((-1,1))  # 输出数据，即年薪

#将数据可视化
fig = plt.figure()
plt.plot(x, y, 'r.')
plt.xlabel('Year')
plt.ylabel('Salary')
plt.savefig('Salary.png', dpi = 300)
plt.close(fig)

""" 下面我们尝试两种机器学习的模型：
   (1) 线性模型: f_hat(x; a, b) = a * x + b
   (2) 二次模型： f_hat(x; a, b, c) = a * x**2 + b * x + c
"""

""" 为了更好地比较这两个模型，我们将原始数据分成两部分：
（1） 一部分叫做“训练集”，用来确定模型的参数a,b或c；
（2） 另一部分叫做“验证集”，用来验证训练好的模型的预测精度。
"""
n = data.shape[0]  # 原始数据的个数
index = np.arange(0, n)
np.random.seed(1234)
np.random.shuffle(index)
# 训练集
x_train = x[index[0:int(n*0.7)]]
y_train = y[index[0:int(n*0.7)]]
# 验证集
x_validate = x[index[int(n*0.7):]]
y_validate = y[index[int(n*0.7):]]

fig = plt.figure()
plt.plot(x_train, y_train, 'r.', x_validate, y_validate, 'b.')
plt.savefig('data_partition', dpi=300)
plt.show()
plt.close(fig)

### 训练线性模型
A1 = np.concatenate((x_train, np.ones((int(n*0.7),1))), axis=1)
B1 = y_train
coef1 = np.linalg.solve(A1.T @ A1, A1.T @ B1)
print(f"a = {coef1[0]}, b = {coef1[1]}\n")


model = LinearRegression()
reg1 = model.fit(x_train,y_train)
print(f"软件包的结果： a = {reg1.coef_}, b = {reg1.intercept_}\n")
print(f"R2: {reg1.score(x_train,y_train)}\n")
      


### 验证线性模型
#y1_predict = x_validate * coef1[0] + coef1[1]
y1_predict = model.predict(x_validate)
err1 = np.mean((y1_predict - y_validate)**2)
print(f"线性模型的验证均方误差为 {err1}\n")

### 训练二次模型
A2 = np.concatenate((x_train**2,  
                     x_train, 
                     np.ones((int(n*0.7),1))),axis=1)
B2 = y_train
coef2 = np.linalg.solve(A2.T@ A2, A2.T @ B2)
print(f"a = {coef2[0]}, b = {coef2[1]}, c = {coef2[2]}\n")

x_train_new = np.concatenate((x_train**2, x_train),axis=1)
reg2 = LinearRegression().fit(x_train_new,y_train)
print(f"软件包的结果：a = {reg2.coef_[0][0]}, b = {reg2.coef_[0][1]}, c = {reg2.intercept_}\n")

print(f"R2: {reg2.score(x_train_new, y_train)}\n")

### 验证二次模型
y2_predict = x_validate**2 * coef2[0] + x_validate * coef2[1] + coef2[2]
err2 = np.mean((y2_predict - y_validate)**2)
print(f"二次模型的验证均方误差为 {err2}\n")


x_test = np.linspace(0, 11, 101)
y1_test = x_test * coef1[0] + coef1[1]
y2_test = x_test**2 * coef2[0] + x_test * coef2[1] + coef2[2]

fig = plt.figure()
plt.plot(x, y, 'c.', label='raw_data')
plt.plot(x_test, y1_test, 'b', label='linear model')
plt.plot(x_test, y2_test, 'r', label='quadratic model')
plt.legend()
plt.xlabel('Year')
plt.ylabel('Salary')
plt.savefig('Prediction.png', dpi = 300)
plt.close(fig)

###由于线性模型的验证误差err1 小于 二次模型的验证误差err2，故
### 我们选择线性模型

###再次训练线性模型，注意此时我们用所有的原始数据(x,y)作为训练集
A = np.concatenate((x.reshape((-1,1)), np.ones((n,1))), axis=1)
B = y.reshape((-1,1))
coef = np.linalg.solve(A.T @ A, A.T @ B)
print(f"a = {coef[0]}, b = {coef[1]}\n")

###利用训练好的线性模型，在测验集x_test上进行预测
fig = plt.figure()
y_predict = x_test * coef[0] + coef[1]
plt.plot(x, y, 'r.', label='data points')
plt.plot(x_test, y_predict, 'b',label = 'model prediction')
plt.legend()
plt.xlabel('Year')
plt.ylabel('Salary')
plt.savefig('best_model.png', dpi=300)
plt.close(fig)







