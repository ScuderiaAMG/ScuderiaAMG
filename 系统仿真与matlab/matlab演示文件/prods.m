%子程序prods.m
function result=prods(x)
global a %声明了与主程序一样的全局变量a，以便在子程序中可以使用主程序中定义的变量
result=a*sum(x);