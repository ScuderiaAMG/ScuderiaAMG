"""CNN training configuration — 3-stage battery aging classification + RUL on RTX 4060."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelConfig:
    # Slim residual 1D-CNN (~40K params, INT8 < 40 KB, A55 < 15 ms)
    in_channels: int = 2           # ch1: IC curve, ch2: IC gradient
    conv_filters: tuple = (16, 32, 48)
    conv_kernels: tuple = (7, 7, 5)
    dropout: float = 0.2
    head_hidden: int = 24

    # 3-stage: healthy, degrading, end-of-life
    num_stages: int = 3
    rul_output_dim: int = 1


@dataclass
class StageThresholds:
    """3-stage thresholds balanced for data distribution."""
    healthy: float = 0.82          # SOH >= 0.82 → healthy
    degrading: float = 0.70        # SOH >= 0.70 → degrading
                                   # SOH <  0.70 → EOL


@dataclass
class TrainingConfig:
    batch_size: int = 128
    epochs: int = 600
    learning_rate: float = 8e-4
    weight_decay: float = 1e-4
    lr_factor: float = 0.5
    lr_patience: int = 30
    early_stop_patience: int = 100
    grad_clip: float = 1.0
    use_amp: bool = True
    num_workers: int = 0
    cls_weight: float = 0.55
    rul_weight: float = 0.45


@dataclass
class AugConfig:
    """Training-only data augmentation."""
    gaussian_noise_std: float = 0.03
    scale_range: tuple = (0.85, 1.15)
    shift_max: int = 6


@dataclass
class DataConfig:
    ic_curve_pts: int = 128
    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    eol_soh_threshold: float = 0.70
    label_smoothing: float = 0.08


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    thresholds: StageThresholds = field(default_factory=StageThresholds)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    augment: AugConfig = field(default_factory=AugConfig)
    data: DataConfig = field(default_factory=DataConfig)
    checkpoint_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "checkpoints")
    log_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "logs")
    seed: int = 42
