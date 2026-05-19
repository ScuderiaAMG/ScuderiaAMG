"""Comprehensive loss function library."""
import numpy as np
from typing import Optional, Union, List, Tuple

_EPS = 1e-8

class Mse_loss:  # 001
    """Mean Squared Error loss function.
    
    Formula: ((pred - target) ** 2).mean(axis=axis)...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute mse_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = ((pred - target) ** 2).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Mae_loss:  # 002
    """Mean Absolute Error (L1) loss function.
    
    Formula: np.abs(pred - target).mean(axis=axis)...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute mae_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.abs(pred - target).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Smooth_l1_loss:  # 003
    """Smooth L1 / Huber loss function.
    
    Formula: np.where(np.abs(pred-target) < beta, 0.5*(pred-target)**2/beta, np.abs(pred-targ...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute smooth_l1_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(np.abs(pred-target) < beta, 0.5*(pred-target)**2/beta, np.abs(pred-target)-0.5*beta).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Huber_loss:  # 004
    """Huber Loss loss function.
    
    Formula: np.where(np.abs(diff) < delta, 0.5*diff**2, delta*(np.abs(diff)-0.5*delta)).mean...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute huber_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(np.abs(diff) < delta, 0.5*diff**2, delta*(np.abs(diff)-0.5*delta)).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Log_cosh_loss:  # 005
    """Log-Cosh loss function.
    
    Formula: np.log(np.cosh(pred - target)).mean(axis=axis)...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute log_cosh_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.log(np.cosh(pred - target)).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Quantile_loss:  # 006
    """Quantile / Pinball loss function.
    
    Formula: np.where(pred >= target, q*(pred-target), (1-q)*(target-pred)).mean(axis=axis)...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute quantile_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(pred >= target, q*(pred-target), (1-q)*(target-pred)).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Cosine_embedding_loss:  # 007
    """Cosine Embedding loss function.
    
    Formula: 1.0 - (x1*x2).sum(axis=-1)/(np.sqrt((x1**2).sum(axis=-1))*np.sqrt((x2**2).sum(ax...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute cosine_embedding_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = 1.0 - (x1*x2).sum(axis=-1)/(np.sqrt((x1**2).sum(axis=-1))*np.sqrt((x2**2).sum(axis=-1))+_EPS)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Poisson_nll_loss:  # 008
    """Poisson NLL loss function.
    
    Formula: (pred - target * np.log(np.clip(pred, _EPS, None))).mean(axis=axis)...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute poisson_nll_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = (pred - target * np.log(np.clip(pred, _EPS, None))).mean(axis=axis)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Kl_div_loss:  # 009
    """KL Divergence loss function.
    
    Formula: (target * (np.log(np.clip(target, _EPS, None)) - log_pred)).sum(axis=-1).mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute kl_div_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = (target * (np.log(np.clip(target, _EPS, None)) - log_pred)).sum(axis=-1).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Hinge_embedding_loss:  # 010
    """Hinge Embedding loss function.
    
    Formula: np.where(y > 0, pred, np.maximum(0, margin - pred)).mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute hinge_embedding_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(y > 0, pred, np.maximum(0, margin - pred)).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Multi_margin_loss:  # 011
    """Multi-class Margin loss function.
    
    Formula: np.maximum(0, margin - x[range(n), y].reshape(-1,1) + x).mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute multi_margin_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.maximum(0, margin - x[range(n), y].reshape(-1,1) + x).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Triplet_margin_loss:  # 012
    """Triplet Margin loss function.
    
    Formula: np.maximum(0, pos_dist - neg_dist + margin).mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute triplet_margin_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.maximum(0, pos_dist - neg_dist + margin).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Ctc_loss_stub:  # 013
    """CTC Loss (simplified) loss function.
    
    Formula: -log_probs[range(B), targets, :].sum() / B...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute ctc_loss_stub.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = -log_probs[range(B), targets, :].sum() / B
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Gaussian_nll_loss:  # 014
    """Gaussian NLL loss function.
    
    Formula: (0.5 * (np.log(np.clip(var, _EPS, None)) + (target - mean)**2 / np.clip(var, _EP...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute gaussian_nll_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = (0.5 * (np.log(np.clip(var, _EPS, None)) + (target - mean)**2 / np.clip(var, _EPS, None))).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Earth_mover_loss:  # 015
    """Earth Mover Distance loss function.
    
    Formula: np.abs(np.cumsum(pred, axis=-1) - np.cumsum(target, axis=-1)).sum(axis=-1).mean(...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute earth_mover_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.abs(np.cumsum(pred, axis=-1) - np.cumsum(target, axis=-1)).sum(axis=-1).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Charbonnier_loss:  # 016
    """Charbonnier loss function.
    
    Formula: (((pred - target)**2 + eps**2) ** 0.5).mean()...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute charbonnier_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = (((pred - target)**2 + eps**2) ** 0.5).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Cauchy_loss:  # 017
    """Cauchy / Lorentzian loss function.
    
    Formula: np.log(1.0 + ((pred-target)/c)**2).mean()...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute cauchy_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.log(1.0 + ((pred-target)/c)**2).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Geman_mcclure_loss:  # 018
    """Geman-McClure loss function.
    
    Formula: ((pred-target)**2 / ((pred-target)**2 + c**2)).mean()...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute geman_mcclure_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = ((pred-target)**2 / ((pred-target)**2 + c**2)).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Welsch_loss:  # 019
    """Welsch / Leclerc loss function.
    
    Formula: (1.0 - np.exp(-((pred-target)/c)**2)).mean()...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute welsch_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = (1.0 - np.exp(-((pred-target)/c)**2)).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Tukey_biweight_loss:  # 020
    """Tukey Biweight loss function.
    
    Formula: np.where(np.abs(diff) <= c, c**2/6*(1-(1-(diff/c)**2)**3), c**2/6).mean()...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute tukey_biweight_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(np.abs(diff) <= c, c**2/6*(1-(1-(diff/c)**2)**3), c**2/6).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Cross_entropy_loss:  # 021
    """Cross Entropy (logits) loss function.
    
    Formula: -log_probs_of_correct_class.mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute cross_entropy_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = -log_probs_of_correct_class.mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Binary_cross_entropy_loss:  # 022
    """Binary Cross Entropy loss function.
    
    Formula: -(target * np.log(p_clip) + (1-target)*np.log(1-p_clip)).mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute binary_cross_entropy_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = -(target * np.log(p_clip) + (1-target)*np.log(1-p_clip)).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Focal_loss_full:  # 023
    """Focal Loss loss function.
    
    Formula: -alpha*(1-pt)**gamma*np.log(np.clip(pt, _EPS, 1)).mean()...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute focal_loss_full.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = -alpha*(1-pt)**gamma*np.log(np.clip(pt, _EPS, 1)).mean()
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Dice_loss_full:  # 024
    """Dice / F1 Loss loss function.
    
    Formula: 1.0 - (2.0*intersection + smooth)/(union + smooth)...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute dice_loss_full.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = 1.0 - (2.0*intersection + smooth)/(union + smooth)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Jaccard_loss:  # 025
    """Jaccard / IoU Loss loss function.
    
    Formula: 1.0 - (intersection + smooth)/(union - intersection + smooth)...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute jaccard_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = 1.0 - (intersection + smooth)/(union - intersection + smooth)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Tversky_loss:  # 026
    """Tversky Loss loss function.
    
    Formula: 1.0 - (intersection + smooth)/(intersection + alpha_t*fp + beta_t*fn + smooth)...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute tversky_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = 1.0 - (intersection + smooth)/(intersection + alpha_t*fp + beta_t*fn + smooth)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Lovasz_hinge_loss:  # 027
    """Lovasz Hinge (stub) loss function.
    
    Formula: lovasz_hinge(logits, target)...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute lovasz_hinge_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = lovasz_hinge(logits, target)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Wing_loss:  # 028
    """Wing Loss loss function.
    
    Formula: np.where(np.abs(x) < w, w*np.log(1+np.abs(x)/eps_w), np.abs(x)-C_w)...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute wing_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(np.abs(x) < w, w*np.log(1+np.abs(x)/eps_w), np.abs(x)-C_w)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Balanced_l1_loss:  # 029
    """Balanced L1 loss function.
    
    Formula: np.where(diff < 1, a_b1/b_b1*(b_b1*diff+1)*np.log(b_b1*diff+1)-a_b1*diff, gamma_...
    """
    def __init__(self, reduction: str = "mean", axis: Optional[int] = None):
        self.reduction = reduction
        self.axis = axis

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute balanced_l1_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = np.where(diff < 1, a_b1/b_b1*(b_b1*diff+1)*np.log(b_b1*diff+1)-a_b1*diff, gamma_b1*diff+C_b1)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

class Soft_dtw_loss:  # 030
    """Soft-DTW (stub) loss function.
    
    Formula: soft_dtw(x, y, gamma_sdtw)...
    """
    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction

    def __call__(self, pred: np.ndarray, target: np.ndarray, **kwargs) -> np.ndarray:
        """
        Compute soft_dtw_loss.
        
        Args:
            pred: Predicted values, shape (N, ...).
            target: Target values, same shape as pred.
            **kwargs: Additional loss-specific parameters.
        Returns:
            Scalar or reduced loss value.
        """
        loss = soft_dtw(x, y, gamma_sdtw)
        if self.reduction == "mean":
            return float(loss)
        elif self.reduction == "sum":
            return float(np.sum(loss))
        return loss

