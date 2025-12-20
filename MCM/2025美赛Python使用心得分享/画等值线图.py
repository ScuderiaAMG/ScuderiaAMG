# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 08:09:09 2025

@author: admin
"""
import matplotlib.pyplot as plt
import numpy as np

x_vec = np.linspace(-1, 1, 31)
y_vec = np.linspace(-1, 1, 31)
x_grid, y_grid = np.meshgrid(x_vec, y_vec)

z = x_grid**2 + y_grid**2

plt.contourf(x_grid, y_grid, z, 100, cmap='jet')
plt.colorbar()
plt.show()