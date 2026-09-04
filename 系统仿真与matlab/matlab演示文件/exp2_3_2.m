clear
clc
z=peaks;
plot(z)
y=1:length(peaks);
plot(z,y)

t=0:pi/100:2*pi;
y=[sin(t);cos(t)];
y1=y';
plot(t,y,'r^')
hold on
plot(t,y1,'b*');
