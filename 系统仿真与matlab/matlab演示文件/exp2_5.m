%绘制单位圆
clear
close all
clc
%定义时间范围
t=[0:0.01:2*pi];
x=sin(t);
y=cos(t);
plot(x,y)
axis([-1.5 1.5 -1.5 1.5])
%限定x轴和y轴的显示范围
grid on
axis('equal') %将x坐标轴和y坐标轴的单位刻度大小调整为一样
axis('tight') %指定坐标轴填满已有的数据范围
axis('fill') %填满位置矩形
axis('equal','tight')