import numpy as np

# 固定随机种子以便复现
np.random.seed(42)

# ==========================================
# 1. 定义神经网络的基础组件 (前向传播与反向传播)
# ==========================================

class Linear:
    def __init__(self, in_dim, out_dim):
        # He 初始化，适合 ReLU
        self.W = np.random.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros((1, out_dim))
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self.x = None

    def forward(self, x):
        self.x = x
        return np.dot(x, self.W) + self.b

    def backward(self, dout):
        # 计算相对于权重和偏差的梯度
        self.dW = np.dot(self.x.T, dout)
        self.db = np.sum(dout, axis=0, keepdims=True)
        # 计算相对于输入的梯度，传递给上一层
        dx = np.dot(dout, self.W.T)
        return dx

    def step(self, lr):
        # 梯度下降更新参数
        self.W -= lr * self.dW
        self.b -= lr * self.db

class ReLU:
    def __init__(self):
        self.x = None

    def forward(self, x):
        self.x = x
        return np.maximum(0, x)

    def backward(self, dout):
        dx = dout.copy()
        dx[self.x <= 0] = 0
        return dx

class Sigmoid:
    def __init__(self):
        self.out = None

    def forward(self, x):
        # 截断以防止溢出
        x = np.clip(x, -500, 500)
        self.out = 1.0 / (1.0 + np.exp(-x))
        return self.out

    def backward(self, dout):
        # Sigmoid 的导数: sigmoid(x) * (1 - sigmoid(x))
        return dout * self.out * (1.0 - self.out)

# ==========================================
# 2. 损失函数 (Binary Cross Entropy)
# ==========================================

def bce_loss(y_pred, y_true):
    """
    计算二元交叉熵损失及梯度
    公式: L = - 1/N * sum(y*log(y_pred) + (1-y)*log(1-y_pred))
    """
    # 裁剪预测值，避免 log(0) 导致的 NaN
    y_pred = np.clip(y_pred, 1e-7, 1.0 - 1e-7)
    N = y_pred.shape[0]
    
    # 前向损失
    loss = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    
    # 反向梯度: dL/dy_pred
    dout = (y_pred - y_true) / (y_pred * (1.0 - y_pred)) / N
    return loss, dout

# ==========================================
# 3. 序列化网络容器
# ==========================================

class Sequential:
    def __init__(self, *layers):
        self.layers = layers

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def backward(self, dout):
        # 链式法则：反向遍历层
        for layer in reversed(self.layers):
            dout = layer.backward(dout)
        return dout

    def step(self, lr):
        # 更新网络中所有包含权重的层
        for layer in self.layers:
            if hasattr(layer, 'step'):
                layer.step(lr)

# ==========================================
# 4. 构建生成器 (G) 和 判别器 (D)
# ==========================================

latent_dim = 4   # 隐变量维度 (在RL中，可以看作是随机噪声输入，或者结合State的输入)
data_dim = 2     # 输出维度 (例如 RL 中的 2 维连续动作空间)

# 生成器: Latent -> Hidden -> Data
G = Sequential(
    Linear(latent_dim, 16),
    ReLU(),
    Linear(16, data_dim)
)

# 判别器: Data -> Hidden -> Probability(0~1)
D = Sequential(
    Linear(data_dim, 16),
    ReLU(),
    Linear(16, 1),
    Sigmoid()
)

# ==========================================
# 5. 训练循环 (Training Loop)
# ==========================================

epochs = 2000
batch_size = 64
lr = 0.05

print("开始纯 NumPy GAN 训练...")

for epoch in range(epochs):
    
    # -------------------------------------------------
    # 阶段 1: 训练判别器 D
    # 目标: D 要能分辨真实数据 (标签为1) 和 G 生成的假数据 (标签为0)
    # -------------------------------------------------
    
    # 1.1 获取真实数据 (在 GAIL 中，这里对应专家给出的 State-Action 演示数据)
    # 假设真实数据分布是一个均值为 [5, 5] 的高斯分布
    real_data = np.random.normal(loc=[5.0, 5.0], scale=[1.0, 1.0], size=(batch_size, data_dim))
    real_labels = np.ones((batch_size, 1))

    # 1.2 G 生成假数据 (在 GAIL 中，对应当前 Policy 生成的 Action)
    z = np.random.normal(0, 1, (batch_size, latent_dim))
    fake_data = G.forward(z)
    fake_labels = np.zeros((batch_size, 1))

    # 1.3 判别器前向传播 & 计算损失
    pred_real = D.forward(real_data)
    loss_d_real, dout_real = bce_loss(pred_real, real_labels)
    
    pred_fake = D.forward(fake_data)
    loss_d_fake, dout_fake = bce_loss(pred_fake, fake_labels)
    
    loss_D = loss_d_real + loss_d_fake

    # 1.4 判别器反向传播 & 更新权重
    D.backward(dout_real)
    D.backward(dout_fake) # 累加真实和虚假的梯度 (注意 Linear 里的 dW 逻辑，如果是分别算需要累加，此处简化为连续后向但会覆盖，我们调整为分别 step 或改写 dW+=，为求准确这里演示单步更新)
    
    # 修正：分别计算并更新，防止梯度被覆盖
    D.backward(dout_real)
    D.step(lr)
    D.backward(dout_fake)
    D.step(lr)

    # -------------------------------------------------
    # 阶段 2: 训练生成器 G
    # 目标: G 生成的数据要骗过 D (让 D 认为标签是1)
    # -------------------------------------------------
    
    # 2.1 重新生成噪声和假数据
    z = np.random.normal(0, 1, (batch_size, latent_dim))
    fake_data = G.forward(z)
    
    # 2.2 用 D 对假数据进行打分
    pred_fake_for_G = D.forward(fake_data)
    
    # 2.3 计算 G 的损失 (G 希望 D 给出全 1 的预测)
    loss_G, dout_g = bce_loss(pred_fake_for_G, np.ones((batch_size, 1)))
    
    # 2.4 反向传播经过 D，但【不更新 D 的参数】！！！
    # 我们只需要获取梯度流经 D 到达假数据输入的那个导数 (dx_fake)
    dx_fake = D.backward(dout_g) 
    
    # 2.5 梯度继续回传给 G，并更新 G 的参数
    G.backward(dx_fake)
    G.step(lr)

    # ==========================================
    # 打印进度
    if epoch % 400 == 0:
        print(f"Epoch {epoch:4d} | Loss D: {loss_D:.4f} | Loss G: {loss_G:.4f} | 判别器对假数据的打分均值: {pred_fake_for_G.mean():.4f}")

# 训练结束后，测试生成器
test_z = np.random.normal(0, 1, (5, latent_dim))
generated_actions = G.forward(test_z)
print("\n训练完成！生成的动作 (逼近真实分布均值 [5, 5]):")
print(generated_actions)