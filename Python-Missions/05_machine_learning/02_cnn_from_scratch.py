#!/usr/bin/env python3
"""
从零手写卷积神经网络 (CNN) —— 仅使用 NumPy
涵盖：im2col 卷积、最大/平均池化、Flatten、LeNet-5 风格架构、
      MNIST 数字分类完整训练流程
"""

import numpy as np
from typing import Any

rng = np.random.default_rng(42)


# ============================================================
# §1  im2col — 将卷积转化为矩阵乘法
# ============================================================

def im2col(
    x: np.ndarray,
    kernel_h: int,
    kernel_w: int,
    stride: int = 1,
    pad: int = 0,
) -> np.ndarray:
    """
    将 4D 图像张量 (N, C, H, W) 转换为 2D 矩阵用于高效卷积。

    返回:
        col: shape (N * out_h * out_w, C * kernel_h * kernel_w)
    """
    N, C, H, W = x.shape

    if pad > 0:
        x_padded = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)),
                          mode="constant")
    else:
        x_padded = x

    out_h = (H + 2 * pad - kernel_h) // stride + 1
    out_w = (W + 2 * pad - kernel_w) // stride + 1

    # 使用 stride_tricks 提取所有滑动窗口
    shape = (N, C, out_h, out_w, kernel_h, kernel_w)
    strides = (
        x_padded.strides[0],                      # N
        x_padded.strides[1],                      # C
        x_padded.strides[2] * stride,             # out_h
        x_padded.strides[3] * stride,             # out_w
        x_padded.strides[2],                      # kernel_h
        x_padded.strides[3],                      # kernel_w
    )

    windows = np.lib.stride_tricks.as_strided(
        x_padded, shape=shape, strides=strides, writeable=False
    )

    # 重排为 (N, out_h, out_w, C, kernel_h, kernel_w)
    # 然后 reshape 为 (N * out_h * out_w, C * kernel_h * kernel_w)
    col = windows.transpose(0, 2, 3, 1, 4, 5).reshape(
        N * out_h * out_w, -1
    )
    return col


def col2im(
    col: np.ndarray,
    x_shape: tuple[int, int, int, int],
    kernel_h: int,
    kernel_w: int,
    stride: int = 1,
    pad: int = 0,
) -> np.ndarray:
    """
    im2col 的逆操作：将梯度矩阵还原为图像形状。
    当多个滑动窗口贡献到同一像素时，对梯度进行累加。
    """
    N, C, H, W = x_shape
    out_h = (H + 2 * pad - kernel_h) // stride + 1
    out_w = (W + 2 * pad - kernel_w) // stride + 1

    # 重塑为 (N, out_h, out_w, C, kernel_h, kernel_w)
    col_reshaped = col.reshape(N, out_h, out_w, C, kernel_h, kernel_w)
    # 转换为 (N, C, out_h, out_w, kernel_h, kernel_w)
    col_reshaped = col_reshaped.transpose(0, 3, 1, 2, 4, 5)

    img = np.zeros((N, C, H + 2 * pad + stride - 1, W + 2 * pad + stride - 1))

    for y in range(out_h):
        for x in range(out_w):
            y_start = y * stride
            x_start = x * stride
            img[:, :, y_start:y_start + kernel_h, x_start:x_start + kernel_w] += \
                col_reshaped[:, :, y, x, :, :]

    # 裁剪到有效区域（移除多余的填充行/列）
    return img[:, :, pad:H + pad, pad:W + pad]


# ============================================================
# §2  卷积层
# ============================================================

class Conv2d:
    """2D 卷积层。"""

    def __init__(self, in_channels: int, out_channels: int,
                 kernel_size: int | tuple[int, int],
                 stride: int = 1, padding: int = 0,
                 init: str = "he") -> None:
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = (kernel_size, kernel_size) if isinstance(kernel_size, int) else kernel_size
        self.stride = stride
        self.padding = padding

        kh, kw = self.kernel_size
        fan_in = in_channels * kh * kw

        if init == "he":
            std = np.sqrt(2.0 / fan_in)
        elif init == "xavier":
            std = np.sqrt(1.0 / fan_in)
        else:
            std = 0.01

        self.W = rng.normal(0, std,
                            (out_channels, in_channels, kh, kw))
        self.b = np.zeros((out_channels,))

        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self.x: np.ndarray | None = None
        self.col: np.ndarray | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """
        x: (N, C, H, W)
        返回: (N, out_channels, out_h, out_w)
        """
        self.x = x
        N, C, H, W = x.shape
        out_channels, in_channels, kh, kw = self.W.shape

        out_h = (H + 2 * self.padding - kh) // self.stride + 1
        out_w = (W + 2 * self.padding - kw) // self.stride + 1

        self.col = im2col(x, kh, kw, self.stride, self.padding)            # (N*out_h*out_w, C*kh*kw)
        W_col = self.W.reshape(out_channels, -1).T                         # (C*kh*kw, out_channels)

        out = self.col @ W_col + self.b                                    # (N*out_h*out_w, out_channels)
        out = out.reshape(N, out_h, out_w, out_channels).transpose(0, 3, 1, 2)
        return out

    def backward(self, dout: np.ndarray) -> np.ndarray:
        """
        dout: (N, out_channels, out_h, out_w)
        返回: dx: (N, C, H, W)
        """
        N, out_channels, out_h, out_w = dout.shape
        out_channels_, in_channels, kh, kw = self.W.shape

        # dout 重排为 (N*out_h*out_w, out_channels)
        dout_reshaped = dout.transpose(0, 2, 3, 1).reshape(-1, out_channels)

        # 梯度 w.r.t. W 和 b
        self.dW = (dout_reshaped.T @ self.col).reshape(self.W.shape) / N     # type: ignore[operator]
        self.db = np.sum(dout_reshaped, axis=0) / N

        # 梯度 w.r.t. x
        W_col = self.W.reshape(out_channels, -1)                             # (out_channels, C*kh*kw)
        dcol = dout_reshaped @ W_col                                         # (N*out_h*out_w, C*kh*kw)

        dx = col2im(dcol, self.x.shape, kh, kw,     # type: ignore[arg-type]
                    self.stride, self.padding)
        return dx

    def update(self, optimizer: Any) -> None:
        self.W = optimizer.update(self.W, self.dW, f"{id(self)}_W")
        self.b = optimizer.update(self.b, self.db, f"{id(self)}_b")


# ============================================================
# §3  池化层
# ============================================================

class MaxPool2d:
    """最大池化层。"""

    def __init__(self, kernel_size: int = 2, stride: int | None = None) -> None:
        self.kernel_size = kernel_size
        self.stride = stride or kernel_size
        self.argmax: np.ndarray | None = None
        self.x_shape: tuple | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        N, C, H, W = x.shape
        self.x_shape = x.shape
        kh, kw = self.kernel_size, self.kernel_size
        stride = self.stride

        out_h = (H - kh) // stride + 1
        out_w = (W - kw) // stride + 1

        col = im2col(x, kh, kw, stride, pad=0)                       # (N*out_h*out_w, C*kh*kw)
        col = col.reshape(N * out_h * out_w * C, kh * kw)

        self.argmax = np.argmax(col, axis=1)
        out = col[np.arange(len(col)), self.argmax]

        return out.reshape(N, out_h, out_w, C).transpose(0, 3, 1, 2)

    def backward(self, dout: np.ndarray) -> np.ndarray:
        """
        dout: (N, C, out_h, out_w)
        返回: dx: (N, C, H, W) — 梯度仅通过 argmax 位置
        """
        N, C, out_h, out_w = dout.shape
        H, W = self.x_shape[2], self.x_shape[3]  # type: ignore[index]
        kh = kw = self.kernel_size
        stride = self.stride

        dout_flat = dout.transpose(0, 2, 3, 1).flatten()

        dcol = np.zeros((N * out_h * out_w * C, kh * kw))
        dcol[np.arange(len(dcol)), self.argmax] = dout_flat     # type: ignore[index]

        dcol = dcol.reshape(N * out_h * out_w, C * kh * kw)

        dx = col2im(dcol, self.x_shape, kh, kw, stride, pad=0)  # type: ignore[arg-type]
        return dx

    def update(self, optimizer: Any) -> None:
        pass


class AvgPool2d:
    """平均池化层。"""

    def __init__(self, kernel_size: int = 2, stride: int | None = None) -> None:
        self.kernel_size = kernel_size
        self.stride = stride or kernel_size
        self.x_shape: tuple | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        self.x_shape = x.shape
        N, C, H, W = x.shape
        kh = kw = self.kernel_size
        stride = self.stride
        out_h = (H - kh) // stride + 1
        out_w = (W - kw) // stride + 1

        col = im2col(x, kh, kw, stride, pad=0)
        col = col.reshape(N, out_h, out_w, C, kh, kw).transpose(0, 3, 1, 2, 4, 5)
        return np.mean(col, axis=(4, 5))

    def backward(self, dout: np.ndarray) -> np.ndarray:
        N, C, out_h, out_w = dout.shape
        N_, C_, H, W = self.x_shape  # type: ignore[misc]
        kh = kw = self.kernel_size
        stride = self.stride

        dout_expanded = dout[:, :, np.newaxis, np.newaxis, :, :]
        dout_broadcast = np.broadcast_to(
            dout_expanded, (N, C, kh, kw, out_h, out_w)
        )
        dout_broadcast = dout_broadcast.transpose(0, 3, 4, 1, 2, 5)
        dcol = (dout_broadcast / (kh * kw)).reshape(N * out_h * out_w, C * kh * kw)

        dx = col2im(dcol, self.x_shape, kh, kw, stride, pad=0)  # type: ignore[arg-type]
        return dx

    def update(self, optimizer: Any) -> None:
        pass


# ============================================================
# §4  Flatten 与 ReLU
# ============================================================

class Flatten:
    def __init__(self) -> None:
        self.in_shape: tuple | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        self.in_shape = x.shape
        return x.reshape(x.shape[0], -1)

    def backward(self, dout: np.ndarray) -> np.ndarray:
        return dout.reshape(self.in_shape)      # type: ignore[return-value]

    def update(self, optimizer: Any) -> None:
        pass


class ReLU:
    def __init__(self) -> None:
        self.mask: np.ndarray | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        self.mask = (x > 0)
        return x * self.mask

    def backward(self, dout: np.ndarray) -> np.ndarray:
        return dout * self.mask                # type: ignore[operator]

    def update(self, optimizer: Any) -> None:
        pass


# 复用 mlp 中的 Linear
class Linear:
    def __init__(self, in_features: int, out_features: int,
                 init: str = "he") -> None:
        if init == "he":
            std = np.sqrt(2.0 / in_features)
        elif init == "xavier":
            std = np.sqrt(1.0 / in_features)
        else:
            std = 0.01
        self.W = rng.normal(0, std, (in_features, out_features))
        self.b = np.zeros((1, out_features))
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self.x: np.ndarray | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        self.x = x
        return x @ self.W + self.b

    def backward(self, dout: np.ndarray) -> np.ndarray:
        batch_size = dout.shape[0]
        self.dW = (self.x.T @ dout) / batch_size   # type: ignore[operator]
        self.db = np.sum(dout, axis=0, keepdims=True) / batch_size
        return dout @ self.W.T

    def update(self, optimizer: Any) -> None:
        self.W = optimizer.update(self.W, self.dW, f"{id(self)}_W")
        self.b = optimizer.update(self.b, self.db, f"{id(self)}_b")


# ============================================================
# §5  CNN Sequential & Trainer
# ============================================================

class Sequential:
    def __init__(self, layers: list[Any]) -> None:
        self.layers = layers

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x, training)
        return x

    def backward(self, dout: np.ndarray) -> np.ndarray:
        for layer in reversed(self.layers):
            dout = layer.backward(dout)
        return dout

    def update(self, optimizer: Any) -> None:
        for layer in self.layers:
            layer.update(optimizer)


class Adam:
    def __init__(self, lr: float = 0.001, betas: tuple[float, float] = (0.9, 0.999),
                 eps: float = 1e-8) -> None:
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.m: dict[str, np.ndarray] = {}
        self.v: dict[str, np.ndarray] = {}
        self.t: int = 0

    def update(self, param: np.ndarray, grad: np.ndarray, key: str) -> np.ndarray:
        self.t += 1
        if key not in self.m:
            self.m[key] = np.zeros_like(grad)
            self.v[key] = np.zeros_like(grad)

        self.m[key] = self.beta1 * self.m[key] + (1 - self.beta1) * grad
        self.v[key] = self.beta2 * self.v[key] + (1 - self.beta2) * grad ** 2

        m_hat = self.m[key] / (1 - self.beta1 ** self.t)
        v_hat = self.v[key] / (1 - self.beta2 ** self.t)

        return param - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


def one_hot(labels: np.ndarray, num_classes: int) -> np.ndarray:
    return np.eye(num_classes)[labels.astype(int)]


# ============================================================
# §6  MNIST 数据加载器
# ============================================================

def load_mnist_subset(n_train: int = 5000, n_test: int = 800) -> tuple:
    """
    生成类 MNIST 的合成数据集（避免下载真实 MNIST）。
    每个数字是一个简单的几何模式。
    """
    images_per_class_train = n_train // 10
    images_per_class_test = n_test // 10

    def generate_digit(digit: int, count: int) -> np.ndarray:
        """生成特定数字的 28x28 图像。"""
        imgs = np.zeros((count, 1, 28, 28))
        for i in range(count):
            img = np.zeros((28, 28))

            if digit == 0:
                # 椭圆环
                yy, xx = np.ogrid[-14:14, -14:14]
                mask = (xx*2/28)**2 + (yy*2/28)**2 < 0.85
                inner = (xx*2/28)**2 + (yy*2/28)**2 < 0.45
                img[mask & ~inner] = 1.0
            elif digit == 1:
                # 竖线
                img[:, 12:16] = 1.0
            elif digit == 2:
                # Z 字形
                img[3:7, 5:23] = 1.0
                img[6:24, 18:22] = 1.0
                for j in range(4, 24):
                    img[j, 20 - j + 3] = 1.0
                img[22:26, 5:23] = 1.0
            elif digit == 3:
                # S 形状
                img[3:7, 5:23] = 1.0
                img[6:12, 19:22] = 1.0
                img[12:16, 5:23] = 1.0
                img[16:22, 19:22] = 1.0
                img[22:26, 5:23] = 1.0
            elif digit == 4:
                img[3:14, 16:19] = 1.0
                img[10:14, 6:19] = 1.0
                img[3:24, 6:9] = 1.0
            elif digit == 5:
                img[3:7, 5:23] = 1.0
                img[3:14, 5:8] = 1.0
                img[12:16, 5:23] = 1.0
                img[16:22, 20:23] = 1.0
                img[22:26, 5:23] = 1.0
            elif digit == 6:
                img[3:7, 5:23] = 1.0
                img[3:24, 4:7] = 1.0
                img[12:16, 6:22] = 1.0
                img[16:22, 20:23] = 1.0
                img[22:26, 5:23] = 1.0
            elif digit == 7:
                img[3:7, 4:24] = 1.0
                for j in range(24):
                    img[j, 21 - j] = 1.0
            elif digit == 8:
                img[3:7, 5:23] = 1.0
                img[22:26, 5:23] = 1.0
                img[3:24, 4:7] = 1.0
                img[3:24, 19:22] = 1.0
                img[12:16, 5:23] = 1.0
            elif digit == 9:
                img[3:7, 5:23] = 1.0
                img[22:26, 5:23] = 1.0
                img[3:14, 19:22] = 1.0
                img[12:16, 5:23] = 1.0
                img[16:24, 4:7] = 1.0

            # 加噪
            img += rng.normal(0, 0.05, (28, 28))
            imgs[i, 0] = np.clip(img, 0, 1)
        return imgs

    X_train_list, y_train_list = [], []
    X_test_list, y_test_list = [], []

    for digit in range(10):
        X_train_list.append(generate_digit(digit, images_per_class_train))
        y_train_list.append(np.full(images_per_class_train, digit))
        X_test_list.append(generate_digit(digit, images_per_class_test))
        y_test_list.append(np.full(images_per_class_test, digit))

    X_train = np.vstack(X_train_list)
    y_train = np.hstack(y_train_list)
    X_test = np.vstack(X_test_list)
    y_test = np.hstack(y_test_list)

    # 打乱
    train_idx = rng.permutation(len(X_train))
    test_idx = rng.permutation(len(X_test))
    return X_train[train_idx], y_train[train_idx], X_test[test_idx], y_test[test_idx]


# ============================================================
# §7  LeNet-5 风格 CNN
# ============================================================

def build_lenet_like(input_channels: int = 1, num_classes: int = 10) -> Sequential:
    """构建类 LeNet-5 架构。"""
    return Sequential([
        # Block 1
        Conv2d(input_channels, 16, kernel_size=5, stride=1, padding=2, init="he"),
        ReLU(),
        MaxPool2d(kernel_size=2, stride=2),

        # Block 2
        Conv2d(16, 32, kernel_size=5, stride=1, padding=2, init="he"),
        ReLU(),
        MaxPool2d(kernel_size=2, stride=2),

        # Block 3
        Conv2d(32, 64, kernel_size=3, stride=1, padding=1, init="he"),
        ReLU(),
        AvgPool2d(kernel_size=2, stride=2),

        # Classifier
        Flatten(),
        Linear(64 * 3 * 3, 128, init="he"),
        ReLU(),
        Linear(128, num_classes, init="xavier"),
    ])


def demo_cnn_mnist() -> None:
    print("=" * 60)
    print("CNN 数字分类演示 (合成 MNIST)")
    print("=" * 60)

    # 加载数据
    print("生成合成 MNIST 数据...")
    X_train, y_train, X_test, y_test = load_mnist_subset(n_train=6000, n_test=1000)
    # 归一化
    X_train = X_train.astype(np.float64)
    X_test = X_test.astype(np.float64)

    y_train_oh = one_hot(y_train, 10)
    y_test_oh = one_hot(y_test, 10)

    print(f"训练集: {X_train.shape}, 测试集: {X_test.shape}")

    # 构建模型
    model = build_lenet_like(input_channels=1, num_classes=10)
    optimizer = Adam(lr=0.001)
    print(f"模型构建完成，总层数: {len(model.layers)}")

    # 训练
    epochs = 30
    batch_size = 64
    print(f"\n开始训练 ({epochs} epochs, batch_size={batch_size})...")

    train_losses: list[float] = []
    test_accs: list[float] = []

    for epoch in range(epochs):
        # Mini-batch SGD
        indices = rng.permutation(len(X_train))
        total_loss = 0.0

        for start in range(0, len(X_train), batch_size):
            batch_idx = indices[start:start + batch_size]
            X_batch = X_train[batch_idx]
            y_batch = y_train_oh[batch_idx]

            # 前向
            out = model.forward(X_batch, training=True)

            # softmax + cross-entropy
            shifted = out - np.max(out, axis=1, keepdims=True)
            exp_out = np.exp(shifted)
            probs = exp_out / np.sum(exp_out, axis=1, keepdims=True)

            loss = -np.mean(np.sum(y_batch * np.log(probs + 1e-12), axis=1))
            total_loss += loss * len(batch_idx)

            # 反向
            dout = (probs - y_batch) / batch_size
            model.backward(dout)
            model.update(optimizer)

        avg_loss = total_loss / len(X_train)
        train_losses.append(avg_loss)

        # 验证准确率
        test_out = model.forward(X_test, training=False)
        test_pred = np.argmax(test_out, axis=1)
        test_acc = float(np.mean(test_pred == y_test))
        test_accs.append(test_acc)

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1:3d}/{epochs} | loss: {avg_loss:.4f} | test_acc: {test_acc:.4f}")

    print(f"\n最终测试准确率: {test_accs[-1]:.4f}")

    # 打印每类准确率
    for digit in range(10):
        mask = y_test == digit
        if mask.sum() > 0:
            acc = float(np.mean(
                np.argmax(model.forward(X_test[mask], training=False), axis=1) == digit
            ))
            print(f"  数字 {digit}: {acc:.4f} ({mask.sum()} 样本)")


# ============================================================
# §8  CNN 可视化——特征图
# ============================================================

def demo_feature_maps() -> None:
    print("\n" + "=" * 60)
    print("CNN 特征图可视化")
    print("=" * 60)

    # 创建一个简单的测试图像
    img = np.zeros((1, 1, 28, 28))
    img[0, 0, 8:20, 8:12] = 1.0                  # 竖线
    img[0, 0, 12:16, 6:22] = 1.0                 # 横线

    # 小 CNN 仅用于可视化
    conv_layer = Conv2d(1, 4, kernel_size=3, stride=1, padding=1, init="he")

    # 获取特征图
    features = conv_layer.forward(img, training=False)

    print(f"输入形状: {img.shape}")
    print(f"卷积 W 形状: {conv_layer.W.shape}  (4 filters, 1 channel, 3x3)")
    print(f"特征图形状: {features.shape}  (1, 4, 28, 28)")
    print(f"特征图 1 均值: {features[0, 0].mean():.4f}")
    print(f"特征图 2 均值: {features[0, 1].mean():.4f}")
    print(f"特征图 3 均值: {features[0, 2].mean():.4f}")
    print(f"特征图 4 均值: {features[0, 3].mean():.4f}")

    # 经过 ReLU + Pool
    relu = ReLU()
    pool = MaxPool2d(2, 2)
    activated = relu.forward(features, training=False)
    pooled = pool.forward(activated, training=False)
    print(f"ReLU 后形状: {activated.shape}")
    print(f"Pool 后形状: {pooled.shape}  (1, 4, 14, 14)")


if __name__ == "__main__":
    demo_feature_maps()
    demo_cnn_mnist()
    print("\n✅ CNN 从零实现全部执行完毕!")
