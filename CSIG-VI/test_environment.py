import torch
import torchvision
import cv2
import numpy as np
import skimage
import sys

def test_environment():
    print("=== 环境验证测试 ===")
    
    # Python版本
    print(f"Python版本: {sys.version}")
    
    # PyTorch和CUDA
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU设备: {torch.cuda.get_device_name(0)}")
        print(f"GPU数量: {torch.cuda.device_count()}")
    
    # 其他关键包
    print(f"OpenCV版本: {cv2.__version__}")
    print(f"NumPy版本: {np.__version__}")
    print(f"Scikit-image版本: {skimage.__version__}")
    
    # 测试张量运算
    if torch.cuda.is_available():
        x = torch.randn(3, 256, 256).cuda()
        y = torch.randn(3, 256, 256).cuda()
        z = torch.matmul(x, y)
        print("GPU张量运算测试: 成功")
    
    print("=== 环境验证完成 ===")

if __name__ == "__main__":
    test_environment()