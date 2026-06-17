# ============================================================
# CIFAR-10 图像分类训练脚本 (v2 - 动态图版本)
# 环境：Anaconda paddle_env (PaddlePaddle 2.6.2 CPU)
# 与 Session03_train_cifar.py 内容一致，动态图模式稳定运行
# ============================================================

import os
import paddle
import paddle.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# -------------------- 超参数 --------------------
BATCH_SIZE = 128
EPOCH_NUM = 20
LEARNING_RATE = 0.001
model_save_dir = "./catdog.inference.model"

print(f"PaddlePaddle 版本: {paddle.__version__}")
paddle.set_device('cpu')


# -------------------- 1. 数据准备 --------------------
train_reader = paddle.batch(
    paddle.reader.shuffle(paddle.dataset.cifar.train10(), buf_size=128*100),
    batch_size=BATCH_SIZE)
test_reader = paddle.batch(
    paddle.dataset.cifar.test10(),
    batch_size=BATCH_SIZE)


# -------------------- 2. 网络定义 --------------------
class CIFAR10_CNN(nn.Layer):
    """三层卷积 + 全连接 CNN 分类器"""
    def __init__(self):
        super().__init__()
        # 第一个卷积-池化组：3→20 通道，5x5 卷积，same padding
        self.conv1 = nn.Conv2D(3, 20, kernel_size=5, stride=1, padding=2)
        self.bn1 = nn.BatchNorm2D(20)
        self.pool1 = nn.MaxPool2D(kernel_size=2, stride=2)
        # 第二个卷积-池化组：20→50 通道
        self.conv2 = nn.Conv2D(20, 50, kernel_size=5, stride=1, padding=2)
        self.bn2 = nn.BatchNorm2D(50)
        self.pool2 = nn.MaxPool2D(kernel_size=2, stride=2)
        # 第三个卷积-池化组：50→50 通道
        self.conv3 = nn.Conv2D(50, 50, kernel_size=5, stride=1, padding=2)
        self.pool3 = nn.MaxPool2D(kernel_size=2, stride=2)
        # 全连接分类层：50*4*4 → 10
        self.fc = nn.Linear(50 * 4 * 4, 10)

    def forward(self, x):
        x = self.pool1(nn.functional.relu(self.bn1(self.conv1(x))))
        x = self.pool2(nn.functional.relu(self.bn2(self.conv2(x))))
        x = self.pool3(nn.functional.relu(self.conv3(x)))
        x = paddle.reshape(x, [x.shape[0], -1])   # 展平
        x = self.fc(x)
        return x


# -------------------- 3. 训练准备 --------------------
model = CIFAR10_CNN()
loss_fn = nn.CrossEntropyLoss()
optimizer = paddle.optimizer.Adam(parameters=model.parameters(), learning_rate=LEARNING_RATE)

print("网络结构:")
print(f"  卷积层1: Conv2D(3, 20, 5) + BatchNorm + MaxPool(2)")
print(f"  卷积层2: Conv2D(20, 50, 5) + BatchNorm + MaxPool(2)")
print(f"  卷积层3: Conv2D(50, 50, 5) + MaxPool(2)")
print(f"  全连接层: Linear(50*4*4, 10)")
total_params = sum(int(p.numel()) for p in model.parameters())
print(f"  总参数量: {total_params:,}")

all_train_iter = 0
all_train_iters = []
all_train_costs = []
all_train_accs = []


def draw_train_process(title, iters, costs, accs, label_cost, label_acc):
    """绘制训练曲线"""
    plt.title(title, fontsize=24)
    plt.xlabel("iter", fontsize=20)
    plt.ylabel("cost/acc", fontsize=20)
    plt.plot(iters, costs, color='red', label=label_cost)
    plt.plot(iters, accs, color='green', label=label_acc)
    plt.legend()
    plt.grid()
    plt.show()


# -------------------- 4. 训练循环 --------------------
print("\n开始训练...")
for pass_id in range(EPOCH_NUM):
    # === 训练阶段 ===
    model.train()
    for batch_id, data in enumerate(train_reader()):
        img_data = np.array([item[0] for item in data], dtype=np.float32).reshape(-1, 3, 32, 32)
        lbl_data = np.array([item[1] for item in data], dtype=np.int64)

        img_tensor = paddle.to_tensor(img_data)
        lbl_tensor = paddle.to_tensor(lbl_data)

        # 前向传播
        logits = model(img_tensor)
        loss = loss_fn(logits, lbl_tensor)
        acc = paddle.metric.accuracy(logits, lbl_tensor.unsqueeze(1))

        # 反向传播
        loss.backward()
        optimizer.step()
        optimizer.clear_grad()

        # 记录
        all_train_iter += BATCH_SIZE
        all_train_iters.append(all_train_iter)
        all_train_costs.append(loss.item())
        all_train_accs.append(acc.item())

        if batch_id % 100 == 0:
            print('Pass:%d, Batch:%d, Cost:%0.5f, Accuracy:%0.5f' %
                  (pass_id, batch_id, loss.item(), acc.item()))

    # === 测试阶段 ===
    model.eval()
    test_costs = []
    test_accs = []
    for batch_id, data in enumerate(test_reader()):
        img_data = np.array([item[0] for item in data], dtype=np.float32).reshape(-1, 3, 32, 32)
        lbl_data = np.array([item[1] for item in data], dtype=np.int64)

        img_tensor = paddle.to_tensor(img_data)
        lbl_tensor = paddle.to_tensor(lbl_data)

        logits = model(img_tensor)
        loss = loss_fn(logits, lbl_tensor)
        acc = paddle.metric.accuracy(logits, lbl_tensor.unsqueeze(1))

        test_costs.append(loss.item())
        test_accs.append(acc.item())

    test_cost_avg = sum(test_costs) / len(test_costs)
    test_acc_avg = sum(test_accs) / len(test_accs)
    print('Test:%d, Cost:%0.5f, ACC:%0.5f' % (pass_id, test_cost_avg, test_acc_avg))

print("训练完成！")

# -------------------- 5. 保存模型 --------------------
if not os.path.exists(model_save_dir):
    os.makedirs(model_save_dir)
save_path = os.path.join(model_save_dir, "model")
paddle.jit.save(model, save_path)
print('模型已保存到 %s' % model_save_dir)

draw_train_process("training", all_train_iters, all_train_costs, all_train_accs,
                   "training cost", "training acc")

# -------------------- 6. 模型预测 --------------------
print("\n开始模型预测...")

try:
    resample = Image.Resampling.LANCZOS
except AttributeError:
    resample = Image.ANTIALIAS

label_list = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]

infer_path = 'dog2.jpg'

try:
    img_show = Image.open(infer_path)
    plt.imshow(img_show)
    plt.axis('off')
    plt.title("Input Image")
    plt.show()

    im = Image.open(infer_path)
    im = im.resize((32, 32), resample)
    im = np.array(im).astype(np.float32)
    im = im.transpose((2, 0, 1))
    im = im / 255.0
    im = np.expand_dims(im, axis=0)
    print('输入图像维度:', im.shape)

    loaded_model = paddle.jit.load(save_path)
    loaded_model.eval()

    img_tensor = paddle.to_tensor(im)
    logits = loaded_model(img_tensor)
    pred_idx = np.argmax(logits.numpy())
    print("预测结果: %s" % label_list[pred_idx])

except FileNotFoundError:
    print(f"未在当前目录找到测试图片 '{infer_path}'，已跳过最终预测阶段。")
    print("提示: 将一张图片命名为 'dog2.jpg' 放到脚本同级目录即可测试预测功能。")
