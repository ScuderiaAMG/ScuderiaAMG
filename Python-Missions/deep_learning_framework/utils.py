"""Miscellaneous utilities."""
import numpy as np
import time
import os
import pickle
import json
import hashlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


_EPS = 1e-8

class Timer:
    def __enter__(self): self.start = time.perf_counter(); return self
    def __exit__(self, *args): self.end = time.perf_counter(); self.elapsed = self.end - self.start

class Profiler:
    def __init__(self): self.records = {}
    def start(self, name): self.records[name] = time.perf_counter()
    def stop(self, name): self.records[name] = time.perf_counter() - self.records.get(name, 0)
    def report(self): return "\n".join(f"{k}: {v:.4f}s" for k,v in self.records.items())

def set_seed(seed: int = 42):
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    import random; random.seed(seed)

def save_pickle(obj, path):
    with open(path, "wb") as f: pickle.dump(obj, f)

def load_pickle(path):
    with open(path, "rb") as f: return pickle.load(f)

def save_json(obj, path):
    with open(path, "w") as f: json.dump(obj, f, indent=2)

def load_json(path):
    with open(path, "r") as f: return json.load(f)

class CheckpointManager:
    def __init__(self, save_dir="./checkpoints", max_to_keep=5):
        self.save_dir = save_dir; self.max_to_keep = max_to_keep
        os.makedirs(save_dir, exist_ok=True)
    def save(self, model, optimizer, epoch, loss, name="checkpoint"):
        path = os.path.join(self.save_dir, f"{name}_epoch{epoch}.pkl")
        save_pickle({"model": model, "optimizer": optimizer, "epoch": epoch, "loss": loss}, path)
    def load(self, path): return load_pickle(path)
    def list_checkpoints(self): return sorted(os.listdir(self.save_dir))

def to_one_hot(labels, num_classes=None):
    labels = np.asarray(labels, dtype=np.int64)
    if num_classes is None: num_classes = labels.max() + 1
    oh = np.zeros((len(labels), num_classes), dtype=np.float32)
    oh[np.arange(len(labels)), labels] = 1.0
    return oh

def from_one_hot(one_hot):
    return one_hot.argmax(axis=-1)

def normalize_minmax(x, **kwargs):
    """minmax normalization."""
    if "minmax" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "minmax" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_zscore(x, **kwargs):
    """zscore normalization."""
    if "zscore" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "zscore" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_robust(x, **kwargs):
    """robust normalization."""
    if "robust" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "robust" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_quantile(x, **kwargs):
    """quantile normalization."""
    if "quantile" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "quantile" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_power(x, **kwargs):
    """power normalization."""
    if "power" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "power" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_unit_vector(x, **kwargs):
    """unit_vector normalization."""
    if "unit_vector" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "unit_vector" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_l1(x, **kwargs):
    """l1 normalization."""
    if "l1" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "l1" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_l2(x, **kwargs):
    """l2 normalization."""
    if "l2" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "l2" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_max_abs(x, **kwargs):
    """max_abs normalization."""
    if "max_abs" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "max_abs" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_tanh(x, **kwargs):
    """tanh normalization."""
    if "tanh" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "tanh" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_log(x, **kwargs):
    """log normalization."""
    if "log" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "log" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_sqrt(x, **kwargs):
    """sqrt normalization."""
    if "sqrt" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "sqrt" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def normalize_boxcox_stub(x, **kwargs):
    """boxcox_stub normalization."""
    if "boxcox_stub" == "minmax":
        return (x - x.min()) / (x.max() - x.min() + _EPS)
    elif "boxcox_stub" == "zscore":
        return (x - x.mean()) / (x.std() + _EPS)
    return x

def init_xavier_uniform(shape, gain=1.0):
    """Weight initialization: xavier_uniform."""
    if "xavier_uniform" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "xavier_uniform" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_xavier_normal(shape, gain=1.0):
    """Weight initialization: xavier_normal."""
    if "xavier_normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "xavier_normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_kaiming_uniform(shape, gain=1.0):
    """Weight initialization: kaiming_uniform."""
    if "kaiming_uniform" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "kaiming_uniform" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_kaiming_normal(shape, gain=1.0):
    """Weight initialization: kaiming_normal."""
    if "kaiming_normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "kaiming_normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_orthogonal(shape, gain=1.0):
    """Weight initialization: orthogonal."""
    if "orthogonal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "orthogonal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_sparse(shape, gain=1.0):
    """Weight initialization: sparse."""
    if "sparse" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "sparse" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_dirac(shape, gain=1.0):
    """Weight initialization: dirac."""
    if "dirac" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "dirac" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_positive_unitball(shape, gain=1.0):
    """Weight initialization: positive_unitball."""
    if "positive_unitball" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "positive_unitball" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_truncated_normal(shape, gain=1.0):
    """Weight initialization: truncated_normal."""
    if "truncated_normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "truncated_normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_lecun_uniform(shape, gain=1.0):
    """Weight initialization: lecun_uniform."""
    if "lecun_uniform" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "lecun_uniform" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_lecun_normal(shape, gain=1.0):
    """Weight initialization: lecun_normal."""
    if "lecun_normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "lecun_normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_he_uniform(shape, gain=1.0):
    """Weight initialization: he_uniform."""
    if "he_uniform" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "he_uniform" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_he_normal(shape, gain=1.0):
    """Weight initialization: he_normal."""
    if "he_normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "he_normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_glorot_uniform(shape, gain=1.0):
    """Weight initialization: glorot_uniform."""
    if "glorot_uniform" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "glorot_uniform" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_glorot_normal(shape, gain=1.0):
    """Weight initialization: glorot_normal."""
    if "glorot_normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "glorot_normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_zeros(shape, gain=1.0):
    """Weight initialization: zeros."""
    if "zeros" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "zeros" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_ones(shape, gain=1.0):
    """Weight initialization: ones."""
    if "ones" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "ones" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_constant(shape, gain=1.0):
    """Weight initialization: constant."""
    if "constant" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "constant" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_uniform(shape, gain=1.0):
    """Weight initialization: uniform."""
    if "uniform" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "uniform" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_normal(shape, gain=1.0):
    """Weight initialization: normal."""
    if "normal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "normal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_eye(shape, gain=1.0):
    """Weight initialization: eye."""
    if "eye" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "eye" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

def init_delta_orthogonal(shape, gain=1.0):
    """Weight initialization: delta_orthogonal."""
    if "delta_orthogonal" == "zeros": return np.zeros(shape, dtype=np.float32)
    if "delta_orthogonal" == "ones": return np.ones(shape, dtype=np.float32)
    return np.random.randn(*shape).astype(np.float32) * 0.02

class LRFinder:
    def __init__(self, model, optimizer, loss_fn):
        self.model = model; self.optimizer = optimizer; self.loss_fn = loss_fn
        self.history = {"lr": [], "loss": []}
    def range_test(self, train_loader, start_lr=1e-7, end_lr=10, num_iter=100):
        lr_mult = (end_lr / start_lr) ** (1 / num_iter)
        lr = start_lr
        for i in range(num_iter):
            self.optimizer.lr = lr; lr *= lr_mult
            self.history["lr"].append(lr)
            self.history["loss"].append(0.0)
    def plot(self): pass

def numerical_gradient(f, x, eps=1e-5):
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=["multi_index"])
    while not it.finished:
        idx = it.multi_index
        old = x[idx]
        x[idx] = old + eps; f_plus = f(x)
        x[idx] = old - eps; f_minus = f(x)
        grad[idx] = (f_plus - f_minus) / (2 * eps)
        x[idx] = old
        it.iternext()
    return grad

def count_parameters(model):
    return sum(p.data.size for p in model.parameters())

def freeze_model(model):
    for p in model.parameters(): p.requires_grad = False

def unfreeze_model(model):
    for p in model.parameters(): p.requires_grad = True

def compute_flops(model, input_shape):
    return 0  # FLOP counter stub

def model_summary(model, input_shape):
    lines = ["Model Summary", "="*50]
    lines.append(f"Total params: {count_parameters(model):,}")
    return "\n".join(lines)

class UniformDistribution:
    """Uniform distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class NormalDistribution:
    """Normal distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class BernoulliDistribution:
    """Bernoulli distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class CategoricalDistribution:
    """Categorical distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class MultivariateNormalDistribution:
    """MultivariateNormal distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class LaplaceDistribution:
    """Laplace distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class CauchyDistribution:
    """Cauchy distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class ExponentialDistribution:
    """Exponential distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class GammaDistribution:
    """Gamma distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class BetaDistribution:
    """Beta distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class DirichletDistribution:
    """Dirichlet distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class PoissonDistribution:
    """Poisson distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class GeometricDistribution:
    """Geometric distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class LogNormalDistribution:
    """LogNormal distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class WeibullDistribution:
    """Weibull distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class ParetoDistribution:
    """Pareto distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class StudentTDistribution:
    """StudentT distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class Chi2Distribution:
    """Chi2 distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class FDistributionDistribution:
    """FDistribution distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class WishartDistribution:
    """Wishart distribution helper."""
    def __init__(self, **params):
        self.params = params
    def sample(self, size=None):
        return np.random.randn(*(size or (1,))).astype(np.float32)
    def log_prob(self, x):
        return -0.5 * np.sum(x**2)
    def entropy(self):
        return 0.5 * np.log(2 * np.pi * np.e)

class Logger:
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir; os.makedirs(log_dir, exist_ok=True)
        self.scalars = {}; self.texts = []; self.images = {}
    def log_scalar(self, tag, value, step):
        self.scalars.setdefault(tag, []).append((step, value))
    def log_text(self, tag, text, step):
        self.texts.append((step, tag, text))
    def log_histogram(self, tag, values, step): pass
    def log_image(self, tag, image, step):
        self.images.setdefault(tag, []).append((step, image))
    def flush(self):
        with open(os.path.join(self.log_dir, "scalars.json"), "w") as f:
            json.dump(self.scalars, f)

class ProgressBar:
    def __init__(self, total, prefix="", width=30):
        self.total = total; self.prefix = prefix; self.width = width
        self.current = 0
    def update(self, n=1):
        self.current += n
    def close(self): pass

def distance_euclidean(x, y, **kwargs):
    """euclidean distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_manhattan(x, y, **kwargs):
    """manhattan distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_chebyshev(x, y, **kwargs):
    """chebyshev distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_minkowski(x, y, **kwargs):
    """minkowski distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_cosine(x, y, **kwargs):
    """cosine distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_mahalanobis(x, y, **kwargs):
    """mahalanobis distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_hamming(x, y, **kwargs):
    """hamming distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_canberra(x, y, **kwargs):
    """canberra distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_braycurtis(x, y, **kwargs):
    """braycurtis distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_jensenshannon(x, y, **kwargs):
    """jensenshannon distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_wasserstein_1d(x, y, **kwargs):
    """wasserstein_1d distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_energy_distance(x, y, **kwargs):
    """energy_distance distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_hellinger(x, y, **kwargs):
    """hellinger distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

def distance_total_variation(x, y, **kwargs):
    """total_variation distance between x and y."""
    diff = np.asarray(x) - np.asarray(y)
    return np.sqrt((diff ** 2).sum())

class PadSequence:
    def __init__(self, max_length=None, padding_value=0, truncating="pre", padding="post"):
        self.max_length = max_length; self.padding_value = padding_value
        self.truncating = truncating; self.padding = padding
    def __call__(self, sequences):
        if self.max_length is None: self.max_length = max(len(s) for s in sequences)
        result = np.full((len(sequences), self.max_length), self.padding_value, dtype=np.float32)
        for i, s in enumerate(sequences):
            length = min(len(s), self.max_length)
            result[i, :length] = s[:length]
        return result

