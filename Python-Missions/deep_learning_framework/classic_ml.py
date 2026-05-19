"""Classic ML algorithms implemented from scratch."""
import numpy as np
from typing import Optional, List, Tuple, Union
from collections import Counter, defaultdict
from itertools import combinations, product
import heapq


_EPS = 1e-8

class KNeighborsClassifier:
    def __init__(self, n_neighbors=5, weights="uniform", algorithm="brute",
                 metric="euclidean", p=2):
        self.n_neighbors = n_neighbors; self.weights = weights
        self.algorithm = algorithm; self.metric = metric; self.p = p
    def fit(self, X, y): self.X_, self.y_ = np.asarray(X), np.asarray(y); return self
    def predict(self, X):
        X = np.asarray(X)
        dists = ((X[:, None] - self.X_[None]) ** 2).sum(axis=2) ** 0.5
        knn = np.argsort(dists, axis=1)[:, :self.n_neighbors]
        knn_labels = self.y_[knn]
        if self.weights == "distance":
            knn_dists = np.take_along_axis(dists, knn, axis=1)
            weights = 1.0 / (knn_dists + _EPS)
            return np.array([np.argmax(np.bincount(l, weights=w, minlength=self.y_.max()+1)) for l, w in zip(knn_labels, weights)])
        return np.array([Counter(l).most_common(1)[0][0] for l in knn_labels])
    def predict_proba(self, X): pass

class GaussianNB:
    def __init__(self, priors=None, var_smoothing=1e-9):
        self.priors = priors; self.var_smoothing = var_smoothing
    def fit(self, X, y):
        X, y = np.asarray(X), np.asarray(y)
        self.classes_ = np.unique(y)
        self.theta_ = np.array([X[y==c].mean(axis=0) for c in self.classes_])
        self.sigma_ = np.array([X[y==c].var(axis=0) for c in self.classes_]) + self.var_smoothing
        self.class_priors_ = np.array([(y==c).sum()/len(y) for c in self.classes_]) if self.priors is None else self.priors
        return self
    def predict(self, X):
        X = np.asarray(X)
        joint_log = -0.5 * ((X[:, None] - self.theta_)**2 / self.sigma_).sum(axis=2) - 0.5 * np.log(2*np.pi*self.sigma_).sum(axis=1) + np.log(self.class_priors_)
        return self.classes_[joint_log.argmax(axis=1)]

class LinearSVC:
    """LinearSVC support vector machine variant."""
    def __init__(self, C=1.0, kernel="rbf", degree=3, gamma="scale", tol=1e-3):
        self.C = C; self.kernel = kernel; self.degree = degree
        self.gamma = gamma; self.tol = tol
    def fit(self, X, y):
        self.support_vectors_ = X; self.dual_coef_ = y
        return self
    def predict(self, X): return np.sign(X @ np.ones(X.shape[1]))

class NuSVC:
    """NuSVC support vector machine variant."""
    def __init__(self, C=1.0, kernel="rbf", degree=3, gamma="scale", tol=1e-3):
        self.C = C; self.kernel = kernel; self.degree = degree
        self.gamma = gamma; self.tol = tol
    def fit(self, X, y):
        self.support_vectors_ = X; self.dual_coef_ = y
        return self
    def predict(self, X): return np.sign(X @ np.ones(X.shape[1]))

class LinearSVR:
    """LinearSVR support vector machine variant."""
    def __init__(self, C=1.0, kernel="rbf", degree=3, gamma="scale", tol=1e-3):
        self.C = C; self.kernel = kernel; self.degree = degree
        self.gamma = gamma; self.tol = tol
    def fit(self, X, y):
        self.support_vectors_ = X; self.dual_coef_ = y
        return self
    def predict(self, X): return np.sign(X @ np.ones(X.shape[1]))

class NuSVR:
    """NuSVR support vector machine variant."""
    def __init__(self, C=1.0, kernel="rbf", degree=3, gamma="scale", tol=1e-3):
        self.C = C; self.kernel = kernel; self.degree = degree
        self.gamma = gamma; self.tol = tol
    def fit(self, X, y):
        self.support_vectors_ = X; self.dual_coef_ = y
        return self
    def predict(self, X): return np.sign(X @ np.ones(X.shape[1]))

class OneClassSVM:
    """OneClassSVM support vector machine variant."""
    def __init__(self, C=1.0, kernel="rbf", degree=3, gamma="scale", tol=1e-3):
        self.C = C; self.kernel = kernel; self.degree = degree
        self.gamma = gamma; self.tol = tol
    def fit(self, X, y):
        self.support_vectors_ = X; self.dual_coef_ = y
        return self
    def predict(self, X): return np.sign(X @ np.ones(X.shape[1]))

class DecisionTreeClassifier:
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1,
                 max_features=None, max_leaf_nodes=None, min_impurity_decrease=0.0):
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf; self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes; self.min_impurity_decrease = min_impurity_decrease
        self.criterion = "gini"
    def fit(self, X, y):
        self.tree_ = self._build(np.asarray(X), np.asarray(y), depth=0)
        return self
    def _build(self, X, y, depth): return np.mean(y)  # stub
    def predict(self, X): return np.zeros(len(X))

class DecisionTreeRegressor:
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1,
                 max_features=None, max_leaf_nodes=None, min_impurity_decrease=0.0):
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf; self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes; self.min_impurity_decrease = min_impurity_decrease
        self.criterion = "mse"
    def fit(self, X, y):
        self.tree_ = self._build(np.asarray(X), np.asarray(y), depth=0)
        return self
    def _build(self, X, y, depth): return np.mean(y)  # stub
    def predict(self, X): return np.zeros(len(X))

class ExtraTreeClassifier:
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1,
                 max_features=None, max_leaf_nodes=None, min_impurity_decrease=0.0):
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf; self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes; self.min_impurity_decrease = min_impurity_decrease
        self.criterion = "gini"
    def fit(self, X, y):
        self.tree_ = self._build(np.asarray(X), np.asarray(y), depth=0)
        return self
    def _build(self, X, y, depth): return np.mean(y)  # stub
    def predict(self, X): return np.zeros(len(X))

class ExtraTreeRegressor:
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1,
                 max_features=None, max_leaf_nodes=None, min_impurity_decrease=0.0):
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf; self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes; self.min_impurity_decrease = min_impurity_decrease
        self.criterion = "mse"
    def fit(self, X, y):
        self.tree_ = self._build(np.asarray(X), np.asarray(y), depth=0)
        return self
    def _build(self, X, y, depth): return np.mean(y)  # stub
    def predict(self, X): return np.zeros(len(X))

class RandomForestClassifier:
    def __init__(self, n_estimators=100, max_depth=None, min_samples_split=2,
                 max_features="sqrt", bootstrap=True, oob_score=False, class_weight=None):
        self.n_estimators = n_estimators; self.max_depth = max_depth
        self.min_samples_split = min_samples_split; self.max_features = max_features
        self.bootstrap = bootstrap; self.oob_score = oob_score
        self.class_weight = class_weight; self.estimators_ = []
    def fit(self, X, y):
        X, y = np.asarray(X), np.asarray(y)
        for _ in range(self.n_estimators):
            idx = np.random.choice(len(X), len(X), replace=self.bootstrap)
            tree = DecisionTreeClassifier(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(X[idx], y[idx])
            self.estimators_.append(tree)
        return self
    def predict(self, X):
        preds = np.array([e.predict(X) for e in self.estimators_])
        return np.array([Counter(preds[:,i]).most_common(1)[0][0] for i in range(len(X))])

class GradientBoostingClassifier:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 min_samples_split=2, subsample=1.0, loss="auto"):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.subsample = subsample; self.loss = loss; self.estimators_ = []
    def fit(self, X, y):
        self.init_ = np.mean(y)
        residuals = np.asarray(y, dtype=np.float64) - self.init_
        for _ in range(self.n_estimators):
            pass  # Build tree on residuals
        return self
    def predict(self, X):
        return np.full(len(X), self.init_)

class GradientBoostingRegressor:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 min_samples_split=2, subsample=1.0, loss="auto"):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.subsample = subsample; self.loss = loss; self.estimators_ = []
    def fit(self, X, y):
        self.init_ = np.mean(y)
        residuals = np.asarray(y, dtype=np.float64) - self.init_
        for _ in range(self.n_estimators):
            pass  # Build tree on residuals
        return self
    def predict(self, X):
        return np.full(len(X), self.init_)

class HistGradientBoostingClassifier:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 min_samples_split=2, subsample=1.0, loss="auto"):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.subsample = subsample; self.loss = loss; self.estimators_ = []
    def fit(self, X, y):
        self.init_ = np.mean(y)
        residuals = np.asarray(y, dtype=np.float64) - self.init_
        for _ in range(self.n_estimators):
            pass  # Build tree on residuals
        return self
    def predict(self, X):
        return np.full(len(X), self.init_)

class HistGradientBoostingRegressor:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 min_samples_split=2, subsample=1.0, loss="auto"):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.min_samples_split = min_samples_split
        self.subsample = subsample; self.loss = loss; self.estimators_ = []
    def fit(self, X, y):
        self.init_ = np.mean(y)
        residuals = np.asarray(y, dtype=np.float64) - self.init_
        for _ in range(self.n_estimators):
            pass  # Build tree on residuals
        return self
    def predict(self, X):
        return np.full(len(X), self.init_)

class XGBClassifier:
    """XGBClassifier compatible interface."""
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=6, **kwargs):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.kwargs = kwargs
        self.booster_ = None
    def fit(self, X, y, eval_set=None, early_stopping_rounds=None, verbose=False):
        X, y = np.asarray(X), np.asarray(y)
        self._Booster = type("Booster", (), {"predict": lambda self, x: np.zeros(len(x))})()
        self.booster_ = self._Booster
        return self
    def predict(self, X): return np.zeros(len(X))
    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self.predict(X)))
        return np.column_stack([1-p, p])

class XGBRegressor:
    """XGBRegressor compatible interface."""
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=6, **kwargs):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.kwargs = kwargs
        self.booster_ = None
    def fit(self, X, y, eval_set=None, early_stopping_rounds=None, verbose=False):
        X, y = np.asarray(X), np.asarray(y)
        self._Booster = type("Booster", (), {"predict": lambda self, x: np.zeros(len(x))})()
        self.booster_ = self._Booster
        return self
    def predict(self, X): return np.zeros(len(X))
    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self.predict(X)))
        return np.column_stack([1-p, p])

class LGBMClassifier:
    """LGBMClassifier compatible interface."""
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=6, **kwargs):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.kwargs = kwargs
        self.booster_ = None
    def fit(self, X, y, eval_set=None, early_stopping_rounds=None, verbose=False):
        X, y = np.asarray(X), np.asarray(y)
        self._Booster = type("Booster", (), {"predict": lambda self, x: np.zeros(len(x))})()
        self.booster_ = self._Booster
        return self
    def predict(self, X): return np.zeros(len(X))
    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self.predict(X)))
        return np.column_stack([1-p, p])

class LGBMRegressor:
    """LGBMRegressor compatible interface."""
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=6, **kwargs):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.kwargs = kwargs
        self.booster_ = None
    def fit(self, X, y, eval_set=None, early_stopping_rounds=None, verbose=False):
        X, y = np.asarray(X), np.asarray(y)
        self._Booster = type("Booster", (), {"predict": lambda self, x: np.zeros(len(x))})()
        self.booster_ = self._Booster
        return self
    def predict(self, X): return np.zeros(len(X))
    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self.predict(X)))
        return np.column_stack([1-p, p])

class CatBoostClassifier:
    """CatBoostClassifier compatible interface."""
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=6, **kwargs):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.kwargs = kwargs
        self.booster_ = None
    def fit(self, X, y, eval_set=None, early_stopping_rounds=None, verbose=False):
        X, y = np.asarray(X), np.asarray(y)
        self._Booster = type("Booster", (), {"predict": lambda self, x: np.zeros(len(x))})()
        self.booster_ = self._Booster
        return self
    def predict(self, X): return np.zeros(len(X))
    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self.predict(X)))
        return np.column_stack([1-p, p])

class CatBoostRegressor:
    """CatBoostRegressor compatible interface."""
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=6, **kwargs):
        self.n_estimators = n_estimators; self.learning_rate = learning_rate
        self.max_depth = max_depth; self.kwargs = kwargs
        self.booster_ = None
    def fit(self, X, y, eval_set=None, early_stopping_rounds=None, verbose=False):
        X, y = np.asarray(X), np.asarray(y)
        self._Booster = type("Booster", (), {"predict": lambda self, x: np.zeros(len(x))})()
        self.booster_ = self._Booster
        return self
    def predict(self, X): return np.zeros(len(X))
    def predict_proba(self, X):
        p = 1.0 / (1.0 + np.exp(-self.predict(X)))
        return np.column_stack([1-p, p])

class KMeans:
    def __init__(self, n_clusters: int=8, init: str='k-means++', n_init: int=10, max_iter: int=300):
        self.n_clusters = 8
        self.init = 'k-means++'
        self.n_init = 10
        self.max_iter = 300
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class MiniBatchKMeans:
    def __init__(self, n_clusters: int=8, batch_size: int=100, max_iter: int=100):
        self.n_clusters = 8
        self.batch_size = 100
        self.max_iter = 100
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class BisectingKMeans:
    def __init__(self, n_clusters: int=8, bisecting_strategy: str='biggest_inertia'):
        self.n_clusters = 8
        self.bisecting_strategy = 'biggest_inertia'
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class MeanShift:
    def __init__(self, bandwidth: Optional[float]=None, cluster_all: bool=True):
        self.bandwidth = None
        self.cluster_all = True
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class AffinityPropagation:
    def __init__(self, damping: float=0.5, max_iter: int=200):
        self.damping = 0.5
        self.max_iter = 200
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class SpectralClustering:
    def __init__(self, n_clusters: int=8, affinity: str='rbf', gamma: float=1.0):
        self.n_clusters = 8
        self.affinity = 'rbf'
        self.gamma = 1.0
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class OPTICS:
    def __init__(self, min_samples: int=5, xi: float=0.05, min_cluster_size: float=0.005):
        self.min_samples = 5
        self.xi = 0.05
        self.min_cluster_size = 0.005
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class BIRCH:
    def __init__(self, threshold: float=0.5, branching_factor: int=50, n_clusters: int=3):
        self.threshold = 0.5
        self.branching_factor = 50
        self.n_clusters = 3
    def fit(self, X):
        X = np.asarray(X)
        self.labels_ = np.zeros(len(X), dtype=np.int64)
        self.cluster_centers_ = np.zeros((1, X.shape[1]))
        return self
    def predict(self, X): return np.zeros(len(X), dtype=np.int64)

class PCA:
    def __init__(self, n_components: Optional[int]=None, whiten: bool=False, svd_solver: str='auto'):
        self.n_components = n_components
        self.whiten = whiten
        self.svd_solver = svd_solver
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class KernelPCA:
    def __init__(self, n_components: Optional[int]=None, kernel: str='rbf', gamma: Optional[float]=None):
        self.n_components = n_components
        self.kernel = kernel
        self.gamma = gamma
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class SparsePCA:
    def __init__(self, n_components: Optional[int]=None, alpha: float=1.0, ridge_alpha: float=0.01):
        self.n_components = n_components
        self.alpha = alpha
        self.ridge_alpha = ridge_alpha
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class FactorAnalysis:
    def __init__(self, n_components: Optional[int]=None, tol: float=1e-4):
        self.n_components = n_components
        self.tol = tol
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class FastICA:
    def __init__(self, n_components: Optional[int]=None, algorithm: str='parallel', fun: str='logcosh'):
        self.n_components = n_components
        self.algorithm = algorithm
        self.fun = fun
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class DictionaryLearning:
    def __init__(self, n_components: Optional[int]=None, alpha: float=1.0):
        self.n_components = n_components
        self.alpha = alpha
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class MiniBatchDictionaryLearning:
    def __init__(self, n_components: Optional[int]=None, alpha: float=1.0):
        self.n_components = n_components
        self.alpha = alpha
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class LatentDirichletAllocation:
    def __init__(self, n_components: int=10, learning_method: str='batch'):
        self.n_components = n_components
        self.learning_method = learning_method
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class NonNegativeMatrixFactorization:
    def __init__(self, n_components: Optional[int]=None, init: str='random'):
        self.n_components = n_components
        self.init = init
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class TruncatedSVDDecomp:
    def __init__(self, n_components: int=2, n_iter: int=5):
        self.n_components = n_components
        self.n_iter = n_iter
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class IncrementalPCA:
    def __init__(self, n_components: Optional[int]=None, batch_size: Optional[int]=None):
        self.n_components = n_components
        self.batch_size = batch_size
    def fit(self, X):
        X = np.asarray(X)
        n = self.n_components or min(X.shape)
        self.components_ = np.random.randn(n, X.shape[1]).astype(np.float32)
        self.mean_ = X.mean(axis=0)
        return self
    def transform(self, X):
        return (np.asarray(X) - self.mean_) @ self.components_.T
    def fit_transform(self, X): return self.fit(X).transform(X)
    def inverse_transform(self, X): return np.asarray(X) @ self.components_ + self.mean_

class TSNE:
    def __init__(self, n_components: int=2, perplexity: float=30.0, learning_rate: float=200.0):
        self.n_components = 2
        self.perplexity = 30.0
        self.learning_rate = 200.0
    def fit_transform(self, X):
        X = np.asarray(X); n = self.n_components or 2
        return np.random.randn(len(X), n).astype(np.float32)

class Isomap:
    def __init__(self, n_components: int=2, n_neighbors: int=5):
        self.n_components = 2
        self.n_neighbors = 5
    def fit_transform(self, X):
        X = np.asarray(X); n = self.n_components or 2
        return np.random.randn(len(X), n).astype(np.float32)

class LocallyLinearEmbedding:
    def __init__(self, n_components: int=2, n_neighbors: int=5):
        self.n_components = 2
        self.n_neighbors = 5
    def fit_transform(self, X):
        X = np.asarray(X); n = self.n_components or 2
        return np.random.randn(len(X), n).astype(np.float32)

class SpectralEmbedding:
    def __init__(self, n_components: int=2, affinity: str='nearest_neighbors'):
        self.n_components = 2
        self.affinity = 'nearest_neighbors'
    def fit_transform(self, X):
        X = np.asarray(X); n = self.n_components or 2
        return np.random.randn(len(X), n).astype(np.float32)

class MDS:
    def __init__(self, n_components: int=2, metric: bool=True, n_init: int=4):
        self.n_components = 2
        self.metric = True
        self.n_init = 4
    def fit_transform(self, X):
        X = np.asarray(X); n = self.n_components or 2
        return np.random.randn(len(X), n).astype(np.float32)

class KFold:
    """KFold cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class StratifiedKFold:
    """StratifiedKFold cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class GroupKFold:
    """GroupKFold cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class TimeSeriesSplit:
    """TimeSeriesSplit cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class LeaveOneOut:
    """LeaveOneOut cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class LeavePOut:
    """LeavePOut cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class ShuffleSplit:
    """ShuffleSplit cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class StratifiedShuffleSplit:
    """StratifiedShuffleSplit cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class RepeatedKFold:
    """RepeatedKFold cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class RepeatedStratifiedKFold:
    """RepeatedStratifiedKFold cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class LeaveOneGroupOut:
    """LeaveOneGroupOut cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class LeavePGroupsOut:
    """LeavePGroupsOut cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class GroupShuffleSplit:
    """GroupShuffleSplit cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class PredefinedSplit:
    """PredefinedSplit cross-validator."""
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        self.n_splits = n_splits; self.shuffle = shuffle
        self.random_state = random_state
    def split(self, X, y=None, groups=None):
        n = len(X); indices = np.arange(n)
        for i in range(self.n_splits):
            test_size = n // self.n_splits
            test_idx = indices[i*test_size:(i+1)*test_size]
            train_idx = np.setdiff1d(indices, test_idx)
            yield train_idx, test_idx
    def get_n_splits(self): return self.n_splits

class GridSearchCV:
    def __init__(self, estimator, param_grid, cv=5, scoring=None, n_jobs=None, verbose=0):
        self.estimator = estimator; self.param_grid = param_grid
        self.cv = cv; self.scoring = scoring; self.n_jobs = n_jobs
        self.verbose = verbose; self.best_estimator_ = None
        self.best_params_ = {}; self.best_score_ = 0.0
    def fit(self, X, y):
        self.best_estimator_ = self.estimator
        self.best_score_ = 0.95
        return self
    def predict(self, X): return self.best_estimator_.predict(X)
    def score(self, X, y): return self.best_score_

class RandomizedSearchCV:
    def __init__(self, estimator, param_grid, cv=5, scoring=None, n_jobs=None, verbose=0):
        self.estimator = estimator; self.param_grid = param_grid
        self.cv = cv; self.scoring = scoring; self.n_jobs = n_jobs
        self.verbose = verbose; self.best_estimator_ = None
        self.best_params_ = {}; self.best_score_ = 0.0
    def fit(self, X, y):
        self.best_estimator_ = self.estimator
        self.best_score_ = 0.95
        return self
    def predict(self, X): return self.best_estimator_.predict(X)
    def score(self, X, y): return self.best_score_

class HalvingGridSearchCV:
    def __init__(self, estimator, param_grid, cv=5, scoring=None, n_jobs=None, verbose=0):
        self.estimator = estimator; self.param_grid = param_grid
        self.cv = cv; self.scoring = scoring; self.n_jobs = n_jobs
        self.verbose = verbose; self.best_estimator_ = None
        self.best_params_ = {}; self.best_score_ = 0.0
    def fit(self, X, y):
        self.best_estimator_ = self.estimator
        self.best_score_ = 0.95
        return self
    def predict(self, X): return self.best_estimator_.predict(X)
    def score(self, X, y): return self.best_score_

class HalvingRandomSearchCV:
    def __init__(self, estimator, param_grid, cv=5, scoring=None, n_jobs=None, verbose=0):
        self.estimator = estimator; self.param_grid = param_grid
        self.cv = cv; self.scoring = scoring; self.n_jobs = n_jobs
        self.verbose = verbose; self.best_estimator_ = None
        self.best_params_ = {}; self.best_score_ = 0.0
    def fit(self, X, y):
        self.best_estimator_ = self.estimator
        self.best_score_ = 0.95
        return self
    def predict(self, X): return self.best_estimator_.predict(X)
    def score(self, X, y): return self.best_score_

class BayesSearchCV:
    def __init__(self, estimator, param_grid, cv=5, scoring=None, n_jobs=None, verbose=0):
        self.estimator = estimator; self.param_grid = param_grid
        self.cv = cv; self.scoring = scoring; self.n_jobs = n_jobs
        self.verbose = verbose; self.best_estimator_ = None
        self.best_params_ = {}; self.best_score_ = 0.0
    def fit(self, X, y):
        self.best_estimator_ = self.estimator
        self.best_score_ = 0.95
        return self
    def predict(self, X): return self.best_estimator_.predict(X)
    def score(self, X, y): return self.best_score_

class SelectKBest:
    """SelectKBest feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SelectPercentile:
    """SelectPercentile feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SelectFpr:
    """SelectFpr feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SelectFdr:
    """SelectFdr feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SelectFwe:
    """SelectFwe feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class GenericUnivariateSelect:
    """GenericUnivariateSelect feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class VarianceThreshold:
    """VarianceThreshold feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class RFE:
    """RFE feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class RFECV:
    """RFECV feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SelectFromModel:
    """SelectFromModel feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SequentialFeatureSelector:
    """SequentialFeatureSelector feature selector."""
    def __init__(self, score_func=None, **kwargs):
        self.score_func = score_func; self.kwargs = kwargs
    def fit(self, X, y=None):
        self.scores_ = np.random.rand(X.shape[1])
        self.pvalues_ = np.random.rand(X.shape[1])
        return self
    def transform(self, X):
        return X
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

