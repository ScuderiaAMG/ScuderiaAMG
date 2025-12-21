#!/bin/bash

echo "=== DarkVision-Net 环境安装脚本 ==="

# 检查系统
echo "检查系统环境..."
if [ ! -f "/etc/os-release" ]; then
    echo "错误：无法确定操作系统"
    exit 1
fi

# 检查Ubuntu版本
UBUNTU_VERSION=$(grep "VERSION_ID" /etc/os-release | cut -d'"' -f2)
echo "检测到Ubuntu版本: $UBUNTU_VERSION"

# 检查NVIDIA驱动
if ! command -v nvidia-smi &> /dev/null; then
    echo "警告：未检测到NVIDIA驱动，性能可能受影响"
else
    echo "NVIDIA驱动检测成功"
    nvidia-smi
fi

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv darkvision_env
source darkvision_env/bin/activate

# 安装PyTorch（根据CUDA版本）
CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -d',' -f1)
echo "检测到CUDA版本: $CUDA_VERSION"

if [ "$CUDA_VERSION" = "11.8" ]; then
    echo "安装CUDA 11.8版本的PyTorch..."
    pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
elif [ "$CUDA_VERSION" = "11.7" ]; then
    echo "安装CUDA 11.7版本的PyTorch..."
    pip install torch==2.0.1+cu117 torchvision==0.15.2+cu117 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117
else
    echo "安装CPU版本的PyTorch..."
    pip install torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
fi

# 安装其他依赖
echo "安装其他依赖包..."
pip install -r requirements.txt

# 验证安装
echo "验证安装..."
python test_environment.py

echo "=== 安装完成 ==="
echo "激活虚拟环境: source darkvision_env/bin/activate"
echo "运行训练: python main.py --input_dir input --epochs 100"