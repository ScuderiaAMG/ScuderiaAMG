# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 09:09:27 2025

@author: admin
"""
# 求解带约束的优化问题
from scipy.optimize import minimize

fun = lambda x: (x[0] - 1)**2 + (x[1] - 2.5)**2 #以匿名函数定义目标函数
bounds = ((0, None), (0, None))
constraints = [
  {'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
  {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
  {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2}
  ]
x0 = (5.0, 0.0)
result = minimize(fun = fun, x0 = x0,
                  method = 'SLSQP', bounds = bounds,
                  constraints = constraints)

print(result.x)