"""PINN training configuration — battery SOH estimation on RTX 4060 Laptop."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelConfig:
    input_dim: int = 132
    hidden_dims: tuple = (128, 128, 64)
    dropout: float = 0.1
    output_dim: int = 1
    activation: str = "gelu"


@dataclass
class PhysicsConfig:
    ecm_weight: float = 0.15
    smoothness_weight: float = 0.05
    monotonic_weight: float = 0.02
    # LiFePO4 18650 ECM nominal parameters
    r0_initial_ohm: float = 0.045
    r0_aging_coeff: float = 0.12
    degradation_alpha: float = 0.78


@dataclass
class TrainingConfig:
    batch_size: int = 256
    epochs: int = 600
    learning_rate: float = 5e-4
    weight_decay: float = 1e-5
    lr_factor: float = 0.5
    lr_patience: int = 30
    early_stop_patience: int = 80
    grad_clip: float = 1.0
    use_amp: bool = True
    num_workers: int = 0  # 0 avoids Windows spawn multiprocessing issues


@dataclass
class DataConfig:
    ic_curve_pts: int = 128
    voltage_span: tuple = (2.8, 3.6)
    train_ratio: float = 0.70
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    n_cells: int = 50
    max_cycles: int = 800
    temperature_range: tuple = (20.0, 45.0)
    charge_current_pu: tuple = (0.3, 1.0)
    noise_voltage_mv: float = 2.5


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    checkpoint_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "checkpoints")
    log_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "logs")
    data_cache: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "cache")
    seed: int = 42
