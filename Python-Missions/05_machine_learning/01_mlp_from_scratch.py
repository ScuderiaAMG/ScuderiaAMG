#!/usr/bin/env python3
"""
从零手写多层感知机 (MLP) —— 仅使用 NumPy
涵盖：全连接层、激活函数、损失函数、前向/反向传播、
      梯度下降优化器、Mini-batch 训练、Xavier/He 初始化、
      Dropout 正则化、Batch Normalization
"""

import numpy as np
from typing import Any, Callable, Literal

rng = np.random.default_rng(42)


# ============================================================
# §1  激活函数与损失函数
# ============================================================

class Activation:
    """激活函数基类。"""

    @staticmethod
    @np.vectorize
    def forward(x: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    @staticmethod
    @np.vectorize
    def backward(x: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class ReLU:
    @staticmethod
    def forward(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def backward(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(np.float64)


class Sigmoid:
    @staticmethod
    def forward(x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    @staticmethod
    def backward(x: np.ndarray) -> np.ndarray:
        s = Sigmoid.forward(x)
        return s * (1 - s)


class Tanh:
    @staticmethod
    def forward(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    @staticmethod
    def backward(x: np.ndarray) -> np.ndarray:
        return 1 - np.tanh(x) ** 2


class LeakyReLU:
    def __init__(self, alpha: float = 0.01) -> None:
        self.alpha = alpha

    def forward(self, x: np.ndarray) -> np.ndarray:
        return np.where(x > 0, x, self.alpha * x)

    def backward(self, x: np.ndarray) -> np.ndarray:
        dx = np.ones_like(x)
        dx[x <= 0] = self.alpha
        return dx


class Softmax:
    @staticmethod
    def forward(x: np.ndarray) -> np.ndarray:
        """沿最后一维做 softmax。"""
        shifted = x - np.max(x, axis=-1, keepdims=True)
        exp_x = np.exp(shifted)
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    @staticmethod
    def backward(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
        """当与交叉熵联合使用时，梯度简化为 y_pred - y_true。"""
        return y_pred - y_true


class Loss:
    """损失函数。"""

    @staticmethod
    def mean_squared_error(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        return float(np.mean((y_pred - y_true) ** 2))

    @staticmethod
    def mse_gradient(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
        return 2 * (y_pred - y_true) / y_true.shape[1]

    @staticmethod
    def cross_entropy(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """y_true 是 one-hot, y_pred 是 softmax 输出。"""
        eps = 1e-12
        return float(-np.mean(np.sum(y_true * np.log(y_pred + eps), axis=1)))

    @staticmethod
    def binary_cross_entropy(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        eps = 1e-12
        return float(-np.mean(
            y_true * np.log(y_pred + eps) + (1 - y_true) * np.log(1 - y_pred + eps)
        ))


# ============================================================
# §2  Layer 基类与全连接层
# ============================================================

class Layer:
    """神经网络层基类。"""

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        raise NotImplementedError

    def backward(self, dout: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def update(self, optimizer: "Optimizer") -> None:
        pass


class Linear(Layer):
    """全连接层 y = xW + b。"""

    def __init__(self, in_features: int, out_features: int,
                 init: str = "he") -> None:
        self.in_features = in_features
        self.out_features = out_features

        # 权重初始化
        if init == "he":
            std = np.sqrt(2.0 / in_features)
        elif init == "xavier":
            std = np.sqrt(1.0 / in_features)
        else:
            std = 0.01

        self.W = rng.normal(0, std, (in_features, out_features))
        self.b = np.zeros((1, out_features))

        self.dW: np.ndarray = np.zeros_like(self.W)
        self.db: np.ndarray = np.zeros_like(self.b)
        self.x: np.ndarray | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        self.x = x
        return x @ self.W + self.b

    def backward(self, dout: np.ndarray) -> np.ndarray:
        batch_size = dout.shape[0]
        self.dW = (self.x.T @ dout) / batch_size  # type: ignore[operator]
        self.db = np.sum(dout, axis=0, keepdims=True) / batch_size
        return dout @ self.W.T

    def update(self, optimizer: "Optimizer") -> None:
        self.W = optimizer.update(self.W, self.dW, f"{id(self)}_W")
        self.b = optimizer.update(self.b, self.db, f"{id(self)}_b")


class Dropout(Layer):
    """Dropout 正则化层。"""

    def __init__(self, p: float = 0.5) -> None:
        self.p = p                             # 保留概率
        self.mask: np.ndarray | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        if training:
            self.mask = (rng.random(x.shape) < self.p).astype(np.float64) / self.p
            return x * self.mask
        return x

    def backward(self, dout: np.ndarray) -> np.ndarray:
        return dout * self.mask                # type: ignore[operator]


class BatchNorm1d(Layer):
    """一维批量归一化。"""

    def __init__(self, num_features: int, eps: float = 1e-5,
                 momentum: float = 0.9) -> None:
        self.eps = eps
        self.momentum = momentum
        self.gamma = np.ones((1, num_features))
        self.beta = np.zeros((1, num_features))
        self.running_mean = np.zeros((1, num_features))
        self.running_var = np.ones((1, num_features))

        # 缓存反向传播中间结果
        self.x: np.ndarray | None = None
        self.x_hat: np.ndarray | None = None
        self.mu: np.ndarray | None = None
        self.var: np.ndarray | None = None

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        self.x = x
        if training:
            self.mu = np.mean(x, axis=0, keepdims=True)
            self.var = np.var(x, axis=0, keepdims=True)
            self.x_hat = (x - self.mu) / np.sqrt(self.var + self.eps)
            # 更新 running statistics
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * self.mu
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * self.var
        else:
            self.x_hat = (x - self.running_mean) / np.sqrt(self.running_var + self.eps)

        return self.gamma * self.x_hat + self.beta

    def backward(self, dout: np.ndarray) -> np.ndarray:
        batch_size = dout.shape[0]
        x_hat = self.x_hat  # type: ignore[has-type]
        mu = self.mu        # type: ignore[has-type]
        var = self.var      # type: ignore[has-type]

        dgamma = np.sum(dout * x_hat, axis=0, keepdims=True)
        dbeta = np.sum(dout, axis=0, keepdims=True)

        dx_hat = dout * self.gamma
        dvar = np.sum(dx_hat * (self.x - mu), axis=0, keepdims=True) * (-0.5) * (var + self.eps) ** (-1.5)  # type: ignore[operator]
        dmu = (np.sum(dx_hat * (-1 / np.sqrt(var + self.eps)), axis=0, keepdims=True)
               + dvar * np.mean(-2 * (self.x - mu), axis=0, keepdims=True))  # type: ignore[operator]

        dx = (dx_hat / np.sqrt(var + self.eps)
              + dvar * 2 * (self.x - mu) / batch_size  # type: ignore[operator]
              + dmu / batch_size)

        self.dgamma = dgamma
        self.dbeta = dbeta
        return dx

    def update(self, optimizer: "Optimizer") -> None:
        self.gamma = optimizer.update(self.gamma, self.dgamma, f"{id(self)}_gamma")
        self.beta = optimizer.update(self.beta, self.dbeta, f"{id(self)}_beta")


# ============================================================
# §3  优化器
# ============================================================

class Optimizer:
    def update(self, param: np.ndarray, grad: np.ndarray, key: str) -> np.ndarray:
        raise NotImplementedError


class SGD(Optimizer):
    def __init__(self, lr: float = 0.01, momentum: float = 0.0,
                 weight_decay: float = 0.0) -> None:
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.velocity: dict[str, np.ndarray] = {}

    def update(self, param: np.ndarray, grad: np.ndarray, key: str) -> np.ndarray:
        if self.weight_decay > 0:
            grad = grad + self.weight_decay * param

        if self.momentum > 0:
            if key not in self.velocity:
                self.velocity[key] = np.zeros_like(grad)
            self.velocity[key] = self.momentum * self.velocity[key] - self.lr * grad
            return param + self.velocity[key]
        return param - self.lr * grad


class Adam(Optimizer):
    def __init__(self, lr: float = 0.001, betas: tuple[float, float] = (0.9, 0.999),
                 eps: float = 1e-8, weight_decay: float = 0.0) -> None:
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.m: dict[str, np.ndarray] = {}
        self.v: dict[str, np.ndarray] = {}
        self.t: int = 0

    def update(self, param: np.ndarray, grad: np.ndarray, key: str) -> np.ndarray:
        if self.weight_decay > 0:
            grad = grad + self.weight_decay * param

        self.t += 1
        if key not in self.m:
            self.m[key] = np.zeros_like(grad)
            self.v[key] = np.zeros_like(grad)

        self.m[key] = self.beta1 * self.m[key] + (1 - self.beta1) * grad
        self.v[key] = self.beta2 * self.v[key] + (1 - self.beta2) * grad ** 2

        m_hat = self.m[key] / (1 - self.beta1 ** self.t)
        v_hat = self.v[key] / (1 - self.beta2 ** self.t)

        return param - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


# ============================================================
# §4  Sequential 模型与训练循环
# ============================================================

class Sequential:
    """顺序容器 — 堆叠各层。"""

    def __init__(self, layers: list[Layer]) -> None:
        self.layers = layers

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x, training)
        return x

    def backward(self, dout: np.ndarray) -> np.ndarray:
        for layer in reversed(self.layers):
            dout = layer.backward(dout)
        return dout

    def update(self, optimizer: Optimizer) -> None:
        for layer in self.layers:
            layer.update(optimizer)

    def parameters(self) -> list[np.ndarray]:
        params: list[np.ndarray] = []
        for layer in self.layers:
            if hasattr(layer, "W"):
                params.append(layer.W)  # type: ignore[attr-defined]
            if hasattr(layer, "b"):
                params.append(layer.b)  # type: ignore[attr-defined]
        return params


class Trainer:
    """模型训练器。"""

    def __init__(self, model: Sequential, loss_fn: Callable,
                 loss_grad_fn: Callable, optimizer: Optimizer) -> None:
        self.model = model
        self.loss_fn = loss_fn
        self.loss_grad_fn = loss_grad_fn
        self.optimizer = optimizer
        self.train_losses: list[float] = []
        self.val_losses: list[float] = []

    def train_epoch(self, X: np.ndarray, y: np.ndarray,
                    batch_size: int = 32) -> float:
        n = X.shape[0]
        indices = rng.permutation(n)
        total_loss = 0.0

        for start in range(0, n, batch_size):
            batch_idx = indices[start:start + batch_size]
            X_batch = X[batch_idx]
            y_batch = y[batch_idx]

            # 前向
            y_pred = self.model.forward(X_batch, training=True)
            loss = self.loss_fn(y_pred, y_batch)

            # 反向
            dout = self.loss_grad_fn(y_pred, y_batch)
            self.model.backward(dout)

            # 更新
            self.model.update(self.optimizer)
            total_loss += loss * len(batch_idx)

        return total_loss / n

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        y_pred = self.model.forward(X, training=False)
        return float(self.loss_fn(y_pred, y))

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.forward(X, training=False)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray,
            X_val: np.ndarray | None = None,
            y_val: np.ndarray | None = None,
            epochs: int = 50, batch_size: int = 32,
            verbose: bool = True) -> None:
        for epoch in range(epochs):
            train_loss = self.train_epoch(X_train, y_train, batch_size)
            self.train_losses.append(train_loss)

            if X_val is not None and y_val is not None:
                val_loss = self.evaluate(X_val, y_val)
                self.val_losses.append(val_loss)

            if verbose and (epoch + 1) % 10 == 0:
                msg = f"Epoch {epoch+1:3d}/{epochs} | train_loss: {train_loss:.4f}"
                if X_val is not None:
                    msg += f" | val_loss: {self.val_losses[-1]:.4f}"
                print(msg)


# ============================================================
# §5  实战演示
# ============================================================

def generate_moons_dataset(n_samples: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """生成半月形二分类数据集。"""
    n = n_samples // 2
    theta = np.linspace(0, np.pi, n)
    r = rng.normal(1, 0.1, n)
    X1 = np.column_stack([r * np.cos(theta), r * np.sin(theta)])

    theta2 = np.linspace(0, np.pi, n)
    r2 = rng.normal(1, 0.1, n)
    X2 = np.column_stack([r2 * np.cos(theta2) + 1.0, -r2 * np.sin(theta2) + 0.5])

    X = np.vstack([X1, X2])
    y = np.hstack([np.zeros(n), np.ones(n)])
    # One-hot for cross-entropy
    y_onehot = np.eye(2)[y.astype(int)]

    # Shuffle
    idx = rng.permutation(len(X))
    return X[idx], y_onehot[idx]


def demo_mlp_classification() -> None:
    print("=" * 60)
    print("MLP 二分类演示 (Moons 数据集)")
    print("=" * 60)

    X, y = generate_moons_dataset(1200)

    # 划分数据集
    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    print(f"训练集: {X_train.shape}, 验证集: {X_val.shape}")

    # 构建模型
    model = Sequential([
        Linear(2, 64, init="he"),
        BatchNorm1d(64),
        ReLU(),
        Dropout(p=0.5),

        Linear(64, 32, init="he"),
        BatchNorm1d(32),
        ReLU(),
        Dropout(p=0.3),

        Linear(32, 16, init="he"),
        ReLU(),

        Linear(16, 2, init="xavier"),
    ])

    # 组合 softmax + cross-entropy 的联合梯度
    def ce_loss(y_pred: np.ndarray, y_true: np.ndarray) -> float:
        probs = Softmax.forward(y_pred)
        return Loss.cross_entropy(probs, y_true)

    def ce_grad(y_pred: np.ndarray, y_true: np.ndarray) -> np.ndarray:
        probs = Softmax.forward(y_pred)
        return Softmax.backward(probs, y_true)

    optimizer = Adam(lr=0.001, weight_decay=1e-5)
    trainer = Trainer(model, ce_loss, ce_grad, optimizer)

    print("\n开始训练...")
    trainer.fit(X_train, y_train, X_val, y_val, epochs=80, batch_size=64, verbose=True)

    # 最终评估
    train_acc = float(np.mean(
        np.argmax(trainer.predict(X_train), axis=1) == np.argmax(y_train, axis=1)
    ))
    val_acc = float(np.mean(
        np.argmax(trainer.predict(X_val), axis=1) == np.argmax(y_val, axis=1)
    ))
    print(f"\n训练准确率: {train_acc:.4f}")
    print(f"验证准确率: {val_acc:.4f}")


def demo_mlp_regression() -> None:
    print("\n" + "=" * 60)
    print("MLP 回归演示 (Sine 函数拟合)")
    print("=" * 60)

    # 生成数据
    X = np.linspace(-2 * np.pi, 2 * np.pi, 500).reshape(-1, 1)
    y = np.sin(X) + 0.1 * rng.standard_normal(X.shape)

    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    # 回归模型
    model = Sequential([
        Linear(1, 32, init="he"),
        ReLU(),
        Linear(32, 32, init="he"),
        ReLU(),
        Linear(32, 16, init="he"),
        ReLU(),
        Linear(16, 1, init="xavier"),
    ])

    optimizer = Adam(lr=0.01)
    trainer = Trainer(model, Loss.mean_squared_error,
                      Loss.mse_gradient, optimizer)

    print("训练 Sine 拟合...")
    trainer.fit(X_train, y_train, X_val, y_val, epochs=200, batch_size=32,
                verbose=True)

    # 在几个点上测试
    test_points = np.array([[-np.pi], [0], [np.pi / 2], [np.pi]])
    preds = trainer.predict(test_points)
    for x_val, pred, true_val in zip(test_points.flatten(), preds.flatten(),
                                      np.sin(test_points).flatten()):
        print(f"  x={x_val:6.2f} | pred={pred:.4f} | true={true_val:.4f}")


# ============================================================
# §6  XOR 问题与深度必要性演示
# ============================================================

def demo_xor_problem() -> None:
    print("\n" + "=" * 60)
    print("XOR 问题：单层 vs 多层的对比")
    print("=" * 60)

    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([[1, 0], [0, 1], [0, 1], [1, 0]])  # one-hot: class 0 vs class 1

    # 单层线性模型（无法拟合 XOR）
    model_linear = Sequential([
        Linear(2, 2, init="xavier"),
    ])
    opt_linear = Adam(lr=0.1)
    trainer_linear = Trainer(model_linear,
                             lambda yp, yt: Loss.cross_entropy(Softmax.forward(yp), yt),
                             lambda yp, yt: Softmax.backward(Softmax.forward(yp), yt),
                             opt_linear)
    trainer_linear.fit(X, y, epochs=100, batch_size=4, verbose=False)
    preds_linear = np.argmax(trainer_linear.predict(X), axis=1)
    print(f"线性模型预测: {preds_linear} (期望交替 0,1,1,0)")
    print(f"线性模型正确率: {np.mean(preds_linear == np.argmax(y, axis=1))}")

    # 带隐藏层的 MLP
    model_mlp = Sequential([
        Linear(2, 8, init="he"),
        ReLU(),
        Linear(8, 2, init="xavier"),
    ])
    opt = Adam(lr=0.1)
    trainer_mlp = Trainer(model_mlp,
                          lambda yp, yt: Loss.cross_entropy(Softmax.forward(yp), yt),
                          lambda yp, yt: Softmax.backward(Softmax.forward(yp), yt),
                          opt)
    trainer_mlp.fit(X, y, epochs=200, batch_size=4, verbose=False)
    preds_mlp = np.argmax(trainer_mlp.predict(X), axis=1)
    print(f"\nMLP 预测:     {preds_mlp} (期望 0,1,1,0)")
    print(f"MLP 正确率:   {np.mean(preds_mlp == np.argmax(y, axis=1))}")


if __name__ == "__main__":
    demo_mlp_classification()
    demo_mlp_regression()
    demo_xor_problem()
    print("\n✅ MLP 从零实现全部执行完毕!")
