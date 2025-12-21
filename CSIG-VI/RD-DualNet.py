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
from torchvision.models.feature_extraction import create_feature_extractor

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
        
        # 增强分支 (侧重细节和亮度)
        self.enhance_branch = nn.Sequential(
            *[LightweightMultiScaleBlock(self.channels) for _ in range(4)]
        )
        
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
        
        # 双分支处理
        enhanced_feat = self.enhance_branch(shallow, x)
        denoised_feat = self.denoise_branch(shallow)
        
        # 特征融合
        fused_feat = torch.cat([enhanced_feat, denoised_feat], dim=1)
        residual = self.fusion(fused_feat)
        
        # 残差学习: 输出 = 输入 + 残差
        output = x + residual
        return torch.clamp(output, -1, 1) # 注意: Ground Truth 需要归一化到 [-1, 1]

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
        
        # GT-Mean Loss: 对齐整体亮度 [[1]]
        self.gt_mean_weight = 0.05
        
    def forward(self, pred, target):
        # 1. 像素级损失
        pixel_loss = self.l1_loss(pred, target)
        
        # 2. 感知损失
        pred_feat = self.vgg(pred)
        target_feat = self.vgg(target)
        perceptual_loss = self.mse_loss(pred_feat, target_feat) * self.perceptual_weight
        
        # 3. GT-Mean Loss: 对齐整体亮度 [[1]]
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

# ======================
# 8. 主函数
# ======================
def main():
    parser = argparse.ArgumentParser(description='RD-DualNet Training')
    parser.add_argument('--low_dir', type=str, required=True, help='Directory of low-light images')
    parser.add_argument('--high_dir', type=str, required=True, help='Directory of high-quality (GT) images')
    parser.add_argument('--val_low_dir', type=str, help='Validation low-light dir')
    parser.add_argument('--val_high_dir', type=str, help='Validation GT dir')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--save_dir', type=str, default='rd_dualnet_results')
    args = parser.parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
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

if __name__ == "__main__":
    main()