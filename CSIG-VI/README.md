# CSIG-VI

2025 “Camera Academic Star” Imaging Algorithm Technology Competition

## Attempt.py

预估无监督学习算法无法完全生成合规图像，计划更换算法

## RD-DualNet.py

Retinex-DCP Guided Dual-Branch Network with Hybrid Supervision (RD-DualNet)

采用有监督学习，直接学习从暗图到 Ground Truth 的映射，这是获得高分的最可靠路径 。

通过融合 Retinex 和 DCP 先验，网络内部的注意力机制具有明确的物理意义，能更精准地分离和增强细节与光照。

使用 深度可分离卷积 和 通道注意力 ，在保证性能的同时大幅降低模型复杂度，符合移动端应用背景 

HybridLoss 结合了L1损失（细节保真）、感知损失（VGG特征对齐，提升视觉质量 ）和 GT-Mean Loss（整体亮度对齐 ），全方位逼近 Ground Truth。

使用 AdamW 优化器、梯度裁剪和余弦退火调度器，确保训练稳定高效。

此方案在算法逻辑上是创新的，并且完全针对赛题的评分标准（与Ground Truth对比）进行了优化。