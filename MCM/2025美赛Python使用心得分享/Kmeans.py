# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 17:13:35 2025

@author: admin
"""
from sklearn.cluster import KMeans
import numpy as np
X = np.array([[1, 2], [1, 4], [1, 0],
               [10, 2], [10, 4], [10, 0]])
model = KMeans(n_clusters=2, random_state=0)
kmeans = model.fit(X)
print(kmeans.labels_)
print(kmeans.predict([[0, 0], [12, 3]]))
print(kmeans.cluster_centers_)
