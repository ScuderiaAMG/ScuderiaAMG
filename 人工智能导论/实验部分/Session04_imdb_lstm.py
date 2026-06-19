import os
import numpy as np
import paddle

# 兼容 PaddlePaddle 2.x 版本，开启静态图模式以支持 fluid API
if paddle.__version__.startswith('2.'):
    paddle.enable_static()

import paddle.dataset.imdb as imdb
import paddle.fluid as fluid

# ================= 1. 准备数据 =================
print("加载数据字典中...")
word_dict = imdb.word_dict()
dict_dim = len(word_dict)
print('加载数据字典完成')

print("加载训练和测试数据中 (首次运行可能会自动下载数据集)...")
# 获取训练和预测数据
train_reader = paddle.batch(paddle.reader.shuffle(imdb.train(word_dict), 512), batch_size=128)
test_reader = paddle.batch(imdb.test(word_dict), batch_size=128)
print('数据加载完成')

# # ================= 2. 配置网络 =================
# # 定义长短期记忆网络 (LSTM)
# def lstm_net(ipt, input_dim):
#     # 以数据的IDS作为输入
#     emb = fluid.layers.embedding(input=ipt, size=[input_dim, 128], is_sparse=True)
#     # 第一个全连接层
#     fc1 = fluid.layers.fc(input=emb, size=128)
    
#     # 进行一个长短期记忆操作 (文档原文存在轻微排版错误，此处已修正)
#     lstm1, _ = fluid.layers.dynamic_lstm(input=fc1, size=128)
    
#     # 第一个最大序列池操作
#     fc2 = fluid.layers.sequence_pool(input=fc1, pool_type='max')
#     # 第二个最大序列池操作
#     lstm2 = fluid.layers.sequence_pool(input=lstm1, pool_type='max')
    
#     # 以softmax作为全连接的输出层，大小为2，也就是正负面
#     out = fluid.layers.fc(input=[fc2, lstm2], size=2, act='softmax')
#     return out
# ================= 2. 配置网络 =================
# 定义长短期记忆网络 (LSTM)
def lstm_net(ipt, input_dim):
    # 以数据的IDS作为输入 (这行没报错，说明API还在，保持原样)
    emb = fluid.layers.embedding(input=ipt, size=[input_dim, 128], is_sparse=True)
    
    # 【修改1】替换掉原来的 fc，注意参数名变成了 x
    fc1 = paddle.static.nn.fc(x=emb, size=128)
    
    # 进行一个长短期记忆操作
    lstm1, _ = fluid.layers.dynamic_lstm(input=fc1, size=128)
    
    # 第一个最大序列池操作
    fc2 = fluid.layers.sequence_pool(input=fc1, pool_type='max')
    # 第二个最大序列池操作
    lstm2 = fluid.layers.sequence_pool(input=lstm1, pool_type='max')
    
    # 【修改2】替换掉原来的 fc，参数变成 x，act 变成 activation
    out = paddle.static.nn.fc(x=[fc2, lstm2], size=2, activation='softmax')
    return out

# 定义输入数据，lod_level不为0指定输入数据为序列数据
# words = fluid.layers.data(name='words', shape=[1], dtype='int64', lod_level=1)
# label = fluid.layers.data(name='label', shape=[1], dtype='int64')
# 定义输入数据，使用 paddle.static.data 替代废弃的 fluid.layers.data
words = paddle.static.data(name='words', shape=[None, 1], dtype='int64', lod_level=1)
label = paddle.static.data(name='label', shape=[None, 1], dtype='int64')

# 获取长短期记忆网络
model = lstm_net(words, dict_dim)

# 获取损失函数和准确率
cost = fluid.layers.cross_entropy(input=model, label=label)
avg_cost = fluid.layers.mean(cost)
acc = fluid.layers.accuracy(input=model, label=label)

# 获取预测程序
test_program = fluid.default_main_program().clone(for_test=True)

# 定义优化方法: Adagrad优化方法多用于处理稀疏数据
optimizer = fluid.optimizer.AdagradOptimizer(learning_rate=0.002)
opt = optimizer.minimize(avg_cost)

# ================= 3. 环境与执行器初始化 =================
# 定义使用CPU还是GPU。拯救者通常有显卡，此处默认尝试使用GPU
use_cuda = False  
place = fluid.CUDAPlace(0) if use_cuda else fluid.CPUPlace()
exe = fluid.Executor(place)

# 进行参数初始化
exe.run(fluid.default_startup_program())

# 定义输入数据的维度
feeder = fluid.DataFeeder(place=place, feed_list=[words, label])

# ================= 4. 训练网络 =================
print("开始训练...")
model_save_dir = "./emotionclassify_inference_model"

for pass_id in range(1):
    # 进行训练
    for batch_id, data in enumerate(train_reader()):
        train_cost = exe.run(program=fluid.default_main_program(),
                             feed=feeder.feed(data),
                             fetch_list=[avg_cost])
        
        # 每40次batch打印一次训练信息
        if batch_id % 40 == 0:
            print('Pass:%d, Batch:%d, Cost:%0.5f' % (pass_id, batch_id, train_cost[0][0])) 
            
    # 进行测试
    test_costs = []
    test_accs = []
    for batch_id, data in enumerate(test_reader()):
        test_cost, test_acc = exe.run(program=test_program,
                                      feed=feeder.feed(data),
                                      fetch_list=[avg_cost, acc])
        test_costs.append(test_cost[0]) 
        test_accs.append(test_acc[0]) 

    # 计算平均预测损失和准确率
    avg_test_cost = (sum(test_costs) / len(test_costs))
    avg_test_acc = (sum(test_accs) / len(test_accs))
    print('Test:%d, Cost:%0.5f, ACC:%0.5f' % (pass_id, avg_test_cost, avg_test_acc))

# 保存模型
if not os.path.exists(model_save_dir):
    os.makedirs(model_save_dir)
print('save models to %s' % (model_save_dir))

fluid.io.save_inference_model(model_save_dir, ['words'], [model], exe)


# ================= 5. 模型预测 =================
print("\n开始进行情感预测...")
# 定义预测数据
reviews_str = ['read the book forget the movie', 'this is a great movie', 'this is very bad']
# 把每个句子拆成一个个单词
reviews = [c.split() for c in reviews_str]

# 获取结束符号的标签
UNK = word_dict['<unk>']
# 获取每句话对应的标签
lod = []
for c in reviews:
    # 需要把单词进行字符串编码转换
    lod.append([word_dict.get(words.encode('utf-8'), UNK) for words in c])

# 获取每句话的单词数量
base_shape = [[len(c) for c in lod]]

# 生成预测数据张量
tensor_words = fluid.create_lod_tensor(lod, base_shape, place)

infer_exe = fluid.Executor(place)  # 创建推测用的executor
inference_scope = fluid.core.Scope()  # Scope指定作用域

with fluid.scope_guard(inference_scope):
    # 从指定目录中加载 推理model
    [inference_program, feed_target_names, fetch_targets] = fluid.io.load_inference_model(model_save_dir, infer_exe)

    # 运行预测程序
    results = infer_exe.run(inference_program,
                            feed={feed_target_names[0]: tensor_words},
                            fetch_list=fetch_targets)

    # 打印每句话的正负面概率
    for i, r in enumerate(results[0]):
        print("\'%s\'的预测结果为: 正面概率为:%0.5f, 负面概率为:%0.5f" % (reviews_str[i], r[0], r[1]))