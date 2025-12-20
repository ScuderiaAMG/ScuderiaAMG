# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 09:01:35 2025

@author: admin
"""

import numpy  as np
import matplotlib.pyplot as plt 

x = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
y = np.array([1.0, 2.5, 3.2, 4.1, 6.5])

from scipy.interpolate import interp1d

interp_fun = interp1d(x, y)

x_test = 0.266

print(interp_fun(x_test))