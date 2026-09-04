%主程序exp2_10.m
clear
clc
global a %声明变量a为全局变量
x=1:100;
a=3;
c=prods(x) %调用子程序prods.m


%子程序prods.m
%   function result=prods(x)
%   global a 
%   result=a*sum(x);
%声明了与主程序一样的全局变量a，以便在子程序中可以
%使用主程序中定义的变量