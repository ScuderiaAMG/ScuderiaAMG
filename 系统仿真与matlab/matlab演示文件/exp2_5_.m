%图形文字标示命令的使用
clear
close all
clc
t=[0:pi/20:5*pi];
plot(t,sin(t),'r:*')
axis([0 5*pi -1.5 1.5 ])
%给x轴和y轴命名
xlabel('t(deg)')
ylabel('magnitude')
%给图形加标题
title('sine wave from zero to 5\pi')
%在指定位置创建说明性文字
text(pi/2,sin(pi/2),'\bullet\leftarrow The sin(t) at t=2')
%输入特定的字符
%\pi 
%\alpha
%\beta
%\leftarrow
%\rightarrow
%\bullet(点号)
hold on
plot(t,cos(t))
%区分图形上不同的曲线
legend('sin(t)','cos(t)')
%用鼠标在特定位置输入文字
gtext('文字标示命令举例')
hold off

