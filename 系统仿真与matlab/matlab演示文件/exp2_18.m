clc
clear
close
[X,Y]=meshgrid(-3:.25:3);%²úÉúX,Yµã
Z = peaks(X,Y);
[XI,YI] = meshgrid(-3:.125:3);
ZI = interp2(X,Y,Z,XI,YI);
mesh(X,Y,Z) 
hold
mesh(XI,YI,ZI+20)
hold off
axis([-4 4 -3 3 -5 25])