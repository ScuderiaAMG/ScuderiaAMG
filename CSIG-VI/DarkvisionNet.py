import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
import cv2
import os
from pathlib import Path
import time
from typing import List, Tuple
import argparse

class PhysicalGuidedAttention(nn.Module):
    """基于物理成像模型的注意力机制"""
    def __init__(self, channels):
        super().__init__()
        self.luminance_conv = nn.Conv2d(3, 1, 3, padding=1)
        self.noise_estimate = nn.Conv2d(3, channels, 3, padding=1)
        self.attention_conv = nn.Conv2d(channels * 2, channels, 1)
        
    def forward(self, x):
        # 估计亮度分布
        luminance = torch.sigmoid(self.luminance_conv(x))
        
        # 估计噪声水平
        noise_level = F.avg_pool2d(
            torch.var(x, dim=1, keepdim=True), 3, stride=1, padding=1
        )
        noise_weight = self.noise_estimate(noise_level)
        
        # 结合亮度和噪声信息生成注意力权重
        attention = torch.cat([luminance.expand_as(noise_weight), noise_weight], dim=1)
        attention_weights = torch.sigmoid(self.attention_conv(attention))
        
        return attention_weights

class MultiScaleResidualBlock(nn.Module):
    """多尺度残差块"""
    def __init__(self, channels):
        super().__init__()
        
        # 不同尺度的卷积
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.conv2 = nn.Conv2d(channels, channels, 5, padding=2)
        self.conv3 = nn.Conv2d(channels, channels, 7, padding=3)
        
        # 注意力机制
        self.attention = PhysicalGuidedAttention(channels)
        
        # 融合层
        self.fusion = nn.Conv2d(channels * 3, channels, 1)
        
    def forward(self, x):
        attn_weights = self.attention(x)
        
        # 多尺度特征提取
        feat1 = F.relu(self.conv1(x))
        feat2 = F.relu(self.conv2(x))
        feat3 = F.relu(self.conv3(x))
        
        # 特征融合
        fused = self.fusion(torch.cat([feat1, feat2, feat3], dim=1))
        
        # 应用注意力权重
        weighted = fused * attn_weights
        
        return x + weighted  # 残差连接

class EnhancementBranch(nn.Module):
    """亮度增强分支"""
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, 7, padding=3),
            nn.ReLU(),
            nn.Conv2d(64, 128, 5, padding=2, stride=2),
            nn.ReLU(),
            nn.Conv2d(128, 256, 3, padding=1, stride=2),
            nn.ReLU()
        )
        
        self.res_blocks = nn.Sequential(
            *[MultiScaleResidualBlock(256) for _ in range(8)]
        )
        
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 5, stride=2, padding=2, output_padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 3, 7, padding=3),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        enc = self.encoder(x)
        res = self.res_blocks(enc)
        dec = self.decoder(res)
        return dec

class DenoisingBranch(nn.Module):
    """噪声抑制分支"""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(),
            *[nn.Sequential(
                nn.Conv2d(64, 64, 3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU()
            ) for _ in range(5)],
            nn.Conv2d(64, 3, 3, padding=1)
        )
        
    def forward(self, x):
        return self.net(x)

class DarkVisionNet(nn.Module):
    """主网络"""
    def __init__(self):
        super().__init__()
        self.enhance_branch = EnhancementBranch()
        self.denoise_branch = DenoisingBranch()
        
        # 融合网络
        self.fusion = nn.Sequential(
            nn.Conv2d(6, 32, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 3, 3, padding=1),
            nn.Tanh()
        )
        
    def forward(self, x):
        # 增强分支
        enhanced = self.enhance_branch(x)
        
        # 去噪分支
        denoised = self.denoise_branch(x)
        
        # 特征融合
        fused = self.fusion(torch.cat([enhanced, denoised], dim=1))
        
        # 保持颜色一致性
        result = x + fused  # 残差学习
        
        return torch.clamp(result, 0, 1)

class DarkImageDataset(Dataset):
    """暗光图像数据集"""
    def __init__(self, input_dir, patch_size=256):
        self.input_dir = Path(input_dir)
        self.image_paths = list(self.input_dir.glob("*.jpg")) + list(self.input_dir.glob("*.png"))
        self.patch_size = patch_size
        
    def __len__(self):
        return len(self.image_paths) * 10  # 每张图像生成10个patch
    
    def __getitem__(self, idx):
        img_idx = idx % len(self.image_paths)
        img_path = self.image_paths[img_idx]
        
        # 读取图像
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.astype(np.float32) / 255.0
        
        # 数据增强
        image = self.augment_image(image)
        
        # 随机裁剪
        h, w = image.shape[:2]
        if h > self.patch_size and w > self.patch_size:
            i = np.random.randint(0, h - self.patch_size)
            j = np.random.randint(0, w - self.patch_size)
            image = image[i:i+self.patch_size, j:j+self.patch_size]
        else:
            image = cv2.resize(image, (self.patch_size, self.patch_size))
        
        # 转换为tensor
        image = torch.from_numpy(image).permute(2, 0, 1).float()
        
        return image, image  # 自监督学习，输入输出相同
    
    def augment_image(self, image):
        """数据增强"""
        # 随机亮度调整（模拟不同暗光程度）
        if np.random.random() > 0.5:
            gamma = np.random.uniform(1.5, 3.0)
            image = image ** gamma
        
        # 随机添加噪声
        if np.random.random() > 0.5:
            noise_level = np.random.uniform(0.01, 0.05)
            noise = np.random.normal(0, noise_level, image.shape)
            image = image + noise
            image = np.clip(image, 0, 1)
        
        return image

class ColorConsistencyLoss(nn.Module):
    """颜色一致性损失"""
    def __init__(self):
        super().__init__()
        
    def forward(self, pred, target):
        # 颜色分布一致性
        pred_gray = torch.mean(pred, dim=1, keepdim=True)
        target_gray = torch.mean(target, dim=1, keepdim=True)
        
        color_loss = F.mse_loss(pred_gray, target_gray)
        
        # 色彩饱和度约束
        saturation_pred = torch.std(pred, dim=1)
        saturation_target = torch.std(target, dim=1)
        saturation_loss = F.mse_loss(saturation_pred, saturation_target)
        
        return color_loss + saturation_loss

class EnhancementTrainer:
    """训练器"""
    def __init__(self, model, train_loader, device):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.device = device
        
        # 损失函数
        self.mse_loss = nn.MSELoss()
        self.ssim_loss = SSIMLoss()
        self.color_loss = ColorConsistencyLoss()
        
        # 优化器
        self.optimizer = Adam(self.model.parameters(), lr=1e-4)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100
        )
        
    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            
            output = self.model(data)
            
            # 多目标损失
            mse_loss = self.mse_loss(output, target)
            ssim_loss = self.ssim_loss(output, target)
            color_loss = self.color_loss(output, target)
            
            # 总损失
            loss = mse_loss + 0.5 * ssim_loss + 0.1 * color_loss
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 100 == 0:
                print(f'Epoch: {epoch} [{batch_idx}/{len(self.train_loader)}] '
                      f'Loss: {loss.item():.6f}')
        
        self.scheduler.step()
        return total_loss / len(self.train_loader)

class SSIMLoss(nn.Module):
    """SSIM损失函数"""
    def __init__(self, window_size=11, size_average=True):
        super().__init__()
        self.window_size = window_size
        self.size_average = size_average
        self.channel = 1
        self.window = self.create_window(window_size, self.channel)

    def forward(self, img1, img2):
        (_, channel, _, _) = img1.size()

        if channel == self.channel and self.window.data.type() == img1.data.type():
            window = self.window
        else:
            window = self.create_window(self.window_size, channel)
            
            if img1.is_cuda:
                window = window.cuda(img1.get_device())
            window = window.type_as(img1)
            
            self.window = window
            self.channel = channel

        return 1 - self._ssim(img1, img2, window, self.window_size, channel, self.size_average)

    def _ssim(self, img1, img2, window, window_size, channel, size_average=True):
        mu1 = F.conv2d(img1, window, padding=window_size//2, groups=channel)
        mu2 = F.conv2d(img2, window, padding=window_size//2, groups=channel)

        mu1_sq = mu1.pow(2)
        mu2_sq = mu2.pow(2)
        mu1_mu2 = mu1 * mu2

        sigma1_sq = F.conv2d(img1*img1, window, padding=window_size//2, groups=channel) - mu1_sq
        sigma2_sq = F.conv2d(img2*img2, window, padding=window_size//2, groups=channel) - mu2_sq
        sigma12 = F.conv2d(img1*img2, window, padding=window_size//2, groups=channel) - mu1_mu2

        C1 = 0.01**2
        C2 = 0.03**2

        ssim_map = ((2*mu1_mu2 + C1)*(2*sigma12 + C2)) / ((mu1_sq + mu2_sq + C1)*(sigma1_sq + sigma2_sq + C2))

        if size_average:
            return ssim_map.mean()
        else:
            return ssim_map.mean(1).mean(1).mean(1)

    def create_window(self, window_size, channel):
        def gaussian(window_size, sigma):
            gauss = torch.Tensor([exp(-(x - window_size//2)**2/float(2*sigma**2)) for x in range(window_size)])
            return gauss/gauss.sum()
        
        _1D_window = gaussian(window_size, 1.5).unsqueeze(1)
        _2D_window = _1D_window.mm(_1D_window.t()).float().unsqueeze(0).unsqueeze(0)
        window = _2D_window.expand(channel, 1, window_size, window_size).contiguous()
        return window

def main():
    parser = argparse.ArgumentParser(description='DarkVision-Net Training')
    parser.add_argument('--input_dir', type=str, required=True, help='Input image directory')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=8, help='Batch size')
    parser.add_argument('--save_dir', type=str, default='results', help='Save directory')
    
    args = parser.parse_args()
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # 创建数据集
    dataset = DarkImageDataset(args.input_dir)
    train_loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=4)
    
    # 创建模型
    model = DarkVisionNet()
    
    # 训练器
    trainer = EnhancementTrainer(model, train_loader, device)
    
    # 训练循环
    os.makedirs(args.save_dir, exist_ok=True)
    
    start_time = time.time()
    for epoch in range(1, args.epochs + 1):
        avg_loss = trainer.train_epoch(epoch)
        print(f'Epoch {epoch}: Average Loss = {avg_loss:.6f}')
        
        # 保存模型
        if epoch % 10 == 0:
            torch.save(model.state_dict(), f'{args.save_dir}/model_epoch_{epoch}.pth')
            
        # 时间检查
        elapsed_time = time.time() - start_time
        if elapsed_time > 4 * 24 * 3600:  # 4天限制
            print("Time limit reached. Stopping training.")
            break
    
    # 保存最终模型
    torch.save(model.state_dict(), f'{args.save_dir}/final_model.pth')

if __name__ == "__main__":
    main()