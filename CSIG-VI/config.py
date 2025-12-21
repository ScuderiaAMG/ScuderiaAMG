import torch
import os

class PerformanceConfig:
    """性能优化配置"""
    
    # CUDA优化设置
    CUDA_CONFIG = {
        'benchmark': True,  # 启用CUDA基准测试
        'deterministic': False,  # 禁用确定性以获得更好性能
        'allow_tf32': True,  # 启用TF32计算（RTX4060支持）
        'cudnn_enabled': True,
    }
    
    # 训练优化
    TRAINING_CONFIG = {
        'gradient_accumulation_steps': 2,
        'mixed_precision': True,  # 自动混合精度
        'pin_memory': True,
        'num_workers': 4,  # 根据CPU核心数调整
    }
    
    # 内存优化
    MEMORY_CONFIG = {
        'max_split_size_mb': 128,
        'garbage_collection_threshold': 0.8,
    }

def setup_environment():
    """设置优化环境"""
    
    # 应用CUDA配置
    torch.backends.cudnn.benchmark = CUDA_CONFIG['benchmark']
    torch.backends.cudnn.deterministic = CUDA_CONFIG['deterministic']
    torch.backends.cuda.matmul.allow_tf32 = CUDA_CONFIG['allow_tf32']
    torch.backends.cudnn.allow_tf32 = CUDA_CONFIG['allow_tf32']
    
    # 设置内存优化
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(0.9)  # 预留10%内存给系统
        
    print("环境优化配置完成")

# 自动设置
setup_environment()