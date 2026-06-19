import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# 导入 PaddlePaddle 相关包
import paddle
import paddle.nn as nn
import paddle.nn.functional as F
from paddle.vision.transforms import Compose, Normalize
from paddle.metric import Accuracy

# ================= 步骤 1: 准备数据 =================
# 定义归一化标准
transform = Compose([Normalize(mean=[127.5], std=[127.5], data_format='CHW')])

print("正在下载并加载训练数据...")
train_dataset = paddle.vision.datasets.MNIST(mode='train', transform=transform)
test_dataset = paddle.vision.datasets.MNIST(mode='test', transform=transform)
print("加载完成！")

# ================= 步骤 2: 网络配置 =================
# 定义多层感知器 (包含两个大小为 100 的隐层和一个大小为 10 的输出层)
class mnist(paddle.nn.Layer):
    def __init__(self):
        super(mnist, self).__init__()
        self.fc1 = nn.Linear(in_features=28*28, out_features=100)
        self.fc2 = nn.Linear(in_features=100, out_features=100)
        self.fc3 = nn.Linear(in_features=100, out_features=10)

    def forward(self, input_):
        # 将输入展平
        x = paddle.reshape(input_, [input_.shape[0], -1])
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)
        y = F.softmax(x)
        return y

# 用 Model 封装模型
model = paddle.Model(mnist())

# 定义优化器与配置模型
optim = paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters())
model.prepare(optim, paddle.nn.CrossEntropyLoss(), Accuracy())

# ================= 步骤 3: 模型训练及评估 =================
print("开始训练模型...")
model.fit(train_dataset, 
          test_dataset, 
          epochs=2, 
          batch_size=64, 
          save_dir='multilayer_perceptron', 
          verbose=1)

# ================= 步骤 4: 模型预测 =================
# 获取测试集的第一个图片
test_data0, test_label_0 = test_dataset[0][0], test_dataset[0][1]
test_data0_reshaped = test_data0.reshape([28, 28])

# 展示测试集中的第一个图片
plt.figure(figsize=(2, 2))
plt.imshow(test_data0_reshaped, cmap=plt.cm.binary)
plt.title(f'True Label: {test_label_0[0]}')
plt.axis('off')
plt.show()

print('test_data0 的真实标签为: ' + str(test_label_0[0]))

# 模型预测
result = model.predict(test_dataset, batch_size=1)

# 提取并打印预测结果
predicted_value = np.argsort(result[0][0])[0][-1]
print('test_data0 预测的数值为: %d' % predicted_value)