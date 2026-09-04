%curve interpolation
clear 
clc
close all
ys=[0 0.9 0.6 1 0 0.1 -0.3 -0.7 -0.9 -0.2]; %已有的样本点ys
xs=0:length(ys)-1;  %已有的样本点xs
x=0:0.1:length(ys)-1;%新的样本点x
y1=interp1(xs,ys,x,'nearest'); %插值产生新的样本点y1,执行速度最快，输出结果为直角转折（最近点插值法）
y2=interp1(xs,ys,x,'linear');  %插值产生新的样本点y2,默认值，在样本点上斜率变化很大（线性插值）
y3=interp1(xs,ys,x,'spline');  %插值产生新的样本点y3,最花时间，但输出结果也最平滑（样条插值）
y4=interp1(xs,ys,x,'cubic');   %插值产生新的样本点y4,最占内存，输出结果与spline差不多（立方插值）
y5=interp1(xs,ys,x,'pchip');   %插值产生新的样本点y5,保形分段三次插值
y6=interp1(xs,ys,x,'v5cubic'); %插值产生新的样本点y6,不进行外推的三次插值,，如果x不是等间隔，则使用样条插值。
hold
plot(xs,ys,'+k') %分别绘制不同方法产生的曲线
plot(x,y1,':r') %分别绘制不同方法产生的曲线
plot(x,y2,'-m') %分别绘制不同方法产生的曲线，m为洋红色
plot(x,y3,'--c') %分别绘制不同方法产生的曲线,c为蓝绿色
plot(x,y4,'--b') %分别绘制不同方法产生的曲线
plot(x,y5,'*g') %分别绘制不同方法产生的曲线
plot(x,y6,'dk') %分别绘制不同方法产生的曲线，k为黑色
hold off
plot(xs,ys,'+k',x,y1,':r',x,y2,'-m',x,y3,'--c',x,y4,'--b',x,y5,'*g',x,y6,'dk') %分别绘制不同方法产生的曲线
legend('sampled point','nearest','linear','spline','cubic','pchip','v5cubic')
