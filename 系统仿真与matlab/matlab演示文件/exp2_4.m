close all
clc
clear
%定义时间范围
t=[0:pi/20:9*pi];
figure(1)   %选择图像
plot(t,sin(t),'rp-.')
grid on     %在所画出的图形坐标中添加栅格，注意用在plot之后
grid off   %删除栅格
figure(2)
plot(t,cos(t))
grid on    
grid off   %删除栅格