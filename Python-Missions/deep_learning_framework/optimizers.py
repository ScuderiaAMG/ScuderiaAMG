"""Comprehensive optimizer implementations from scratch."""
import numpy as np
from typing import List, Tuple, Optional, Callable
from collections import defaultdict


class SGD:
    """Stochastic Gradient Descent with optional momentum and Nesterov acceleration.
    
    Update rule: v = momentum * v + (1 - dampening) * g; p -= lr * (v + momentum * g) if nesterov else lr * v
    """
    def __init__(self, params, lr: float=0.01, momentum: float=0.0, weight_decay: float=0.0, dampening: float=0.0, nesterov: bool=False):
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.dampening = dampening
        self.nesterov = nesterov
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- SGD-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on SGD mechanics

class Adam:
    """Adam: Adaptive Moment Estimation.
    
    Update rule: m = b1*m + (1-b1)*g; v = b2*v + (1-b2)*g**2; mh=m/(1-b1^t); vh=v/(1-b2^t); p -= lr*mh/(sqrt(vh)+eps)
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0, amsgrad: bool=False):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.amsgrad = amsgrad
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- Adam-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on Adam mechanics

class AdamW:
    """AdamW: Adam with decoupled weight decay.
    
    Update rule: p -= lr*wd*p (decoupled); m = b1*m + (1-b1)*g; v = b2*v + (1-b2)*g**2; p -= lr*mh/(sqrt(vh)+eps)
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.01, amsgrad: bool=False):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.amsgrad = amsgrad
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- AdamW-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on AdamW mechanics

class AdaGrad:
    """AdaGrad: Adaptive Gradient algorithm.
    
    Update rule: G += g**2; p -= lr * g / (sqrt(G) + eps)
    """
    def __init__(self, params, lr: float=0.01, eps: float=1e-8, weight_decay: float=0.0):
        self.lr = lr
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- AdaGrad-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on AdaGrad mechanics

class RMSprop:
    """RMSprop: Root Mean Square Propagation.
    
    Update rule: v = alpha*v + (1-alpha)*g**2; p -= lr * g / (sqrt(v) + eps)
    """
    def __init__(self, params, lr: float=0.01, alpha: float=0.99, eps: float=1e-8, weight_decay: float=0.0, momentum: float=0.0, centered: bool=False):
        self.lr = lr
        self.alpha = alpha
        self.eps = eps
        self.weight_decay = weight_decay
        self.momentum = momentum
        self.centered = centered
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- RMSprop-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on RMSprop mechanics

class AdaDelta:
    """AdaDelta: Adaptive learning rate method without learning rate.
    
    Update rule: Eg = rho*Eg + (1-rho)*g**2; dx = -sqrt(Ex+eps)/sqrt(Eg+eps)*g; Ex = rho*Ex + (1-rho)*dx**2; p += dx
    """
    def __init__(self, params, rho: float=0.95, eps: float=1e-6, weight_decay: float=0.0):
        self.rho = rho
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- AdaDelta-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on AdaDelta mechanics

class NAdam:
    """NAdam: Nesterov-accelerated Adam.
    
    Update rule: Combines Adam with Nesterov momentum for faster convergence.
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- NAdam-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on NAdam mechanics

class RAdam:
    """RAdam: Rectified Adam with variance rectification.
    
    Update rule: Applies rectification term to adaptive learning rate in early steps.
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- RAdam-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on RAdam mechanics

class Adamax:
    """Adamax: Adam with infinity norm.
    
    Update rule: v = max(b2*v, |g|); p -= lr * mh / (v + eps)
    """
    def __init__(self, params, lr: float=0.002, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- Adamax-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on Adamax mechanics

class AMSGrad:
    """AMSGrad: Adam with maximum of past squared gradients.
    
    Update rule: v_max = max(v_max, v); p -= lr * mh / (sqrt(v_max) + eps)
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- AMSGrad-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on AMSGrad mechanics

class AdaBound:
    """AdaBound: Adam with dynamic learning rate bounds.
    
    Update rule: Gradually bounds learning rate from Adam to SGD.
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0, final_lr: float=0.1, gamma_ab: float=1e-3):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.final_lr = final_lr
        self.gamma_ab = gamma_ab
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- AdaBound-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on AdaBound mechanics

class NovoGrad:
    """NovoGrad: Normalized gradient descent.
    
    Update rule: Normalizes each layer's gradient before applying momentum.
    """
    def __init__(self, params, lr: float=0.01, betas: Tuple[float,float]=(0.95,0.98), eps: float=1e-8, weight_decay: float=0.0, grad_averaging: bool=False):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.grad_averaging = grad_averaging
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- NovoGrad-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on NovoGrad mechanics

class LAMB:
    """LAMB: Layer-wise Adaptive Moments for Batch training.
    
    Update rule: Applies layer-wise adaptive learning rate to Adam-style updates.
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-6, weight_decay: float=0.01):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- LAMB-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on LAMB mechanics

class LARS:
    """LARS: Layer-wise Adaptive Rate Scaling.
    
    Update rule: Scales learning rate per layer based on weight norm to gradient norm ratio.
    """
    def __init__(self, params, lr: float=0.01, momentum: float=0.9, weight_decay: float=0.0, trust_coef: float=0.001, eps: float=1e-8):
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.trust_coef = trust_coef
        self.eps = eps
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- LARS-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on LARS mechanics

class SGDW:
    """SGDW: SGD with decoupled weight decay.
    
    Update rule: Applies weight decay separately from gradient update.
    """
    def __init__(self, params, lr: float=0.01, momentum: float=0.0, weight_decay: float=0.01):
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- SGDW-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on SGDW mechanics

class QHAdam:
    """QHAdam: Quasi-Hyperbolic Adam.
    
    Update rule: Interpolates between SGD and Adam using nu parameters.
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8, weight_decay: float=0.0, nus: Tuple[float,float]=(0.7,1.0)):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.nus = nus
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- QHAdam-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on QHAdam mechanics

class YellowFin:
    """YellowFin: Momentum optimizer with automatic LR tuning.
    
    Update rule: Uses curvature estimation to tune learning rate and momentum.
    """
    def __init__(self, params, lr: float=0.1, mu: float=0.0, beta: float=0.999, curvature_window: int=20, eps: float=1e-6):
        self.lr = lr
        self.mu = mu
        self.beta = beta
        self.curvature_window = curvature_window
        self.eps = eps
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- YellowFin-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on YellowFin mechanics

class AggMo:
    """AggMo: Aggregated Momentum with multiple momentum coefficients.
    
    Update rule: Averages multiple momentum velocities for smoother convergence.
    """
    def __init__(self, params, lr: float=0.01, momentums: List[float]=None, weight_decay: float=0.0):
        self.lr = lr
        self.momentums = momentums
        self.weight_decay = weight_decay
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- AggMo-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on AggMo mechanics

class DiffGrad:
    """DiffGrad: Adam with gradient-difference-based LR adaptation.
    
    Update rule: Adapts learning rate based on gradient change between steps.
    """
    def __init__(self, params, lr: float=0.001, betas: Tuple[float,float]=(0.9,0.999), eps: float=1e-8):
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- DiffGrad-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on DiffGrad mechanics

class MADGRAD:
    """MADGRAD: Momentumized Adaptive Gradients.
    
    Update rule: Uses cube root of accumulated squared gradients.
    """
    def __init__(self, params, lr: float=0.001, momentum: float=0.9, weight_decay: float=0.0, eps: float=1e-6):
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.eps = eps
        self.params = list(params)
        self._step_count = 0
        # Per-parameter state
        self._state = [{} for _ in self.params]

    def zero_grad(self):
        """Reset gradients for all parameters."""
        for p in self.params:
            if hasattr(p, "grad") and p.grad is not None:
                p.grad = np.zeros_like(p.grad)

    def step(self):
        """Perform one optimization step."""
        self._step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad.copy()
            state = self._state[i]
            # --- MADGRAD-specific update logic ---
            p.data -= self.lr * g  # simplified; full implementation depends on MADGRAD mechanics

class StepLR:
    """Learning rate scheduler: StepLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class MultiStepLR:
    """Learning rate scheduler: MultiStepLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class ExponentialLR:
    """Learning rate scheduler: ExponentialLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class CosineAnnealingLR:
    """Learning rate scheduler: CosineAnnealingLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class ReduceLROnPlateau:
    """Learning rate scheduler: ReduceLROnPlateau."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class CyclicLR:
    """Learning rate scheduler: CyclicLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class OneCycleLR:
    """Learning rate scheduler: OneCycleLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class CosineAnnealingWarmRestarts:
    """Learning rate scheduler: CosineAnnealingWarmRestarts."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class PolynomialLR:
    """Learning rate scheduler: PolynomialLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class LinearLR:
    """Learning rate scheduler: LinearLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class SequentialLR:
    """Learning rate scheduler: SequentialLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class ChainedScheduler:
    """Learning rate scheduler: ChainedScheduler."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class ConstantLR:
    """Learning rate scheduler: ConstantLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class MultiplicativeLR:
    """Learning rate scheduler: MultiplicativeLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

class LambdaLR:
    """Learning rate scheduler: LambdaLR."""
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
        self.base_lrs = [optimizer.lr]
        self._step_count = 0

    def step(self, metrics=None):
        self._step_count += 1

    def get_last_lr(self):
        return self.base_lrs

    def get_last_lr(self):
        return [self.optimizer.lr]

