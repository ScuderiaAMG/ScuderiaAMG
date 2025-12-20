# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 08:28:25 2025

@author: admin
"""
import matplotlib.pyplot as plt
import numpy as np
matrix = np.random.rand(10, 10)

plt.imshow(matrix, cmap = "gray")
plt.colorbar()
plt.show()

import seaborn as sns
sns.heatmap(matrix, annot = True, cmap = "jet")
plt.show()