import os
import paddle
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# 开启静态图模式
paddle.enable_static()

BATCH_SIZE = 128
train_reader = paddle.batch(
    paddle.reader.shuffle(paddle.dataset.cifar.train10(), buf_size=128*100),
    batch_size=BATCH_SIZE)
test_reader = paddle.batch(
    paddle.dataset.cifar.test10(),
    batch_size=BATCH_SIZE)

# (1) 网络搭建
def convolutional_neural_network(img):
    import paddle.fluid as fluid 
    conv_pool_1 = fluid.nets.simple_img_conv_pool(
        input=img, filter_size=5, num_filters=20, pool_size=2, pool_stride=2, act="relu")
    conv_pool_1 = paddle.static.nn.batch_norm(conv_pool_1)
    
    conv_pool_2 = fluid.nets.simple_img_conv_pool(
        input=conv_pool_1, filter_size=5, num_filters=50, pool_size=2, pool_stride=2, act="relu")
    conv_pool_2 = paddle.static.nn.batch_norm(conv_pool_2)
    
    conv_pool_3 = fluid.nets.simple_img_conv_pool(
        input=conv_pool_2, filter_size=5, num_filters=50, pool_size=2, pool_stride=2, act="relu")
        
    prediction = paddle.static.nn.fc(x=conv_pool_3, size=10, activation='softmax')
    return prediction

# (2) 定义数据 
images = paddle.static.data(name='images', shape=[None, 3, 32, 32], dtype='float32')
label = paddle.static.data(name='label', shape=[None, 1], dtype='int64')

# (3) 获取分类器
predict = convolutional_neural_network(images)

# (4) 定义损失函数和准确率
cost = paddle.nn.functional.cross_entropy(input=predict, label=label, reduction='none', use_softmax=False) 
avg_cost = paddle.mean(cost)
acc = paddle.static.accuracy(input=predict, label=label)

test_program = paddle.static.default_main_program().clone(for_test=True)

# (5) 定义优化方法
optimizer = paddle.optimizer.Adam(learning_rate=0.001)
optimizer.minimize(avg_cost)
print("网络配置完成，准备启动 Executor...")

# ==========================================
# 终极修复：绝对强制使用 CPUPlace()，彻底切断与 CUDA 的联系
# ==========================================
place = paddle.CPUPlace()
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
    for batch_id, data in enumerate(train_reader()):
        
        # CPU 内存下安全的数据打包
        img_data = np.array([item[0] for item in data], dtype=np.float32).reshape(-1, 3, 32, 32)
        lbl_data = np.array([item[1] for item in data], dtype=np.int64).reshape(-1, 1)

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

    # 测试阶段
    test_costs = []
    test_accs = []
    for batch_id, data in enumerate(test_reader()):
        img_data = np.array([item[0] for item in data], dtype=np.float32).reshape(-1, 3, 32, 32)
        lbl_data = np.array([item[1] for item in data], dtype=np.int64).reshape(-1, 1)
        
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
paddle.fluid.io.save_inference_model(model_save_dir, ['images'], [predict], exe)
print('训练模型保存完成！')
draw_train_process("training", all_train_iters, all_train_costs, all_train_accs, "training cost", "training acc")

# 模型预测
infer_exe = paddle.static.Executor(place)
inference_scope = paddle.static.Scope()

def load_image(file):
    im = Image.open(file)
    # 兼容新版 Pillow
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS
    im = im.resize((32, 32), resample)
    im = np.array(im).astype(np.float32)
    im = im.transpose((2, 0, 1))
    im = im / 255.0
    im = np.expand_dims(im, axis=0)
    return im

with paddle.static.scope_guard(inference_scope):
    [inference_program, feed_target_names, fetch_targets] = paddle.fluid.io.load_inference_model(model_save_dir, infer_exe)
     
    infer_path = 'dog2.jpg'
    try:
        img_show = Image.open(infer_path)
        plt.imshow(img_show)
        plt.show()
        img = load_image(infer_path)
        
        results = infer_exe.run(inference_program,
                                feed={feed_target_names[0]: img},
                                fetch_list=fetch_targets)
        
        label_list = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]
        print("infer results: %s" % label_list[np.argmax(results[0])])
    except FileNotFoundError:
        print(f"未在当前目录找到测试图片 '{infer_path}'，已跳过最终预测阶段。")