%plot绘图命令的使用
clc    %清屏命令
clear  %清除工作空间中所有变量
close all
%定义时间范围
t=[0:pi/20:9*pi];
y1=sin(t);
y2=cos(t);
plot(t,y1,'rs',t,y2,'m diamond')
plot(t)
plot(y1)
plot(y2)

y=[y1;y2];
plot(t,y)

set(gca,'xtick',[pi 2*pi 3*pi 4*pi 5*pi 6*pi 7*pi 8*pi 9*pi])