# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 08:03:59 2025

@author: admin
"""

# 画线条图

import matplotlib.pyplot as plt
import numpy as np

x = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
y = np.array([1.0, 2.5, 3.2, 4.1, 6.5])


plt.plot(x, y, 'ro:', linewidth = 4, markersize=12)
plt.xlabel('x')
plt.ylabel('y')
plt.title('y~x curve')
plt.show()

plt.subplot(2,2,1)
plt.plot(x,y,'ro')
plt.subplot(2,2,2)
plt.plot(x,y,'b*')
plt.subplot(2,2,3)
plt.plot(x,y, 'cs')
plt.subplot(2,2,4)
plt.plot(x,y,'k.')
plt.tight_layout()
plt.show()