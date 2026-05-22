"""CNN training configuration — battery aging classification + RUL on RTX 4060 Laptop."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelConfig:
    # 1D-CNN architecture
    in_channels: int = 1
    conv_filters: tuple = (16, 32, 64)
    conv_kernels: tuple = (7, 5, 3)
    dropout: float = 0.15
    hidden_dim: int = 32

    # Task heads
    num_stages: int = 4       # I: formation, II: stable, III: accelerated, IV: EOL
    rul_output_dim: int = 1   # remaining cycles (normalised)


@dataclass
class StageThresholds:
    """SOH thresholds for aging stage classification."""
    formation: float = 0.88   # stage I:   SOH >= 0.88
    stable: float = 0.78      # stage II:  SOH >= 0.78
    accelerated: float = 0.68 # stage III: SOH >= 0.68
                              # stage IV:  SOH <  0.68  (EOL)


@dataclass
class TrainingConfig:
    batch_size: int = 128
    epochs: int = 500
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    lr_factor: float = 0.5
    lr_patience: int = 25
    early_stop_patience: int = 60
    grad_clip: float = 1.0
    use_amp: bool = True
    num_workers: int = 0

    # Multi-task loss weights
    cls_weight: float = 0.5
    rul_weight: float = 0.5


@dataclass
class DataConfig:
    ic_curve_pts: int = 128
    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15

    # RUL: cycles below which SOH first drops under EOL threshold
    eol_soh_threshold: float = 0.70

    # Stage label smoothing
    label_smoothing: float = 0.05


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    thresholds: StageThresholds = field(default_factory=StageThresholds)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    checkpoint_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "checkpoints")
    log_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "logs")
    seed: int = 42
