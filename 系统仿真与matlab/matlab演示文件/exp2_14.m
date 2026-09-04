clear
clc
close all
t=-pi:0.1:pi;
trigname=input('Input trig functions name:')
switch trigname
case 'sin' 
plot(t,sin(t))
case 'cos' 
plot(t,cos(t))
otherwise
% break  %ÖÕÖ¹£¬Ìø³öswitchÓï¾ä
end
