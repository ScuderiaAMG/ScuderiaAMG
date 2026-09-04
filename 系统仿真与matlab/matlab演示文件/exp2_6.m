%图形分割命令的使用
clear
close all
clc
t=[0:pi/20:5*pi];
figure(1)
subplot(321)
plot(t,sin(t))
axis([0 16 -1.5 1.5])
xlabel('t(deg)')
ylabel('magnitude')
grid on
title('sin(t)')
subplot(322)
plot(t,-sin(t))
axis([0 16 -1.5 1.5])
xlabel('t(deg)')
ylabel('magnitude')
grid on
title('-sin(t)')
subplot(323)
plot(t,cos(t))
axis([0 16 -1.5 1.5])
xlabel('t(deg)')
ylabel('magnitude')
grid on
title('cos(t)')
subplot(324)
plot(t,-cos(t))
axis([0 16 -1.5 1.5])
xlabel('t(deg)')
ylabel('magnitude')
grid on
title('-cos(t)')
subplot(325)
subplot(326)
