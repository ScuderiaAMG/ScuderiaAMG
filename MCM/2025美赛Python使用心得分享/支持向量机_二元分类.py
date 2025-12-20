# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 17:03:11 2025

@author: admin
"""

### 支持向量机做二元分类
from sklearn import svm
X = [[0, 0], [1, 1]]
y = [0, 1]
clf = svm.SVC()
clf.fit(X, y)
print(clf.predict([[2., 2.]]))


### 单棵决策树做二元分类
from sklearn import tree
X = [[0, 0], [1, 1]]
Y = [0, 1]
clf = tree.DecisionTreeClassifier()
clf = clf.fit(X, Y)
print(clf.predict([[2., 2.]]))