clc
clear
sum=0;
clc
for i=1:0.5:100
   sum=sum+i;
   if i>2
      break
     % continue
     sum=sum-i
   end
end
sum
i