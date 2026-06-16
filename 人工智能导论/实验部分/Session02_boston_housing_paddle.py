import paddle.fluid as fluid
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
