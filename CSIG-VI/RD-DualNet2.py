import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
import cv2
import os
from pathlib import Path
import time
from typing import List, Tuple
import argparse
from torchvision.models import vgg16
from torchvision.utils import save_image
import numpy.linalg as LA

# ======================
# 1. 轻量化基础模块
# ======================
class DepthwiseSeparableConv(nn.Module):
    """轻量化卷积模块"""
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size, 
                                   stride=stride, padding=kernel_size//2, groups=in_channels)
        self.pointwise = nn.Conv2d(in_channels, out_channels, 1)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, x):
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = self.bn(x)
        return self.relu(x)

class SEBlock(nn.Module):
    """通道注意力模块"""
    def __init__(self, channel, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)

# ======================
# 2. 物理先验引导模块
# ======================
class RetinexDCPGuidedAttention(nn.Module):
    """
    创新点：融合Retinex反射分量和DCP噪声/光照先验的注意力机制
    """
    def __init__(self, in_channels, out_channels):
        super().__init__()
        # 1. 估计Retinex反射分量 R (细节信息)
        self.reflect_conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 3, 3, padding=1),
            nn.Sigmoid()
        )
        
        # 2. 估计DCP先验 (光照和噪声信息)
        self.dcp_conv = nn.Sequential(
            nn.Conv2d(3, 16, 5, padding=2),
            nn.ReLU(),
            nn.Conv2d(16, 1, 5, padding=2)
        )
        
        # 3. 融合生成注意力权重
        self.fusion = nn.Sequential(
            nn.Conv2d(in_channels + 4, out_channels, 1), # 4 = 3(R) + 1(DCP)
            nn.Sigmoid()
        )
        
    def forward(self, x, feat):
        # 计算Retinex反射分量 R
        R = self.reflect_conv(x)
        
        # 计算DCP先验图
        dcp_prior = self.dcp_conv(x)
        
        # 将物理先验与深层特征融合
        B, C, H, W = feat.shape
        R_resized = F.interpolate(R, size=(H, W), mode='bilinear', align_corners=False)
        dcp_resized = F.interpolate(dcp_prior, size=(H, W), mode='bilinear', align_corners=False)
        
        combined = torch.cat([feat, R_resized, dcp_resized], dim=1)
        attention_weights = self.fusion(combined)
        return attention_weights

# ======================
# 3. 轻量化多尺度残差块
# ======================
class LightweightMultiScaleBlock(nn.Module):
    """轻量化的多尺度特征提取块"""
    def __init__(self, channels):
        super().__init__()
        self.conv1 = DepthwiseSeparableConv(channels, channels, 3)
        self.conv2 = DepthwiseSeparableConv(channels, channels, 5)
        self.conv3 = DepthwiseSeparableConv(channels, channels, 7)
        self.se = SEBlock(channels * 3)
        self.fusion = nn.Conv2d(channels * 3, channels, 1)
        self.attention = RetinexDCPGuidedAttention(channels, channels)
        
    def forward(self, x, orig_input):
        feat1 = self.conv1(x)
        feat2 = self.conv2(x)
        feat3 = self.conv3(x)
        
        fused = torch.cat([feat1, feat2, feat3], dim=1)
        fused = self.se(fused)
        fused = self.fusion(fused)
        
        # 应用物理引导的注意力
        attn_weights = self.attention(orig_input, fused)
        weighted = fused * attn_weights
        
        return x + weighted

# ======================
# 4. 双分支主干网络
# ======================
class RD_DualNet(nn.Module):
    """
    主网络：Retinex-DCP Guided Dual-Branch Network
    """
    def __init__(self):
        super().__init__()
        self.channels = 64
        
        # 共享的浅层特征提取器
        self.shallow_feat = nn.Sequential(
            nn.Conv2d(3, self.channels, 3, padding=1),
            nn.ReLU()
        )
        
        # 增强分支 (侧重细节和亮度) - 修正为 ModuleList
        self.enhance_blocks = nn.ModuleList([
            LightweightMultiScaleBlock(self.channels) for _ in range(4)
        ])
        
        # 去噪分支 (侧重平滑和噪声抑制)
        self.denoise_branch = nn.Sequential(
            *[DepthwiseSeparableConv(self.channels, self.channels) for _ in range(3)],
            SEBlock(self.channels)
        )
        
        # 融合与输出
        self.fusion = nn.Sequential(
            nn.Conv2d(self.channels * 2, self.channels, 1),
            nn.ReLU(),
            nn.Conv2d(self.channels, 3, 3, padding=1),
            nn.Tanh()
        )
        
    def forward(self, x):
        shallow = self.shallow_feat(x)
        
        # 双分支处理 - 修正循环调用
        enhanced_feat = shallow
        for block in self.enhance_blocks:
            enhanced_feat = block(enhanced_feat, x)
        denoised_feat = self.denoise_branch(shallow)
        
        # 特征融合
        fused_feat = torch.cat([enhanced_feat, denoised_feat], dim=1)
        residual = self.fusion(fused_feat)
        
        # 残差学习: 输出 = 输入 + 残差
        output = x + residual
        return output # Tanh 已保证范围在 [-1, 1]

# ======================
# 5. 数据集与数据加载
# ======================
class PairedDataset(Dataset):
    """有监督配对数据集: (暗图, 高质量图)"""
    def __init__(self, low_dir, high_dir, patch_size=256):
        self.low_dir = Path(low_dir)
        self.high_dir = Path(high_dir)
        self.patch_size = patch_size
        self.image_names = [f.name for f in self.low_dir.glob("*.jpg")] + \
                           [f.name for f in self.low_dir.glob("*.png")]
        
    def __len__(self):
        return len(self.image_names)
    
    def __getitem__(self, idx):
        name = self.image_names[idx]
        low_img = self._load_image(self.low_dir / name)
        high_img = self._load_image(self.high_dir / name)
        
        # 随机裁剪
        h, w = low_img.shape[:2]
        if h > self.patch_size and w > self.patch_size:
            i = np.random.randint(0, h - self.patch_size)
            j = np.random.randint(0, w - self.patch_size)
            low_img = low_img[i:i+self.patch_size, j:j+self.patch_size]
            high_img = high_img[i:i+self.patch_size, j:j+self.patch_size]
        else:
            low_img = cv2.resize(low_img, (self.patch_size, self.patch_size))
            high_img = cv2.resize(high_img, (self.patch_size, self.patch_size))
        
        # 转换为Tensor并归一化到 [-1, 1]
        low_tensor = torch.from_numpy(low_img).permute(2, 0, 1).float() * 2.0 - 1.0
        high_tensor = torch.from_numpy(high_img).permute(2, 0, 1).float() * 2.0 - 1.0
        
        return low_tensor, high_tensor
    
    def _load_image(self, path):
        img = cv2.imread(str(path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img.astype(np.float32) / 255.0

# ======================
# 6. 混合损失函数
# ======================
class HybridLoss(nn.Module):
    """
    创新点：结合像素级、感知级和亮度对齐的混合损失
    """
    def __init__(self, device):
        super().__init__()
        self.mse_loss = nn.MSELoss()
        self.l1_loss = nn.L1Loss()
        
        # 感知损失 (Perceptual Loss)
        vgg = vgg16(pretrained=True).features[:16].eval().to(device)
        for param in vgg.parameters():
            param.requires_grad = False
        self.vgg = vgg
        self.perceptual_weight = 0.1
        
        # GT-Mean Loss: 对齐整体亮度
        self.gt_mean_weight = 0.05
        
    def forward(self, pred, target):
        # 1. 像素级损失
        pixel_loss = self.l1_loss(pred, target)
        
        # 2. 感知损失 - 修正：将 [-1,1] 转为 [0,1]
        def denorm(x):
            return (x + 1.0) / 2.0
        
        pred_vgg = denorm(pred)
        target_vgg = denorm(target)
        pred_feat = self.vgg(pred_vgg)
        target_feat = self.vgg(target_vgg)
        perceptual_loss = self.mse_loss(pred_feat, target_feat) * self.perceptual_weight
        
        # 3. GT-Mean Loss: 对齐整体亮度
        gt_mean_loss = self.mse_loss(
            torch.mean(pred, dim=[1,2,3]), 
            torch.mean(target, dim=[1,2,3])
        ) * self.gt_mean_weight
        
        total_loss = pixel_loss + perceptual_loss + gt_mean_loss
        return total_loss, {
            'pixel': pixel_loss.item(),
            'perceptual': perceptual_loss.item(),
            'gt_mean': gt_mean_loss.item()
        }

# ======================
# 7. 训练器
# ======================
class RD_DualNetTrainer:
    def __init__(self, model, train_loader, val_loader, device, save_dir):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        self.criterion = HybridLoss(device)
        self.optimizer = AdamW(self.model.parameters(), lr=2e-4, weight_decay=1e-4)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100, eta_min=1e-6
        )
        
    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()
            
            output = self.model(data)
            loss, loss_dict = self.criterion(output, target)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            if batch_idx % 50 == 0:
                print(f'Epoch {epoch} [{batch_idx}/{len(self.train_loader)}] '
                      f'Loss: {loss.item():.6f} | '
                      f'Pixel: {loss_dict["pixel"]:.6f} | '
                      f'Percep: {loss_dict["perceptual"]:.6f}')
        
        self.scheduler.step()
        return total_loss / len(self.train_loader)

    def validate(self):
        """简单的验证循环"""
        self.model.eval()
        val_loss = 0
        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss, _ = self.criterion(output, target)
                val_loss += loss.item()
        return val_loss / len(self.val_loader)


# # ======================
# # 8. 新增：评估与调优函数
# # ======================
# def evaluate_and_tune(model, eval_dir, device):
#     """
#     使用 evaluation 目录中的配对图像来“调整”模型。
#     此处的“调整”指计算一个全局亮度缩放因子 gamma，用于后处理。
#     """
#     model.eval()
#     eval_path = Path(eval_dir)
#     input_files = sorted(list(eval_path.glob("*input*")))
#     gt_files = sorted(list(eval_path.glob("*gt*")))
    
#     if len(input_files) != len(gt_files):
#         raise ValueError("Evaluation directory must have equal number of 'input' and 'gt' images.")
    
#     gamma_sum = 0.0
#     count = 0
    
#     with torch.no_grad():
#         for in_file, gt_file in zip(input_files, gt_files):
#             # 加载图像
#             in_img = cv2.imread(str(in_file))
#             in_img = cv2.cvtColor(in_img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
#             in_tensor = torch.from_numpy(in_img).permute(2, 0, 1).float().unsqueeze(0) * 2.0 - 1.0
#             in_tensor = in_tensor.to(device)
            
#             gt_img = cv2.imread(str(gt_file))
#             gt_mean = gt_img.mean()
            
#             # 模型预测
#             enhanced = model(in_tensor)
#             # 转回 [0, 255] 范围计算均值
#             enhanced_np = ((enhanced.squeeze().cpu().numpy() + 1.0) / 2.0 * 255.0).clip(0, 255)
#             enhanced_mean = enhanced_np.mean()
            
#             # 计算亮度缩放因子 (简单线性对齐)
#             if enhanced_mean > 1:
#                 gamma = gt_mean / enhanced_mean
#                 gamma_sum += gamma
#                 count += 1
    
#     if count > 0:
#         avg_gamma = gamma_sum / count
#         print(f"Computed average brightness adjustment factor (gamma): {avg_gamma:.4f}")
#         return avg_gamma
#     else:
#         print("Warning: No valid images for tuning. Using gamma=1.0")
#         return 1.0


# # ======================
# # 9. 新增：增强并保存函数
# # ======================
# def enhance_and_save(model, input_dir, gamma, device):
#     """
#     对 input_dir 中的所有图像进行增强，并保存为 '原图名称_gt.png'
#     """
#     model.eval()
#     input_path = Path(input_dir)
#     output_path = input_path  # 保存在同一目录
    
#     image_files = []
#     for ext in ['*.jpg', '*.png', '*.jpeg']:
#         image_files.extend(input_path.glob(ext))
    
#     with torch.no_grad():
#         for img_file in image_files:
#             # 加载图像
#             img = cv2.imread(str(img_file))
#             img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
#             img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float().unsqueeze(0) * 2.0 - 1.0
#             img_tensor = img_tensor.to(device)
            
#             # 模型预测
#             enhanced = model(img_tensor)
            
#             # 应用亮度调整
#             enhanced = enhanced * gamma
            
#             # 保存图像
#             # 构建新文件名: 原文件名_gt.png
#             stem = img_file.stem
#             new_name = f"{stem}_gt.png"
#             save_path = output_path / new_name
            
#             # 使用 torchvision.utils.save_image 保存
#             # 注意: save_image 默认处理 [0,1] 或 [-1,1] 范围，normalize=True 会自动处理
#             save_image(enhanced, str(save_path), normalize=True)
#             print(f"Saved enhanced image to: {save_path}")
# # ======================
# # 8. 新增：评估与调优函数 (修正版 - 支持大图)
# # ======================
# def evaluate_and_tune(model, eval_dir, device, max_size=768):
#     """
#     使用 evaluation 目录中的配对图像来“调整”模型。
#     此处的“调整”指计算一个全局亮度缩放因子 gamma，用于后处理。
#     为避免显存溢出，图像会被下采样到 max_size x max_size。
#     """
#     model.eval()
#     eval_path = Path(eval_dir)
#     input_files = sorted([f for f in eval_path.glob("*") if "input" in f.name and f.suffix.lower() in ['.jpg', '.png', '.jpeg']])
#     gt_files = sorted([f for f in eval_path.glob("*") if "gt" in f.name and f.suffix.lower() in ['.jpg', '.png', '.jpeg']])
    
#     if len(input_files) != len(gt_files):
#         raise ValueError(f"Evaluation directory must have equal number of 'input' and 'gt' images. Found {len(input_files)} input and {len(gt_files)} gt.")
    
#     gamma_sum = 0.0
#     count = 0
    
#     with torch.no_grad():
#         for in_file, gt_file in zip(input_files, gt_files):
#             print(f"Processing for tuning: {in_file.name}")
#             # --- 加载并下采样输入图像 ---
#             in_img = cv2.imread(str(in_file))
#             in_img = cv2.cvtColor(in_img, cv2.COLOR_BGR2RGB)
#             h, w = in_img.shape[:2]
#             # 计算缩放比例
#             scale = min(max_size / h, max_size / w, 1.0)
#             if scale < 1.0:
#                 new_h, new_w = int(h * scale), int(w * scale)
#                 in_img_resized = cv2.resize(in_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
#             else:
#                 in_img_resized = in_img
#             in_img_resized = in_img_resized.astype(np.float32) / 255.0
            
#             in_tensor = torch.from_numpy(in_img_resized).permute(2, 0, 1).float().unsqueeze(0) * 2.0 - 1.0
#             in_tensor = in_tensor.to(device)
            
#             # --- 加载 GT 图像并计算其原始均值 (用于亮度对齐) ---
#             gt_img = cv2.imread(str(gt_file))
#             gt_mean = gt_img.mean()
            
#             # --- 模型预测 ---
#             enhanced = model(in_tensor)
            
#             # --- 转回 [0, 255] 范围计算均值 ---
#             enhanced_np = ((enhanced.squeeze().cpu().numpy() + 1.0) / 2.0 * 255.0).clip(0, 255)
#             enhanced_mean = enhanced_np.mean()
            
#             # --- 计算亮度缩放因子 (简单线性对齐) ---
#             if enhanced_mean > 1:
#                 gamma = gt_mean / enhanced_mean
#                 gamma_sum += gamma
#                 count += 1
#                 print(f"  GT Mean: {gt_mean:.2f}, Enhanced Mean: {enhanced_mean:.2f}, Gamma: {gamma:.4f}")
    
#     if count > 0:
#         avg_gamma = gamma_sum / count
#         print(f"\nComputed average brightness adjustment factor (gamma): {avg_gamma:.4f}")
#         return avg_gamma
#     else:
#         print("Warning: No valid images for tuning. Using gamma=1.0")
#         return 1.0


# # ======================
# # 9. 新增：增强并保存函数 (修正版 - 支持大图)
# # ======================
# def enhance_and_save(model, input_dir, gamma, device, max_size=768):
#     """
#     对 input_dir 中的所有图像进行增强，并保存为 '原图名称_gt.png'
#     为避免显存溢出，图像会被下采样到 max_size x max_size 进行处理。
#     """
#     model.eval()
#     input_path = Path(input_dir)
#     output_path = input_path  # 保存在同一目录
    
#     image_files = []
#     for ext in ['*.jpg', '*.png', '*.jpeg']:
#         image_files.extend(input_path.glob(ext))
    
#     with torch.no_grad():
#         for img_file in image_files:
#             print(f"Enhancing: {img_file.name}")
#             # --- 加载原始图像 ---
#             img = cv2.imread(str(img_file))
#             orig_h, orig_w = img.shape[:2]
#             img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
#             # --- 下采样到处理尺寸 ---
#             scale = min(max_size / orig_h, max_size / orig_w, 1.0)
#             if scale < 1.0:
#                 proc_h, proc_w = int(orig_h * scale), int(orig_w * scale)
#                 img_resized = cv2.resize(img_rgb, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
#             else:
#                 img_resized = img_rgb
#                 proc_h, proc_w = orig_h, orig_w
                
#             img_resized = img_resized.astype(np.float32) / 255.0
#             img_tensor = torch.from_numpy(img_resized).permute(2, 0, 1).float().unsqueeze(0) * 2.0 - 1.0
#             img_tensor = img_tensor.to(device)
            
#             # --- 模型预测 ---
#             enhanced = model(img_tensor)
            
#             # --- 应用亮度调整 ---
#             enhanced = enhanced * gamma
            
#             # --- 转换回 [0, 1] 的 numpy 数组 ---
#             enhanced_np = ((enhanced.squeeze().cpu().numpy() + 1.0) / 2.0).clip(0, 1)
#             enhanced_np = (enhanced_np * 255).astype(np.uint8)
#             enhanced_np = enhanced_np.transpose(1, 2, 0) # HWC
            
#             # --- 上采样回原始尺寸 (如果需要) ---
#             if scale < 1.0:
#                 final_img = cv2.resize(enhanced_np, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
#             else:
#                 final_img = enhanced_np
                
#             # --- 转回 BGR 保存 ---
#             final_img_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
            
#             # --- 构建新文件名并保存 ---
#             stem = img_file.stem
#             new_name = f"{stem}_gt.png"
#             save_path = output_path / new_name
#             cv2.imwrite(str(save_path), final_img_bgr)
#             print(f"  Saved to: {save_path}")
# ======================
# 8. 新增：评估与调优函数 (V2 - 学习仿射变换)
# ======================
def evaluate_and_tune(model, eval_dir, device, max_size=768):
    """
    使用 evaluation 目录中的配对图像来学习一个全局颜色变换。
    1. 对每对 (input, gt) 图像，下采样后用模型增强 input。
    2. 计算增强结果与 gt 之间的像素级差异。
    3. 通过线性回归，学习一个 3x3 的颜色变换矩阵 (gain) 和 3x1 的偏置 (bias)，
       使得: corrected_enhanced = gain @ enhanced + bias ≈ gt
    4. 返回学习到的 gain 和 bias。
    """
    model.eval()
    eval_path = Path(eval_dir)
    input_files = sorted([f for f in eval_path.glob("*") if "input" in f.name.lower() and f.suffix.lower() in ['.jpg', '.png', '.jpeg']])
    gt_files = sorted([f for f in eval_path.glob("*") if "gt" in f.name.lower() and f.suffix.lower() in ['.jpg', '.png', '.jpeg']])
    
    if len(input_files) != len(gt_files):
        raise ValueError(f"Evaluation directory must have equal number of 'input' and 'gt' images. Found {len(input_files)} input and {len(gt_files)} gt.")
    
    print(f"Found {len(input_files)} pairs for evaluation and tuning.")
    
    # 用于存储所有像素样本
    all_enhanced_pixels = []
    all_gt_pixels = []
    
    with torch.no_grad():
        for in_file, gt_file in zip(input_files, gt_files):
            print(f"Analyzing pair: {in_file.name} <-> {gt_file.name}")
            # --- 加载并下采样输入图像 ---
            in_img = cv2.imread(str(in_file))
            in_img = cv2.cvtColor(in_img, cv2.COLOR_BGR2RGB)
            h, w = in_img.shape[:2]
            scale = min(max_size / h, max_size / w, 1.0)
            if scale < 1.0:
                new_h, new_w = int(h * scale), int(w * scale)
                in_img_resized = cv2.resize(in_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                in_img_resized = in_img
            in_img_resized = in_img_resized.astype(np.float32) / 255.0
            
            in_tensor = torch.from_numpy(in_img_resized).permute(2, 0, 1).float().unsqueeze(0) * 2.0 - 1.0
            in_tensor = in_tensor.to(device)
            
            # --- 加载 GT 图像 ---
            gt_img = cv2.imread(str(gt_file))
            gt_img = cv2.cvtColor(gt_img, cv2.COLOR_BGR2RGB)
            if scale < 1.0:
                gt_img_resized = cv2.resize(gt_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                gt_img_resized = gt_img
            gt_img_resized = gt_img_resized.astype(np.float32) / 255.0
            
            # --- 模型预测 ---
            enhanced = model(in_tensor)
            enhanced_np = ((enhanced.squeeze().cpu().numpy() + 1.0) / 2.0).clip(0, 1) # [C, H, W]
            enhanced_np = enhanced_np.transpose(1, 2, 0) # [H, W, C]
            
            # --- 收集像素用于线性回归 ---
            # 将 [H, W, C] reshape 为 [N, C]
            enhanced_pixels = enhanced_np.reshape(-1, 3)
            gt_pixels = gt_img_resized.reshape(-1, 3)
            
            all_enhanced_pixels.append(enhanced_pixels)
            all_gt_pixels.append(gt_pixels)
    
    # 合并所有样本
    X = np.vstack(all_enhanced_pixels) # Shape: [N_total, 3]
    Y = np.vstack(all_gt_pixels)       # Shape: [N_total, 3]
    
    print(f"Total pixels for regression: {X.shape[0]}")
    
    # --- 线性回归: Y = X @ W^T + b ---
    # 为了使用标准的线性回归公式，我们在 X 上加一列 1 来吸收偏置项
    X_with_bias = np.hstack([X, np.ones((X.shape[0], 1))]) # Shape: [N, 4]
    # 现在求解: Y = X_with_bias @ Theta, where Theta = [[W], [b]] (4x3 matrix)
    # 使用最小二乘法: Theta = (X^T X)^-1 X^T Y
    try:
        Theta = LA.lstsq(X_with_bias, Y, rcond=None)[0] # Shape: [4, 3]
        gain = Theta[:3, :].T  # Shape: [3, 3] (因为 Y = X@W^T + b, 所以 W^T = Theta[:3, :])
        bias = Theta[3, :]     # Shape: [3,]
        print("Successfully learned color transformation matrix and bias.")
        print(f"Gain Matrix:\n{gain}")
        print(f"Bias Vector:\n{bias}")
    except np.linalg.LinAlgError as e:
        print(f"Linear regression failed: {e}. Falling back to identity transform.")
        gain = np.eye(3, dtype=np.float32)
        bias = np.zeros(3, dtype=np.float32)
    
    return gain, bias


# ======================
# 9. 新增：增强并保存函数 (V2 - 应用学习到的变换)
# ======================
def enhance_and_save(model, input_dir, gain, bias, device, max_size=768):
    """
    对 input_dir 中的所有图像进行增强，并应用学习到的颜色变换。
    最终结果会上采样回原始尺寸。
    """
    model.eval()
    input_path = Path(input_dir)
    output_path = input_path
    
    image_files = []
    for ext in ['*.jpg', '*.png', '*.jpeg']:
        image_files.extend(input_path.glob(ext))
    
    # 将 gain, bias 转为 numpy 以便在 CPU 上快速计算
    gain = gain.astype(np.float32)
    bias = bias.astype(np.float32)
    
    with torch.no_grad():
        for img_file in image_files:
            print(f"Enhancing: {img_file.name}")
            # --- 加载原始图像 ---
            img = cv2.imread(str(img_file))
            orig_h, orig_w = img.shape[:2]
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # --- 下采样到处理尺寸 ---
            scale = min(max_size / orig_h, max_size / orig_w, 1.0)
            if scale < 1.0:
                proc_h, proc_w = int(orig_h * scale), int(orig_w * scale)
                img_resized = cv2.resize(img_rgb, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
            else:
                img_resized = img_rgb
                proc_h, proc_w = orig_h, orig_w
                
            img_resized = img_resized.astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_resized).permute(2, 0, 1).float().unsqueeze(0) * 2.0 - 1.0
            img_tensor = img_tensor.to(device)
            
            # --- 模型预测 ---
            enhanced = model(img_tensor)
            enhanced_np = ((enhanced.squeeze().cpu().numpy() + 1.0) / 2.0).clip(0, 1) # [C, H, W]
            enhanced_np = enhanced_np.transpose(1, 2, 0) # [H, W, C]
            
            # --- 应用学习到的颜色变换: corrected = gain @ pixel + bias ---
            # Reshape for matrix multiplication
            H, W, C = enhanced_np.shape
            enhanced_flat = enhanced_np.reshape(-1, C) # [N, 3]
            corrected_flat = enhanced_flat @ gain.T + bias # [N, 3]
            corrected_np = corrected_flat.reshape(H, W, C) # [H, W, 3]
            corrected_np = np.clip(corrected_np, 0, 1)
            
            # --- 转换为 uint8 并上采样回原始尺寸 ---
            corrected_np_uint8 = (corrected_np * 255).astype(np.uint8)
            if scale < 1.0:
                final_img = cv2.resize(corrected_np_uint8, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
            else:
                final_img = corrected_np_uint8
                
            # --- 转回 BGR 保存 ---
            final_img_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
            
            # --- 保存 ---
            stem = img_file.stem
            new_name = f"{stem}_gt.png"
            save_path = output_path / new_name
            cv2.imwrite(str(save_path), final_img_bgr)
            print(f"  Saved to: {save_path}")

# ======================
# 10. 主函数
# ======================
def main():
    parser = argparse.ArgumentParser(description='RD-DualNet Training and Enhancement')
    parser.add_argument('--low_dir', type=str, help='Directory of low-light images for training')
    parser.add_argument('--high_dir', type=str, help='Directory of high-quality (GT) images for training')
    parser.add_argument('--val_low_dir', type=str, help='Validation low-light dir')
    parser.add_argument('--val_high_dir', type=str, help='Validation GT dir')
    parser.add_argument('--eval_dir', type=str, default='~/test/evaluation', help='Directory for evaluation and tuning')
    parser.add_argument('--input_dir', type=str, default='~/test/input', help='Directory of input images to enhance')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--save_dir', type=str, default='rd_dualnet_results')
    parser.add_argument('--mode', type=str, choices=['train', 'enhance'], default='enhance', 
                        help='Mode: "train" to train the model, "enhance" to enhance images')
    args = parser.parse_args()
    
    # 展开用户目录
    eval_dir = os.path.expanduser(args.eval_dir)
    input_dir = os.path.expanduser(args.input_dir)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    if args.mode == 'train':
        if not args.low_dir or not args.high_dir:
            raise ValueError("For training mode, --low_dir and --high_dir are required.")
        
        # 数据集
        train_dataset = PairedDataset(args.low_dir, args.high_dir)
        train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=4)
        
        val_loader = None
        if args.val_low_dir and args.val_high_dir:
            val_dataset = PairedDataset(args.val_low_dir, args.val_high_dir)
            val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False)
        
        # 模型
        model = RD_DualNet()
        
        # 训练器
        trainer = RD_DualNetTrainer(model, train_loader, val_loader, device, args.save_dir)
        
        # 训练
        best_val_loss = float('inf')
        for epoch in range(1, args.epochs + 1):
            train_loss = trainer.train_epoch(epoch)
            print(f'Epoch {epoch}: Train Loss = {train_loss:.6f}')
            
            if val_loader is not None:
                val_loss = trainer.validate()
                print(f'Epoch {epoch}: Val Loss = {val_loss:.6f}')
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    torch.save(model.state_dict(), f'{args.save_dir}/best_model.pth')
            
            if epoch % 20 == 0:
                torch.save(model.state_dict(), f'{args.save_dir}/model_epoch_{epoch}.pth')
        
        torch.save(model.state_dict(), f'{args.save_dir}/final_model.pth')
    
    # elif args.mode == 'enhance':
    #     # 加载预训练模型 (这里为了演示，我们使用一个新初始化的模型)
    #     # 在实际应用中，你应该加载一个训练好的权重文件
    #     model = RD_DualNet()
    #     # 如果有训练好的模型，取消下面的注释并指定路径
    #     # model.load_state_dict(torch.load('path/to/your/best_model.pth', map_location=device))
    #     model.to(device)
        
    #     # 1. 使用 evaluation 目录进行调优
    #     gamma = evaluate_and_tune(model, eval_dir, device)
        
    #     # 2. 对 input 目录中的图像进行增强和保存
    #     enhance_and_save(model, input_dir, gamma, device)
    elif args.mode == 'enhance':
        # 加载预训练模型 (这里为了演示，我们使用一个新初始化的模型)
        # 在实际应用中，你应该加载一个训练好的权重文件
        model = RD_DualNet()
        # 如果有训练好的模型，取消下面的注释并指定路径
        # model.load_state_dict(torch.load('path/to/your/best_model.pth', map_location=device))
        model.to(device)
        
        # 1. 使用 evaluation 目录进行调优，学习变换
        gain, bias = evaluate_and_tune(model, eval_dir, device)
        
        # 2. 对 input 目录中的图像进行增强、变换和保存
        enhance_and_save(model, input_dir, gain, bias, device)


if __name__ == "__main__":
    main()