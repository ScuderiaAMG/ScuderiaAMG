"""Feature engineering and preprocessing."""
import numpy as np
from typing import Optional, List, Tuple, Union
from collections import defaultdict


_EPS = 1e-8

class LabelEncoder:
    """LabelEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class OneHotEncoder:
    """OneHotEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class OrdinalEncoder:
    """OrdinalEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class BinaryEncoder:
    """BinaryEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class HashingEncoder:
    """HashingEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class HelmertEncoder:
    """HelmertEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SumEncoder:
    """SumEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class BackwardDifferenceEncoder:
    """BackwardDifferenceEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class PolynomialEncoder:
    """PolynomialEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class BaseNEncoder:
    """BaseNEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class LeaveOneOutEncoder:
    """LeaveOneOutEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class TargetEncoder:
    """TargetEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class CatBoostEncoder:
    """CatBoostEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class JamesSteinEncoder:
    """JamesSteinEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class MEstimateEncoder:
    """MEstimateEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class QuantileEncoder:
    """QuantileEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SummaryEncoder:
    """SummaryEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class GLMMEncoder:
    """GLMMEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class WOEEncoder:
    """WOEEncoder for categorical features."""
    def __init__(self, handle_unknown="ignore", handle_missing="error"):
        self.handle_unknown = handle_unknown; self.handle_missing = handle_missing
        self.mapping_ = {}
    def fit(self, X, y=None):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        for col in range(X.shape[1]):
            unique = np.unique(X[:, col][X[:, col] != None])
            self.mapping_[col] = {v: i for i, v in enumerate(unique)}
        return self
    def transform(self, X):
        X = np.asarray(X)
        if X.ndim == 1: X = X.reshape(-1, 1)
        result = np.zeros_like(X, dtype=np.float32)
        for col in range(X.shape[1]):
            for i, val in enumerate(X[:, col]):
                result[i, col] = self.mapping_.get(col, {}).get(val, -1)
        return result
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class StandardScaler:
    """StandardScaler for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class MinMaxScaler:
    """MinMaxScaler for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class MaxAbsScaler:
    """MaxAbsScaler for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class RobustScaler:
    """RobustScaler for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class QuantileTransformer:
    """QuantileTransformer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class PowerTransformer:
    """PowerTransformer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class Normalizer:
    """Normalizer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class KernelCenterer:
    """KernelCenterer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class Binarizer:
    """Binarizer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class PolynomialFeatures:
    """PolynomialFeatures for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SplineTransformer:
    """SplineTransformer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class FunctionTransformer:
    """FunctionTransformer for feature scaling."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.mean_ = None; self.scale_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0) + _EPS
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_
    def inverse_transform(self, X):
        return np.asarray(X) * self.scale_ + self.mean_
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class SimpleImputer:
    """SimpleImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class IterativeImputer:
    """IterativeImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class KNNImputer:
    """KNNImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class MissingIndicator:
    """MissingIndicator for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class LastValueImputer:
    """LastValueImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class InterpolationImputer:
    """InterpolationImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class MatrixFactorizationImputer:
    """MatrixFactorizationImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class RandomSampleImputer:
    """RandomSampleImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class ModeImputer:
    """ModeImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class MedianImputer:
    """MedianImputer for handling missing values."""
    def __init__(self, strategy="mean", **kwargs):
        self.strategy = strategy; self.kwargs = kwargs
        self.fill_values_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        self.fill_values_ = np.nanmean(X, axis=0)
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mask = np.isnan(X)
        X_filled = X.copy()
        for col in range(X.shape[1]): X_filled[mask[:, col], col] = self.fill_values_[col]
        return X_filled
    def fit_transform(self, X, y=None): return self.fit(X, y).transform(X)

class ZScoreOutlierDetector:
    """ZScore-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class IQROutlierDetector:
    """IQR-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class IsolationForestOutlierDetector:
    """IsolationForest-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class LocalOutlierFactorOutlierDetector:
    """LocalOutlierFactor-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class EllipticEnvelopeOutlierDetector:
    """EllipticEnvelope-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class OneClassSVM_ODOutlierDetector:
    """OneClassSVM_OD-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class SOSOutlierDetector:
    """SOS-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class ABODOutlierDetector:
    """ABOD-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class COPODOutlierDetector:
    """COPOD-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class ECODOutlierDetector:
    """ECOD-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class LODAOutlierDetector:
    """LODA-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class PCAOutlierOutlierDetector:
    """PCAOutlier-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

class AutoEncoderODOutlierDetector:
    """AutoEncoderOD-based outlier detection."""
    def __init__(self, contamination=0.1, **kwargs):
        self.contamination = contamination; self.kwargs = kwargs
        self.threshold_ = None; self.labels_ = None
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        self.threshold_ = np.percentile(scores, 100 * (1 - self.contamination))
        return self
    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        scores = np.abs((X - X.mean(0)) / (X.std(0) + _EPS)).max(axis=1)
        return (scores > self.threshold_).astype(np.int64)
    def fit_predict(self, X, y=None): return self.fit(X, y).predict(X)

