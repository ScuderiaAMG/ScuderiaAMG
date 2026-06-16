```python
code_content = """import paddle.fluid as fluid
import paddle
import numpy as np
import os
import matplotlib.pyplot as plt

# ==========================================
# Step1: 准备数据
# ==========================================
BUF_SIZE = 500
BATCH_SIZE = 20

# 用于训练的数据提供器，每次从缓存中随机读取批次大小的数据
train_reader = paddle.batch(
    paddle.reader.shuffle(paddle.dataset.uci_housing.train(), buf_size=BUF_SIZE),
    batch_size=BATCH_SIZE
)

# 用于测试的数据提供器，每次从缓存中随机读取批次大小的数据
test_reader = paddle.batch(
    paddle.reader.shuffle(paddle.dataset.uci_housing.test(), buf_size=BUF_SIZE),
    batch_size=BATCH_SIZE
)

# 用于打印，查看uci_housing数据
train_data = paddle.dataset.uci_housing.train()
sampledata = next(train_data())
print("数据样例：", sampledata)

# ==========================================
# Step2: 网络配置
# ==========================================
# (1) 网络搭建
# 定义张量变量x，表示13维的特征值
x = fluid.layers.data(name='x', shape=[13], dtype='float32')
# 定义张量y，表示目标值
y = fluid.layers.data(name='y', shape=[1], dtype='float32')
# 定义一个简单的线性网络，连接输入和输出的全连接层
y_predict = fluid.layers.fc(input=x, size=1, act=None)

# (2) 定义损失函数
cost = fluid.layers.square_error_cost(input=y_predict, label=y)  # 求一个batch的损失值
avg_cost = fluid.layers.mean(cost)                              # 对损失值求平均值

# (3) 定义优化函数
optimizer = fluid.optimizer.SGDOptimizer(learning_rate=0.001)
opts = optimizer.minimize(avg_cost)

# 克隆主程序用于测试
test_program = fluid.default_main_program().clone(for_test=True)

# ==========================================
# Step3: 模型训练 and Step4: 模型评估
# ==========================================
# (1) 创建Executor
use_cuda = False
place = fluid.CUDAPlace(0) if use_cuda else fluid.CPUPlace()
exe = fluid.Executor(place)               # 创建一个Executor实例exe
exe.run(fluid.default_startup_program())  # 执行startup_program()，进行参数初始化

# (2) 定义输入数据维度
feeder = fluid.DataFeeder(place=place, feed_list=[x, y])

# (3) 定义绘制训练过程的损失值变化趋势的方法
iter = 0
iters = []
train_costs = []

def draw_train_process(iters, train_costs):
    title = "training cost"
    plt.title(title, fontsize=24)
    plt.xlabel("iter", fontsize=14)
    plt.ylabel("cost", fontsize=14)
    plt.plot(iters, train_costs, color='red', label='training cost')
    plt.grid()
    plt.show()

# (4) 训练并保存模型
EPOCH_NUM = 50
model_save_dir = "./fit_a_line.inference.model"  # 修改为当前目录方便运行

for pass_id in range(EPOCH_NUM):
    # 开始训练并输出最后一个batch的损失值
    train_cost = 0
    for batch_id, data in enumerate(train_reader()):
        train_cost = exe.run(
            program=fluid.default_main_program(),
            feed=feeder.feed(data),
            fetch_list=[avg_cost]
        )
        
        if batch_id % 40 == 0:
            print("Pass:%d, Cost:%0.5f" % (pass_id, train_cost[0][0]))
            
        iter = iter + BATCH_SIZE
        iters.append(iter)
        train_costs.append(train_cost[0][0])
        
    # 开始测试并输出最后一个batch的损失值
    test_cost = 0
    for batch_id, data in enumerate(test_reader()):
        test_cost = exe.run(
            program=test_program,
            feed=feeder.feed(data),
            fetch_list=[avg_cost]
        )
    print('Test:%d, Cost:%0.5f' % (pass_id, test_cost[0][0]))
    
    # 保存模型
    if not os.path.exists(model_save_dir):
        os.makedirs(model_save_dir)
    print('save models to %s' % (model_save_dir))
    
    fluid.io.save_inference_model(
        model_save_dir,
        ['x'],
        [y_predict],
        exe
    )

# 绘制训练曲线
draw_train_process(iters, train_costs)

# ==========================================
# Step5: 模型预测
# ==========================================
# (1) 创建预测用的Executor
infer_exe = fluid.Executor(place)
inference_scope = fluid.core.Scope()

# (2) 可视化真实值与预测值方法定义
infer_results = []
groud_truths = []  # 保持图片中的拼写

def draw_infer_result(groud_truths, infer_results):
    title = 'Boston'
    plt.title(title, fontsize=24)
    x = np.arange(1, 20)
    y = x
    plt.plot(x, y)
    plt.xlabel('ground truth', fontsize=14)
    plt.ylabel('infer result', fontsize=14)
    plt.scatter(groud_truths, infer_results, color='green', label='training cost')
    plt.grid()
    plt.show()

# (3) 开始预测
with fluid.scope_guard(inference_scope):
    [inference_program, feed_target_names, fetch_targets] = fluid.io.load_inference_model(
        model_save_dir,
        infer_exe
    )
    
    infer_reader = paddle.batch(
        paddle.dataset.uci_housing.test(),
        batch_size=200
    )
    
    test_data = next(infer_reader())
    test_x = np.array([data[0] for data in test_data]).astype("float32")
    test_y = np.array([data[1] for data in test_data]).astype("float32")
    
    results = infer_exe.run(
        inference_program,
        feed={feed_target_names[0]: np.array(test_x)},
        fetch_list=fetch_targets
    )
    
    print("infer results and ground truth: (House Price)")
    for idx, val in enumerate(zip(results[0], test_y)):
        print("%d: infer:%.2f  gt:%.2f" % (idx, val[0], val[1]))
        infer_results.append(val[0])
        groud_truths.append(val[1])
        
    draw_infer_result(groud_truths, infer_results)
"""

filename = "boston_housing_paddle.py"
with open(filename, "w", encoding="utf-8") as f:
    f.write(code_content)

print(f"File {filename} created successfully.")



```

```text
File boston_housing_paddle.py created successfully.


```

Your Python file is ready


这份代码演示了如何使用早期的 **PaddlePaddle（基于 `paddle.fluid` 静态图框架）** 实现经典的**波士顿房价预测**任务。整个过程是一个标准的机器学习线性回归工作流。

以下是代码各个模块的完整文字讲解：

### 总体概述

本教程通过构建一个简单的单层线性回归模型，对 UCI 波士顿房价数据集进行拟合。公式可以抽象为：`Y' = wX + b`，目的是通过不断优化权重 `w` 和偏置 `b`，使模型预测的房价（Y'）尽可能接近真实房价（Y）。

---

### Step 1: 准备数据

* **数据集引入**：使用了 Paddle 内置的 `paddle.dataset.uci_housing` 数据集。该数据集有 506 行，包含 13 个维度的特征信息（如犯罪率、房间数等），最后一列为真实房价中位数。
* **数据读取器（Reader）**：
* 通过 `paddle.reader.shuffle` 设置 `BUF_SIZE=500` 对数据进行打乱，防止模型过度记忆数据顺序。
* 通过 `paddle.batch` 设置 `BATCH_SIZE=20`，也就是每次向模型喂入 20 条数据进行批量训练。分别生成了 `train_reader` 和 `test_reader`。



### Step 2: 网络配置

在静态图模式下，这部分主要是构建**计算图（Program）**，并没有真正开始计算：

1. **数据层定义**：定义了输入变量 `x`（维度为 13 的浮点数张量）和目标变量 `y`（维度为 1 的房价张量）。
2. **网络搭建**：使用 `fluid.layers.fc` 构建了一个简单的全连接层，输入为 `x`，输出大小 `size=1`，由于是线性回归，所以不使用激活函数（`act=None`）。
3. **定义损失函数**：选用**均方误差（MSE）** `square_error_cost` 来衡量预测值 `y_predict` 和真实值 `y` 之间的差距，并求得批次的平均损失 `avg_cost`。
4. **定义优化器**：使用随机梯度下降（SGD）优化器，学习率设定为 `0.001`，目标是最小化平均损失 `avg_cost`。
5. 同时，克隆了一份 `test_program` 专用于测试评估（不会修改网络权重）。

### Step 3 & 4: 模型训练与评估

真正开始运行计算图：

1. **创建执行器（Executor）**：指定运行设备（CPU），实例化 `fluid.Executor`，并运行 `startup_program` 对网络参数进行初始化。
2. **定义数据转换（DataFeeder）**：负责将 Reader 提供的数据格式化，并正确映射给输入张量 `x` 和 `y`。
3. **循环训练**：
* 外层循环控制 Epoch（共训练 50 轮）。
* 内层循环遍历 `train_reader`，不断调用 `exe.run` 喂入训练数据，计算 Loss 并在后台更新网络权重。每 40 个 batch 打印一次训练 Loss，并记录到数组中用于后续画图。
* 每个 Epoch 结束后，在测试集上运行一遍前向计算，得出测试 Loss。


4. **模型保存**：使用 `fluid.io.save_inference_model` 接口，提取网络中专门用于预测的部分，连同训练好的权重一并保存到本地目录（`/home/aistudio/work/fit_a_line.inference.model`）。
5. **可视化**：训练结束后，调用自定义的 `draw_train_process` 绘制包含所有迭代步数的 Loss 下降趋势图。

### Step 5: 模型预测

加载之前保存的预测模型（Inference Model），在未知数据上验证效果：

1. **作用域管理**：通过 `with fluid.scope_guard(inference_scope):` 开辟一个新的作用域，防止预测时的变量与训练时发生冲突。
2. **模型加载**：通过 `load_inference_model` 拿到推断的主程序、需要喂入的数据变量名以及推断结果的目标张量。
3. **执行预测**：从测试集中取出一个大小为 200 的 batch，剥离出特征 `test_x` 和真实标签 `test_y`，只将 `test_x` 喂入模型得到预测结果数组。
4. **预测结果可视化**：将模型给出的预测值与真实的 Ground Truth 进行对比打印，并调用 `draw_infer_result` 绘制散点图，直观地观察预测值与一条 `y=x` 基准线的偏离程度。