function[A,B]=myhilb(n,m)
% MYHILB 生成一个Hilbert矩阵 
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