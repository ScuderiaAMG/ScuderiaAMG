import os
import numpy as np
import paddle

# 开启静态图模式以支持 fluid 实验代码
if paddle.__version__.startswith('2.'):
    paddle.enable_static()

import paddle.dataset.imdb as imdb
import paddle.fluid as fluid

# ================= 1. 准备数据 =================
print("加载数据字典中...")
word_dict = imdb.word_dict()
dict_dim = len(word_dict)
print('加载数据字典完成')

print("加载训练和测试数据中...")
train_reader = paddle.batch(paddle.reader.shuffle(imdb.train(word_dict), 512), batch_size=128)
test_reader = paddle.batch(imdb.test(word_dict), batch_size=128)
print('数据加载完成')

# ================= 2. 配置网络 =================
def lstm_net(ipt, input_dim):
    # 以数据的IDS作为输入
    emb = fluid.layers.embedding(input=ipt, size=[input_dim, 128], is_sparse=True)
    # 第一个全连接层
    fc1 = fluid.layers.fc(input=emb, size=128)
    
    # 长短期记忆操作 (核心实验代码)
    lstm1, _ = fluid.layers.dynamic_lstm(input=fc1, size=128)
    
    # 第一个最大序列池操作
    fc2 = fluid.layers.sequence_pool(input=fc1, pool_type='max')
    # 第二个最大序列池操作
    lstm2 = fluid.layers.sequence_pool(input=lstm1, pool_type='max')
    
    # 输出层
    out = fluid.layers.fc(input=[fc2, lstm2], size=2, act='softmax')
    return out

# 定义输入数据
words = fluid.layers.data(name='words', shape=[1], dtype='int64', lod_level=1)
label = fluid.layers.data(name='label', shape=[1], dtype='int64')

# 获取网络、损失函数、准确率
model = lstm_net(words, dict_dim)
cost = fluid.layers.cross_entropy(input=model, label=label)
avg_cost = fluid.layers.mean(cost)
acc = fluid.layers.accuracy(input=model, label=label)

# 获取预测程序并定义优化方法
test_program = fluid.default_main_program().clone(for_test=True)
optimizer = fluid.optimizer.AdagradOptimizer(learning_rate=0.002)
opt = optimizer.minimize(avg_cost)

# ================= 3. 运行环境配置 =================
use_cuda = False  # 保持纯 CPU 模式运行
place = fluid.CUDAPlace(0) if use_cuda else fluid.CPUPlace()
exe = fluid.Executor(place)
exe.run(fluid.default_startup_program())
feeder = fluid.DataFeeder(place=place, feed_list=[words, label])

# ================= 4. 开始训练 =================
print("开始训练...")
model_save_dir = "./emotionclassify_inference_model"

for pass_id in range(1):
    for batch_id, data in enumerate(train_reader()):
        train_cost = exe.run(program=fluid.default_main_program(),
                             feed=feeder.feed(data),
                             fetch_list=[avg_cost])
        if batch_id % 40 == 0:
            print('Pass:%d, Batch:%d, Cost:%0.5f' % (pass_id, batch_id, train_cost[0][0])) 
            
    test_costs = []
    test_accs = []
    for batch_id, data in enumerate(test_reader()):
        test_cost, test_acc = exe.run(program=test_program,
                                      feed=feeder.feed(data),
                                      fetch_list=[avg_cost, acc])
        test_costs.append(test_cost[0]) 
        test_accs.append(test_acc[0]) 

    print('Test:%d, Cost:%0.5f, ACC:%0.5f' % (pass_id, sum(test_costs)/len(test_costs), sum(test_accs)/len(test_accs)))

if not os.path.exists(model_save_dir):
    os.makedirs(model_save_dir)
fluid.io.save_inference_model(model_save_dir, ['words'], [model], exe)
print('模型已保存至 %s' % (model_save_dir))

# ================= 5. 模型预测 =================
print("\n开始进行情感预测...")
reviews_str = ['read the book forget the movie', 'this is a great movie', 'this is very bad']
reviews = [c.split() for c in reviews_str]
UNK = word_dict['<unk>']

lod = []
for c in reviews:
    lod.append([word_dict.get(words.encode('utf-8'), UNK) for words in c])

# base_shape = [[len(c) for c in lod]]
# tensor_words = fluid.create_lod_tensor(lod, base_shape, place)
# 获取每句话的单词数量
base_shape = [[len(c) for c in lod]]

# 解决 Windows 下 Numpy 默认 int32 导致的数据类型不匹配问题：
# 1. 把所有句子的单词 ID 展平到一个一维列表中
flat_words = [word for sentence in lod for word in sentence]
# 2. 强制转为 int64 格式的 Numpy 数组，并重塑形状为 [总词数, 1] 匹配网络输入
word_array = np.array(flat_words, dtype='int64').reshape(-1, 1)

# 使用转换好的 64 位数组生成 LoD 张量
tensor_words = fluid.create_lod_tensor(word_array, base_shape, place)

infer_exe = fluid.Executor(place)
inference_scope = fluid.core.Scope()

with fluid.scope_guard(inference_scope):
    [inference_program, feed_target_names, fetch_targets] = fluid.io.load_inference_model(model_save_dir, infer_exe)
    results = infer_exe.run(inference_program, feed={feed_target_names[0]: tensor_words}, fetch_list=fetch_targets)

    for i, r in enumerate(results[0]):
        print("\'%s\'的预测结果为: 正面概率为:%0.5f, 负面概率为:%0.5f" % (reviews_str[i], r[0], r[1]))