import paddle
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 核心背景提示：
# 这份代码已经从旧版的 paddle.fluid (静态图)
# 升级为了现代的 PaddlePaddle 2.x (动态图) 写法。
# 逻辑与你原先的截图完全一致，但语法更简洁、更符合直觉。
# ==========================================

# 1. 准备数据
print("正在加载数据集...")
# Paddle 2.x 内置了波士顿房价数据集的快速调用，并可直接结合 DataLoader 使用
train_dataset = paddle.text.datasets.UCIHousing(mode='train')
test_dataset = paddle.text.datasets.UCIHousing(mode='test')

train_loader = paddle.io.DataLoader(train_dataset, batch_size=20, shuffle=True)
test_loader = paddle.io.DataLoader(test_dataset, batch_size=200, shuffle=False)

# 2. 网络配置 (动态图面向对象写法)
class LinearRegression(paddle.nn.Layer):
    def __init__(self):
        super(LinearRegression, self).__init__()
        # 定义一个全连接层：输入13维特征，输出1维房价
        self.fc = paddle.nn.Linear(in_features=13, out_features=1)

    def forward(self, inputs):
        return self.fc(inputs)

model = LinearRegression()

# 定义损失函数：均方误差 MSE
mse_loss = paddle.nn.MSELoss()

# 定义优化器：随机梯度下降 SGD，并传入模型参数
optimizer = paddle.optimizer.SGD(learning_rate=0.001, parameters=model.parameters())

# 3. 模型训练
EPOCH_NUM = 50
model_save_dir = "boston_housing.pdparams"

iters = []
train_costs = []
iter_count = 0

print("开始训练...")
model.train() # 将模型设置为训练模式
for epoch_id in range(EPOCH_NUM):
    for batch_id, data in enumerate(train_loader()):
        feature = data[0]
        label = data[1]

        # 前向计算
        predict = model(feature)
        # 计算损失
        loss = mse_loss(predict, label)
        # 反向传播
        loss.backward()
        # 更新权重参数
        optimizer.step()
        # 清空梯度
        optimizer.clear_grad()

        iter_count += len(feature)
        iters.append(iter_count)
        train_costs.append(loss.item())

    # 每过 10 个 Epoch 打印一次损失
    if epoch_id % 10 == 0:
        print(f"Epoch: {epoch_id}, Loss: {loss.item():.5f}")

# 保存模型参数
paddle.save(model.state_dict(), model_save_dir)
print(f"模型已保存至 {model_save_dir}")

# 绘制训练 Loss 曲线
plt.figure(figsize=(8, 6))
plt.title("Training Cost", fontsize=24)
plt.xlabel("Iter", fontsize=14)
plt.ylabel("Cost", fontsize=14)
plt.plot(iters, train_costs, color='red', label='training cost')
plt.grid()
plt.show()

# 4. 模型预测与评估
print("开始预测...")
# 加载刚才保存的模型权重
state_dict = paddle.load(model_save_dir)
model.set_state_dict(state_dict)

model.eval() # 设置为评估模式，关闭梯度追踪
infer_results = []
ground_truths = []

for data in test_loader():
    feature = data[0]
    label = data[1]

    predict = model(feature)
    
    # 提取张量里的数据转换为普通列表
    infer_results.extend(predict.numpy().flatten())
    ground_truths.extend(label.numpy().flatten())
    break  # 仅测试第一个 batch 里的 200 条数据进行可视化展示

# 打印部分结果比对
print("\n部分预测结果 vs 真实值 (House Price):")
for i in range(10):
    print(f"[{i}] 预测值:{infer_results[i]:.2f}  |  真实值:{ground_truths[i]:.2f}")

# 绘制预测值与真实值的散点图对比
plt.figure(figsize=(8, 6))
plt.title('Boston Housing Prediction', fontsize=24)
plt.xlabel('Ground Truth (Real Price)', fontsize=14)
plt.ylabel('Infer Result (Predicted Price)', fontsize=14)

# 绘制一条 y=x 的基准线，点越靠近这条线说明预测越准
max_val = max(max(ground_truths), max(infer_results))
x_ref = np.linspace(0, max_val, 10)
plt.plot(x_ref, x_ref, 'k--', label='Ideal Fit (y=x)')

plt.scatter(ground_truths, infer_results, color='green', label='Predictions')
plt.legend()
plt.grid()
plt.show()
