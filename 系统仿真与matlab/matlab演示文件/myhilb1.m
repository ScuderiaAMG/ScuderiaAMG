function[A,B]=myhilb1(n,m)
%问题：生成一个Hilbert矩阵，该矩阵是一个n×m矩阵，它的第i行
%第j列的元素为1/(i+j-1)。如果想在编写的函数中实现下面几点：
%1）如果只给出一个输入参数，则会自动生成一个方阵，即有m=n
%2）如果想返回两个参数A和B，则返回的B矩阵为A矩阵的平方，
%   即B=A'A
%3)在函数中给出合适的帮助信息，包括基本功能、调用方式
%   和参数说明

%myhilb 生成一个Hilbert矩阵 
% [A,B]=myhilb(n,m)
% where
% n,m are size of the Hilbert matrix,if only one
% argument given,then a square matrix is generated
% A is the Hilbert matrix
% B:if two matrices to be returned,B is assigned to
% A'*A
% 2001/12/1
if nargin==1,m=n;end
for i=1:n
   for j=1:m
      A(i,j)=1/(i+j-1);
   end
end
if (nargout==2),B=A'*A;end