function y = mean(x,dim)  %函数定义行，注意函数名称必须与文件名称相同
%MEAN   Average or mean value.——H1帮助行
%   For vectors, MEAN(X) is the mean value of the elements in X. For
%   matrices, MEAN(X) is a row vector containing the mean value of
%   each column.  For N-D arrays, MEAN(X) is the mean value of the
%   elements along the first non-singleton dimension of X.——函数体说明
%
%   MEAN(X,DIM) takes the mean along the dimension DIM of X. 
%
%   Example: If X = [0 1 2
%                    3 4 5]
%
%   then mean(X,1) is [1.5 2.5 3.5] and mean(X,2) is [1
%                                                     4]
%
%   See also MEDIAN, STD, MIN, MAX, COV.

%   Copyright (c) 1984-98 by The MathWorks, Inc.
%   $Revision: 5.13 $  $Date: 1997/11/21 23:23:55 $——注解

%函数主体
if nargin==1, %nargin指函数的输入变量数；nargout指函数的输出变量数
  % Determine which dimension SUM will use
  dim = min(find(size(x)~=1));%size 求矩阵的行数与列数，find找出非零元素的索引号
  if isempty(dim), dim = 1; end

  y = sum(x)/size(x,dim);
else
  y = sum(x,dim)/size(x,dim);
end
