 echo off % 不显示程序内容

clear
clc
a=4;
b=6
disp('暂停，请按任意键继续') % disp指令 可以用来显示字符
pause % 暂停，直到用户按任意键

echo on
% 显示程序内容，注意matlab默认是不显示
c=a+b
% 暂时把控制权交给键盘（在命令窗口中出现k提示符),
% 输入return，回车后退出，继续执行下面的语句。
keyboard  
        
d=input('Enter the value of d=');%提示用户输入d的值
e=a*24+b*8+d*6-c
f=e/d
disp('work pause 30 second') % disp指令可以用来显示字符
pause(10)  %暂停10秒
disp(f)  % 显示指定变量的结果，而不显示变量名称
echo off
