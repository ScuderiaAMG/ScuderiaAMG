%curve fitting of sin wave
clc
clear
x=0:0.1:2*pi; %生成样本点x
y=sin(x)+0.5*rand(size(x)); %生成样本点y，通过随机矩阵
p=polyfit(x,y,3) %拟合出多项式（3阶）
y1=polyval(p,x); %求多项式的值
plot(x,y,'+',x,y1,'-r') %绘制多项式曲线，以验证结果

