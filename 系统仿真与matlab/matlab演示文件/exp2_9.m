%主程序exp2_9.m
clear
clc
a=input('please input value of a=');
b=input('please input value of b=');
c=sumhe(a,b)
% 在此例中，主程序exp2_9.m设定了两个参数a和b来调用
% 子程序sumhe.m(为一个函数文件)，
% 所以执行主程序时，子程序就会调用主程序传递过来的
% a和b值进行计算，再将结果返回主程序。


%子程序sumhe.m
%    function result=sumhe(a,b)
%    sumhe(a,b) sum the serial of numbers from a tob
%    result=sum(a:b);