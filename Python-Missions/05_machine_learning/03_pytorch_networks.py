#!/usr/bin/env python3
"""
PyTorch 深度学习 —— 从基础到高级网络架构
涵盖：Tensor 基础、autograd、nn.Module、DataLoader、
      CNN (ResNet)、RNN/LSTM、GAN、训练流程最佳实践
所有代码可独立运行（除 GAN 需要 torchvision）
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset, random_split
import numpy as np
import math
from typing import Any


# ============================================================
# §1  Tensor 基础与 autograd
# ============================================================

def demo_tensor_basics() -> None:
    print("=" * 60)
    print("§1  Tensor 基础与 autograd")
    print("=" * 60)

    # 创建 Tensor
    a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    b = torch.randn(2, 3)
    c = torch.zeros(3, 4, dtype=torch.long)
    d = torch.eye(4)
    e = torch.arange(0, 10, 2)
    f = torch.linspace(0, 1, 5)

    print(f"tensor a:\n{a}")
    print(f"randn(2,3):\n{b}")
    print(f"zeros(3,4):\n{c}")
    print(f"arange(0,10,2): {e}")

    # 运算
    print(f"\na @ a:\n{a @ a}")
    print(f"a * a (element-wise):\n{a * a}")
    print(f"torch.cat([a,a], dim=0):\n{torch.cat([a, a], dim=0)}")
    print(f"torch.stack([a,a], dim=0):\n{torch.stack([a, a], dim=0)}")

    # 形状操作
    x = torch.randn(2, 3, 4)
    print(f"\noriginal shape: {x.shape}")
    print(f"view(2, 12):    {x.view(2, 12).shape}")
    print(f"reshape(6, 4):  {x.reshape(6, 4).shape}")
    print(f"transpose(0,2): {x.transpose(0, 2).shape}")
    print(f"permute(2,0,1): {x.permute(2, 0, 1).shape}")
    print(f"squeeze:        {torch.randn(1, 3, 1, 5).squeeze().shape}")
    print(f"unsqueeze:      {torch.randn(3, 5).unsqueeze(0).shape}")

    # Autograd 演示
    w = torch.tensor([2.0], requires_grad=True)
    b = torch.tensor([1.0], requires_grad=True)
    x_in = torch.tensor([3.0])

    y_pred = x_in * w + b                       # 前向
    y_true = torch.tensor([10.0])
    loss = (y_pred - y_true) ** 2                # MSE
    loss.backward()                              # 反向

    print(f"\nAutograd: w.grad={w.grad.item():.1f}, b.grad={b.grad.item():.1f}")
    print(f"  手动验证: dL/dw = 2*(x*w+b-y)*x = {2*(3*2+1-10)*3:.1f}")

    # 梯度清零
    w.grad.zero_()
    b.grad.zero_()
    print(f"zero_() 后: w.grad={w.grad.item()}")


# ============================================================
# §2  nn.Module — 自定义网络
# ============================================================

class MLP(nn.Module):
    """可配置的多层感知机。"""

    def __init__(self, input_dim: int, hidden_dims: list[int],
                 output_dim: int, dropout: float = 0.0,
                 activation: nn.Module = nn.ReLU) -> None:
        super().__init__()

        layers: list[nn.Module] = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, h_dim),
                activation(),
                nn.BatchNorm1d(h_dim),
                nn.Dropout(dropout),
            ])
            prev_dim = h_dim
        layers.append(nn.Linear(prev_dim, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class CNN_Classifier(nn.Module):
    """简单 CNN 分类器（适用于 MNIST/CIFAR 风格输入）。"""

    def __init__(self, in_channels: int = 1, num_classes: int = 10) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            # Block 1: 28x28 -> 14x14
            nn.Conv2d(in_channels, 32, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.25),

            # Block 2: 14x14 -> 7x7
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.25),
        )
        # 动态计算全连接输入维度
        self._fc_input_dim: int | None = None
        self.fc = nn.Sequential(
            nn.Linear(64 * 7 * 7, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def demo_nn_module() -> None:
    print("\n" + "=" * 60)
    print("§2  nn.Module — 自定义网络")
    print("=" * 60)

    # MLP
    mlp = MLP(input_dim=784, hidden_dims=[256, 128], output_dim=10,
              dropout=0.3)
    print(f"MLP: \n{mlp}")
    dummy = torch.randn(4, 784)
    out = mlp(dummy)
    print(f"MLP 输入 {dummy.shape} -> 输出 {out.shape}")

    # CNN
    cnn = CNN_Classifier(in_channels=1, num_classes=10)
    print(f"\nCNN: {sum(p.numel() for p in cnn.parameters()):,} 参数")
    dummy_img = torch.randn(4, 1, 28, 28)
    cnn_out = cnn(dummy_img)
    print(f"CNN 输入 {dummy_img.shape} -> 输出 {cnn_out.shape}")


# ============================================================
# §3  ResNet 残差块
# ============================================================

class ResidualBlock(nn.Module):
    """标准残差块 (ResNet)。"""

    def __init__(self, in_channels: int, out_channels: int,
                 stride: int = 1, downsample: nn.Module | None = None) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3,
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3,
                               stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.downsample = downsample

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return F.relu(out)


class ResNet(nn.Module):
    """类 ResNet-18 架构。"""

    def __init__(self, block: type[ResidualBlock] = ResidualBlock,
                 layers: list[int] = [2, 2, 2, 2],
                 num_classes: int = 10) -> None:
        super().__init__()
        self.in_channels = 64

        self.conv1 = nn.Conv2d(3, 64, 7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(3, stride=2, padding=1)

        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)

    def _make_layer(self, block: type[ResidualBlock],
                    out_channels: int, blocks: int,
                    stride: int = 1) -> nn.Sequential:
        downsample = None
        if stride != 1 or self.in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels, 1,
                          stride=stride, bias=False),
                nn.BatchNorm2d(out_channels),
            )

        layers_list: list[nn.Module] = []
        layers_list.append(
            block(self.in_channels, out_channels, stride, downsample)
        )
        self.in_channels = out_channels
        for _ in range(1, blocks):
            layers_list.append(
                block(self.in_channels, out_channels)
            )
        return nn.Sequential(*layers_list)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def demo_resnet() -> None:
    print("\n" + "=" * 60)
    print("§3  ResNet 残差网络")
    print("=" * 60)

    resnet = ResNet(ResidualBlock, [2, 2, 2, 2], num_classes=1000)
    n_params = sum(p.numel() for p in resnet.parameters())
    print(f"ResNet-18: {n_params:,} 参数")

    dummy = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        out = resnet(dummy)
    print(f"输入 {dummy.shape} -> 输出 {out.shape}")


# ============================================================
# §4  RNN / LSTM / GRU
# ============================================================

class LSTMModel(nn.Module):
    """LSTM 用于序列分类/回归。"""

    def __init__(self, input_size: int, hidden_size: int,
                 num_layers: int, num_classes: int,
                 dropout: float = 0.0, bidirectional: bool = False) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional

        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout,
            bidirectional=bidirectional,
        )
        directions = 2 if bidirectional else 1
        self.fc = nn.Linear(hidden_size * directions, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        batch_size = x.size(0)
        h0 = torch.zeros(self.num_layers * (2 if self.bidirectional else 1),
                         batch_size, self.hidden_size, device=x.device)
        c0 = torch.zeros_like(h0)

        out, (hn, cn) = self.lstm(x, (h0, c0))
        # 取最后一个时间步
        last_out = out[:, -1, :]
        return self.fc(last_out)


class GRUModel(nn.Module):
    """GRU 版本 — 参数更少。"""

    def __init__(self, input_size: int, hidden_size: int,
                 num_layers: int, num_classes: int) -> None:
        super().__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers,
                          batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, hn = self.gru(x)
        last_out = out[:, -1, :]
        return self.fc(last_out)


def demo_rnn() -> None:
    print("\n" + "=" * 60)
    print("§4  RNN / LSTM / GRU")
    print("=" * 60)

    # LSTM
    lstm = LSTMModel(input_size=128, hidden_size=256,
                     num_layers=2, num_classes=10,
                     dropout=0.3, bidirectional=True)
    print(f"LSTM: {sum(p.numel() for p in lstm.parameters()):,} 参数")

    dummy_seq = torch.randn(8, 50, 128)          # (batch=8, seq_len=50, features=128)
    with torch.no_grad():
        lstm_out = lstm(dummy_seq)
    print(f"LSTM 输入 {dummy_seq.shape} -> 输出 {lstm_out.shape}")

    # GRU
    gru = GRUModel(input_size=128, hidden_size=256,
                   num_layers=2, num_classes=10)
    print(f"GRU: {sum(p.numel() for p in gru.parameters()):,} 参数")

    with torch.no_grad():
        gru_out = gru(dummy_seq)
    print(f"GRU 输入 {dummy_seq.shape} -> 输出 {gru_out.shape}")


# ============================================================
# §5  GAN — 生成对抗网络
# ============================================================

class Generator(nn.Module):
    """DCGAN 风格的生成器。"""

    def __init__(self, latent_dim: int = 100, img_channels: int = 1,
                 feature_maps: int = 64) -> None:
        super().__init__()
        self.net = nn.Sequential(
            # latent_dim x 1 x 1 -> feature_maps*8 x 4 x 4
            nn.ConvTranspose2d(latent_dim, feature_maps * 8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(feature_maps * 8),
            nn.ReLU(True),

            # feature_maps*8 x 4x4 -> feature_maps*4 x 8x8
            nn.ConvTranspose2d(feature_maps * 8, feature_maps * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 4),
            nn.ReLU(True),

            # feature_maps*4 x 8x8 -> feature_maps*2 x 16x16
            nn.ConvTranspose2d(feature_maps * 4, feature_maps * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 2),
            nn.ReLU(True),

            # feature_maps*2 x 16x16 -> img_channels x 32x32
            nn.ConvTranspose2d(feature_maps * 2, img_channels, 4, 2, 1, bias=False),
            nn.Tanh(),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z.unsqueeze(-1).unsqueeze(-1))


class Discriminator(nn.Module):
    """DCGAN 风格的判别器。"""

    def __init__(self, img_channels: int = 1, feature_maps: int = 64) -> None:
        super().__init__()
        self.net = nn.Sequential(
            # img_channels x 32x32 -> feature_maps x 16x16
            nn.Conv2d(img_channels, feature_maps, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, True),

            # feature_maps x 16x16 -> feature_maps*2 x 8x8
            nn.Conv2d(feature_maps, feature_maps * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 2),
            nn.LeakyReLU(0.2, True),

            # feature_maps*2 x 8x8 -> feature_maps*4 x 4x4
            nn.Conv2d(feature_maps * 2, feature_maps * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 4),
            nn.LeakyReLU(0.2, True),

            # feature_maps*4 x 4x4 -> 1
            nn.Conv2d(feature_maps * 4, 1, 4, 1, 0, bias=False),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).view(-1, 1)


def demo_gan() -> None:
    print("\n" + "=" * 60)
    print("§5  GAN — 生成对抗网络")
    print("=" * 60)

    latent_dim = 100
    gen = Generator(latent_dim=latent_dim, img_channels=1)
    disc = Discriminator(img_channels=1)

    print(f"Generator: {sum(p.numel() for p in gen.parameters()):,} 参数")
    print(f"Discriminator: {sum(p.numel() for p in disc.parameters()):,} 参数")

    # 前向测试
    with torch.no_grad():
        z = torch.randn(4, latent_dim)
        fake_imgs = gen(z)
        real_imgs = torch.randn(4, 1, 32, 32)
        fake_pred = disc(fake_imgs)
        real_pred = disc(real_imgs)

    print(f"噪声 {z.shape} -> 图像 {fake_imgs.shape}")
    print(f"判别器: real_pred={real_pred.flatten().tolist()}, "
          f"fake_pred={fake_pred.flatten().tolist()}")

    # 损失函数
    criterion = nn.BCELoss()
    real_labels = torch.ones(4, 1)
    fake_labels = torch.zeros(4, 1)

    d_loss_real = criterion(real_pred, real_labels)
    d_loss_fake = criterion(fake_pred, fake_labels)
    d_loss = d_loss_real + d_loss_fake

    # 生成器损失（最小化 log(1-D(G(z))) 等效于最大化 log(D(G(z)))）
    g_loss = criterion(fake_pred, real_labels)   # 欺骗判别器

    print(f"D loss: {d_loss.item():.4f}, G loss: {g_loss.item():.4f}")


# ============================================================
# §6  Dataset / DataLoader
# ============================================================

class SyntheticDataset(Dataset):
    """合成数据集示例。"""

    def __init__(self, n_samples: int = 1000, n_features: int = 20,
                 n_classes: int = 3, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        self.X = torch.tensor(
            rng.standard_normal((n_samples, n_features)), dtype=torch.float32
        )
        self.y = torch.tensor(
            rng.integers(0, n_classes, n_samples), dtype=torch.long
        )

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


def demo_training_loop() -> None:
    print("\n" + "=" * 60)
    print("§6  完整训练流程")
    print("=" * 60)

    # 数据集
    dataset = SyntheticDataset(n_samples=2000, n_features=20, n_classes=3)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False)

    print(f"训练批次数: {len(train_loader)}, 验证批次数: {len(val_loader)}")

    # 模型 / 优化器 / 损失函数 / 调度器
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MLP(20, [64, 32], 3, dropout=0.2).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2
    )
    criterion = nn.CrossEntropyLoss()

    print(f"设备: {device}")
    print(f"优化器: AdamW, 调度器: CosineAnnealingWarmRestarts")

    # 训练
    epochs = 15
    train_losses: list[float] = []
    val_accs: list[float] = []

    for epoch in range(epochs):
        # 训练阶段
        model.train()
        total_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item() * len(X_batch)
        scheduler.step()
        avg_loss = total_loss / len(train_ds)
        train_losses.append(avg_loss)

        # 验证阶段
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                output = model(X_batch)
                preds = output.argmax(dim=1)
                correct += (preds == y_batch).sum().item()
                total += len(y_batch)
        val_acc = correct / total
        val_accs.append(val_acc)

        if (epoch + 1) % 5 == 0:
            lr = optimizer.param_groups[0]["lr"]
            print(f"Epoch {epoch+1:3d} | loss: {avg_loss:.4f} | "
                  f"val_acc: {val_acc:.4f} | lr: {lr:.2e}")

    print(f"\n最终验证准确率: {val_accs[-1]:.4f}")

    # 保存与加载模型
    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epochs,
        "val_acc": val_accs[-1],
    }, "checkpoint.pt")
    print("checkpoint 已保存到 checkpoint.pt")

    # 加载
    checkpoint = torch.load("checkpoint.pt", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    print("checkpoint 加载成功")


if __name__ == "__main__":
    demo_tensor_basics()
    demo_nn_module()
    demo_resnet()
    demo_rnn()
    demo_gan()
    demo_training_loop()
    print("\n✅ PyTorch 神经网络篇全部执行完毕!")
