import os
import paddle
import paddle.fluid as fluid
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# 关键：开启静态图模式，兼容文档中的 Fluid 旧 API
paddle.enable_static()

BATCH_SIZE = 128
# 用于训练的数据提供器
train_reader = paddle.batch(
    paddle.reader.shuffle(paddle.dataset.cifar.train10(), buf_size=128*100),
    batch_size=BATCH_SIZE)
# 用于测试的数据提供器
test_reader = paddle.batch(
    paddle.dataset.cifar.test10(),
    batch_size=BATCH_SIZE)

# (1) 网络搭建
def convolutional_neural_network(img):
    # 第一个卷积-池化层
    conv_pool_1 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=5,
        num_filters=20,
        pool_size=2,
        pool_stride=2,
        act="relu")
    conv_pool_1 = paddle.static.nn.batch_norm(conv_pool_1)

    # 第二个卷积-池化层
    conv_pool_2 = fluid.nets.simple_img_conv_pool(
        input=conv_pool_1,
        filter_size=5,
        num_filters=50,
        pool_size=2,
        pool_stride=2,
        act="relu")
    conv_pool_2 = paddle.static.nn.batch_norm(conv_pool_2)

    # 第三个卷积-池化层
    conv_pool_3 = fluid.nets.simple_img_conv_pool(
        input=conv_pool_2,
        filter_size=5,
        num_filters=50,
        pool_size=2,
        pool_stride=2,
        act="relu")

    # 全连接层 + softmax 分类
    prediction = paddle.static.nn.fc(x=conv_pool_3, size=10, activation='softmax')
    return prediction

# (2) 定义数据 (已加入 None 维度)
images = paddle.static.data(name='images', shape=[None, 3, 32, 32], dtype='float32')
label = paddle.static.data(name='label', shape=[None, 1], dtype='int64')

# (3) 获取分类器
predict = convolutional_neural_network(images)

# (4) 定义损失函数和准确率
# 关闭 use_softmax（上一步 fc 已自带 softmax），reduction='none' 供后续求平均
cost = paddle.nn.functional.cross_entropy(input=predict, label=label, reduction='none', use_softmax=False)
avg_cost = paddle.mean(cost)
acc = paddle.static.accuracy(input=predict, label=label)

# 获取测试程序
test_program = paddle.static.default_main_program().clone(for_test=True)

# (5) 定义优化方法
optimizer = paddle.optimizer.Adam(learning_rate=0.001)
optimizer.minimize(avg_cost)
print("网络配置完成，准备启动 Executor...")

# 创建 Executor（自动检测 GPU / CPU）
use_cuda = paddle.is_compiled_with_cuda()
place = paddle.CUDAPlace(0) if use_cuda else paddle.CPUPlace()
print(f"使用设备: {'GPU (CUDA)' if use_cuda else 'CPU'}")
exe = paddle.static.Executor(place)
exe.run(paddle.static.default_startup_program())

all_train_iter = 0
all_train_iters = []
all_train_costs = []
all_train_accs = []

def draw_train_process(title, iters, costs, accs, label_cost, lable_acc):
    plt.title(title, fontsize=24)
    plt.xlabel("iter", fontsize=20)
    plt.ylabel("cost/acc", fontsize=20)
    plt.plot(iters, costs, color='red', label=label_cost)
    plt.plot(iters, accs, color='green', label=lable_acc)
    plt.legend()
    plt.grid()
    plt.show()

# 训练并保存模型
EPOCH_NUM = 20
model_save_dir = "./catdog.inference.model"

for pass_id in range(EPOCH_NUM):
    # 开始训练
    for batch_id, data in enumerate(train_reader()):
        # 显式 Reshape 恢复 4D 结构，并保证内存连续（防止 C++ 端指针越界）
        img_data = np.array([item[0] for item in data], dtype=np.float32).reshape(-1, 3, 32, 32)
        img_data = np.ascontiguousarray(img_data)
        lbl_data = np.array([item[1] for item in data], dtype=np.int64).reshape(-1, 1)
        lbl_data = np.ascontiguousarray(lbl_data)

        train_cost, train_acc = exe.run(program=paddle.static.default_main_program(),
                                        feed={'images': img_data, 'label': lbl_data},
                                        fetch_list=[avg_cost, acc])

        all_train_iter = all_train_iter + BATCH_SIZE
        all_train_iters.append(all_train_iter)
        all_train_costs.append(train_cost.item())
        all_train_accs.append(train_acc.item())

        if batch_id % 100 == 0:
            print('Pass:%d, Batch:%d, Cost:%0.5f, Accuracy:%0.5f' %
                  (pass_id, batch_id, train_cost.item(), train_acc.item()))

    # 开始测试
    test_costs = []
    test_accs = []
    for batch_id, data in enumerate(test_reader()):
        img_data = np.array([item[0] for item in data], dtype=np.float32).reshape(-1, 3, 32, 32)
        img_data = np.ascontiguousarray(img_data)
        lbl_data = np.array([item[1] for item in data], dtype=np.int64).reshape(-1, 1)
        lbl_data = np.ascontiguousarray(lbl_data)

        test_cost, test_acc = exe.run(program=test_program,
                                      feed={'images': img_data, 'label': lbl_data},
                                      fetch_list=[avg_cost, acc])
        test_costs.append(test_cost.item())
        test_accs.append(test_acc.item())

    test_cost_avg = (sum(test_costs) / len(test_costs))
    test_acc_avg = (sum(test_accs) / len(test_accs))
    print('Test:%d, Cost:%0.5f, ACC:%0.5f' % (pass_id, test_cost_avg, test_acc_avg))

# 保存模型
if not os.path.exists(model_save_dir):
    os.makedirs(model_save_dir)
print('save models to %s' % (model_save_dir))
paddle.static.save_inference_model(model_save_dir,
                                   [images],
                                   [predict],
                                   exe)
print('训练模型保存完成！')
draw_train_process("training", all_train_iters, all_train_costs, all_train_accs, "trainning cost", "trainning acc")

# Step5. 模型预测
infer_exe = paddle.static.Executor(place)
inference_scope = paddle.static.Scope()

def load_image(file):
    im = Image.open(file)
    # 兼容新版 Pillow（>=10.0 移除 ANTIALIAS）
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS
    im = im.resize((32, 32), resample)
    im = np.array(im).astype(np.float32)
    im = im.transpose((2, 0, 1))       # HWC → CHW
    im = im / 255.0
    im = np.expand_dims(im, axis=0)    # 添加 batch 维度
    print('im_shape的维度:', im.shape)
    return im

with paddle.static.scope_guard(inference_scope):
    [inference_program,
     feed_target_names,
     fetch_targets] = paddle.static.load_inference_model(model_save_dir, infer_exe)

    infer_path = 'dog2.jpg'  # 请确保当前文件夹下有这张测试图片

    # 防止因找不到图片而阻断运行，加入异常处理
    try:
        img_show = Image.open(infer_path)
        plt.imshow(img_show)
        plt.axis('off')
        plt.show()
        img = load_image(infer_path)

        results = infer_exe.run(inference_program,
                                feed={feed_target_names[0]: img},
                                fetch_list=fetch_targets)
        print('results', results)

        label_list = [
            "airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"
        ]
        print("infer results: %s" % label_list[np.argmax(results[0])])
    except FileNotFoundError:
        print(f"未在当前目录找到测试图片 '{infer_path}'，已跳过最终预测阶段。")
