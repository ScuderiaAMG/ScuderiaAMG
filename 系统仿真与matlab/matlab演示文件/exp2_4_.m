close all
clc
clear
%定义时间范围
t=[0:pi/20:9*pi];
hold on     %允许在同一坐标系下绘制不同的图形
plot(t,sin(t),'r:*')
plot(t,cos(t))
plot(t,-cos(t),'k')
grid on     %在所画出的图形坐标中添加栅格，注意用在plot之后
hold off    %覆盖旧图
plot(t,-sin(t))