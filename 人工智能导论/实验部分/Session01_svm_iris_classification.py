"""
SVM 鸢尾花分类实验 —— 完整代码（数据集已嵌入）
=================================================
任务描述:
  构建一个 SVM 模型，根据鸢尾花的花萼和花瓣大小将其分为三种不同的品种。
  - 特征: 花萼长度(sepal length), 花萼宽度(sepal width), 花瓣长度(petal length), 花瓣宽度(petal width)
  - 标签: 0=山鸢尾(Iris-setosa), 1=变色鸢尾(Iris-versicolor), 2=维吉尼亚鸢尾(Iris-virginica)

数据集:
  鸢尾花数据集 (Iris), 共150行, 每行4个特征 + 1个标签, 已内嵌于脚本中。

实验步骤:
  Step 1: 数据准备 —— 加载数据、分割训练集/测试集
  Step 2: 模型搭建 —— 构建 SVM 分类器 (线性核, OVR)
  Step 3: 模型训练 —— 使用训练集拟合模型
  Step 4: 模型评估 —— 计算准确率、可视化决策边界
"""

import numpy as np
from io import StringIO
from matplotlib import colors
from sklearn import svm
from sklearn.svm import SVC
from sklearn import model_selection
import matplotlib
matplotlib.use('Agg')           # 使用非交互式后端, 避免 plt.show() 阻塞
import matplotlib.pyplot as plt
import matplotlib as mpl

# ============================================================================
# 内嵌数据集: 鸢尾花 (Iris) 共150行
# 每行格式: 花萼长度,花萼宽度,花瓣长度,花瓣宽度,品种名称
# ============================================================================
IRIS_CSV = """\
5.1,3.5,1.4,0.2,Iris-setosa
4.9,3.0,1.4,0.2,Iris-setosa
4.7,3.2,1.3,0.2,Iris-setosa
4.6,3.1,1.5,0.2,Iris-setosa
5.0,3.6,1.4,0.2,Iris-setosa
5.4,3.9,1.7,0.4,Iris-setosa
4.6,3.4,1.4,0.3,Iris-setosa
5.0,3.4,1.5,0.2,Iris-setosa
4.4,2.9,1.4,0.2,Iris-setosa
4.9,3.1,1.5,0.1,Iris-setosa
5.4,3.7,1.5,0.2,Iris-setosa
4.8,3.4,1.6,0.2,Iris-setosa
4.8,3.0,1.4,0.1,Iris-setosa
4.3,3.0,1.1,0.1,Iris-setosa
5.8,4.0,1.2,0.2,Iris-setosa
5.7,4.4,1.5,0.4,Iris-setosa
5.4,3.9,1.3,0.4,Iris-setosa
5.1,3.5,1.4,0.3,Iris-setosa
5.7,3.8,1.7,0.3,Iris-setosa
5.1,3.8,1.5,0.3,Iris-setosa
5.4,3.4,1.7,0.2,Iris-setosa
5.1,3.7,1.5,0.4,Iris-setosa
4.6,3.6,1.0,0.2,Iris-setosa
5.1,3.3,1.7,0.5,Iris-setosa
4.8,3.4,1.9,0.2,Iris-setosa
5.0,3.0,1.6,0.2,Iris-setosa
5.0,3.4,1.6,0.4,Iris-setosa
5.2,3.5,1.5,0.2,Iris-setosa
5.2,3.4,1.4,0.2,Iris-setosa
4.7,3.2,1.6,0.2,Iris-setosa
4.8,3.1,1.6,0.2,Iris-setosa
5.4,3.4,1.5,0.4,Iris-setosa
5.2,4.1,1.5,0.1,Iris-setosa
5.5,4.2,1.4,0.2,Iris-setosa
4.9,3.1,1.5,0.2,Iris-setosa
5.0,3.2,1.2,0.2,Iris-setosa
5.5,3.5,1.3,0.2,Iris-setosa
4.9,3.6,1.4,0.1,Iris-setosa
4.4,3.0,1.3,0.2,Iris-setosa
5.1,3.4,1.5,0.2,Iris-setosa
5.0,3.5,1.3,0.3,Iris-setosa
4.5,2.3,1.3,0.3,Iris-setosa
4.4,3.2,1.3,0.2,Iris-setosa
5.0,3.5,1.6,0.6,Iris-setosa
5.1,3.8,1.9,0.4,Iris-setosa
4.8,3.0,1.4,0.3,Iris-setosa
5.1,3.8,1.6,0.2,Iris-setosa
4.6,3.2,1.4,0.2,Iris-setosa
5.3,3.7,1.5,0.2,Iris-setosa
5.0,3.3,1.4,0.2,Iris-setosa
7.0,3.2,4.7,1.4,Iris-versicolor
6.4,3.2,4.5,1.5,Iris-versicolor
6.9,3.1,4.9,1.5,Iris-versicolor
5.5,2.3,4.0,1.3,Iris-versicolor
6.5,2.8,4.6,1.5,Iris-versicolor
5.7,2.8,4.5,1.3,Iris-versicolor
6.3,3.3,4.7,1.6,Iris-versicolor
4.9,2.4,3.3,1.0,Iris-versicolor
6.6,2.9,4.6,1.3,Iris-versicolor
5.2,2.7,3.9,1.4,Iris-versicolor
5.0,2.0,3.5,1.0,Iris-versicolor
5.9,3.0,4.2,1.5,Iris-versicolor
6.0,2.2,4.0,1.0,Iris-versicolor
6.1,2.9,4.7,1.4,Iris-versicolor
5.6,2.9,3.6,1.3,Iris-versicolor
6.7,3.1,4.4,1.4,Iris-versicolor
5.6,3.0,4.5,1.5,Iris-versicolor
5.8,2.7,4.1,1.0,Iris-versicolor
6.2,2.2,4.5,1.5,Iris-versicolor
5.6,2.5,3.9,1.1,Iris-versicolor
5.9,3.2,4.8,1.8,Iris-versicolor
6.1,2.8,4.0,1.3,Iris-versicolor
6.3,2.5,4.9,1.5,Iris-versicolor
6.1,2.8,4.7,1.2,Iris-versicolor
6.4,2.9,4.3,1.3,Iris-versicolor
6.6,3.0,4.4,1.4,Iris-versicolor
6.8,2.8,4.8,1.4,Iris-versicolor
6.7,3.0,5.0,1.7,Iris-versicolor
6.0,2.9,4.5,1.5,Iris-versicolor
5.7,2.6,3.5,1.0,Iris-versicolor
5.5,2.4,3.8,1.1,Iris-versicolor
5.5,2.4,3.7,1.0,Iris-versicolor
5.8,2.7,3.9,1.2,Iris-versicolor
6.0,2.7,5.1,1.6,Iris-versicolor
5.4,3.0,4.5,1.5,Iris-versicolor
6.0,3.4,4.5,1.6,Iris-versicolor
6.7,3.1,4.7,1.5,Iris-versicolor
6.3,2.3,4.4,1.3,Iris-versicolor
5.6,3.0,4.1,1.3,Iris-versicolor
5.5,2.5,4.0,1.3,Iris-versicolor
5.5,2.6,4.4,1.2,Iris-versicolor
6.1,3.0,4.6,1.4,Iris-versicolor
5.8,2.6,4.0,1.2,Iris-versicolor
5.0,2.3,3.3,1.0,Iris-versicolor
5.6,2.7,4.2,1.3,Iris-versicolor
5.7,3.0,4.2,1.2,Iris-versicolor
5.7,2.9,4.2,1.3,Iris-versicolor
6.2,2.9,4.3,1.3,Iris-versicolor
5.1,2.5,3.0,1.1,Iris-versicolor
5.7,2.8,4.1,1.3,Iris-versicolor
6.3,3.3,6.0,2.5,Iris-virginica
5.8,2.7,5.1,1.9,Iris-virginica
7.1,3.0,5.9,2.1,Iris-virginica
6.3,2.9,5.6,1.8,Iris-virginica
6.5,3.0,5.8,2.2,Iris-virginica
7.6,3.0,6.6,2.1,Iris-virginica
4.9,2.5,4.5,1.7,Iris-virginica
7.3,2.9,6.3,1.8,Iris-virginica
6.7,2.5,5.8,1.8,Iris-virginica
7.2,3.6,6.1,2.5,Iris-virginica
6.5,3.2,5.1,2.0,Iris-virginica
6.4,2.7,5.3,1.9,Iris-virginica
6.8,3.0,5.5,2.1,Iris-virginica
5.7,2.5,5.0,2.0,Iris-virginica
5.8,2.8,5.1,2.4,Iris-virginica
6.4,3.2,5.3,2.3,Iris-virginica
6.5,3.0,5.5,1.8,Iris-virginica
7.7,3.8,6.7,2.2,Iris-virginica
7.7,2.6,6.9,2.3,Iris-virginica
6.0,2.2,5.0,1.5,Iris-virginica
6.9,3.2,5.7,2.3,Iris-virginica
5.6,2.8,4.9,2.0,Iris-virginica
7.7,2.8,6.7,2.0,Iris-virginica
6.3,2.7,4.9,1.8,Iris-virginica
6.7,3.3,5.7,2.1,Iris-virginica
7.2,3.2,6.0,1.8,Iris-virginica
6.2,2.8,4.8,1.8,Iris-virginica
6.1,3.0,4.9,1.8,Iris-virginica
6.4,2.8,5.6,2.1,Iris-virginica
7.2,3.0,5.8,1.6,Iris-virginica
7.4,2.8,6.1,1.9,Iris-virginica
7.9,3.8,6.4,2.0,Iris-virginica
6.4,2.8,5.6,2.2,Iris-virginica
6.3,2.8,5.1,1.5,Iris-virginica
6.1,2.6,5.6,1.4,Iris-virginica
7.7,3.0,6.1,2.3,Iris-virginica
6.3,3.4,5.6,2.4,Iris-virginica
6.4,3.1,5.5,1.8,Iris-virginica
6.0,3.0,4.8,1.8,Iris-virginica
6.9,3.1,5.4,2.1,Iris-virginica
6.7,3.1,5.6,2.4,Iris-virginica
6.9,3.1,5.1,2.3,Iris-virginica
5.8,2.7,5.1,1.9,Iris-virginica
6.8,3.2,5.9,2.3,Iris-virginica
6.7,3.3,5.7,2.5,Iris-virginica
6.7,3.0,5.2,2.3,Iris-virginica
6.3,2.5,5.0,1.9,Iris-virginica
6.5,3.0,5.2,2.0,Iris-virginica
6.2,3.4,5.4,2.3,Iris-virginica
5.9,3.0,5.1,1.8,Iris-virginica"""


# ============================================================================
# Part 1: 辅助函数定义
# ============================================================================

def iris_type(s):
    """
    将鸢尾花标签转换为整数类别。
    兼容字节串 (从文件读取) 和普通字符串 (从 StringIO 读取)。
    例如: b'Iris-setosa' / 'Iris-setosa' -> 0
    """
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    it = {'Iris-setosa': 0, 'Iris-versicolor': 1, 'Iris-virginica': 2}
    return it[s]


def classifier():
    """
    构建 SVM 分类器。

    参数说明:
      C:     误差项惩罚系数, 默认值为1。
             C 越大, 对误分类的惩罚越大, 趋向于对训练集全分对,
             训练集准确率很高但泛化能力弱 (过拟合)。
             C 越小, 对误分类的惩罚越小, 允许容错, 泛化能力较强。
      kernel: 'linear' 为线性核; 'rbf' 为高斯核。
      decision_function_shape:
             'ovr' (one vs rest): 一个类别与其他类别进行划分。
             'ovo' (one vs one):  类别两两之间进行划分, 用二分类模拟多分类。
    """
    # 另一种可选的配置 (高斯核):
    # clf = svm.SVC(C=0.8, kernel='rbf', gamma=50, decision_function_shape='ovr')
    clf = svm.SVC(C=0.5,
                  kernel='linear',
                  decision_function_shape='ovr')
    return clf


def train(clf, x_train, y_train):
    """
    训练 SVM 模型。
    参数:
      clf:      SVM 分类器
      x_train:  训练集特征向量
      y_train:  训练集目标值 (使用 ravel() 展平)
    """
    clf.fit(x_train, y_train.ravel())


def show_accuracy(a, b, tip):
    """
    比较预测值 a 和真实值 b 是否相等，计算准确率并打印。
    参数:
      a:   预测值
      b:   真实值
      tip: 提示信息 (如 'traing data' / 'testing data')
    """
    acc = a.ravel() == b.ravel()
    print('%s Accuracy:%.3f' % (tip, np.mean(acc)))


def print_accuracy(clf, x_train, y_train, x_test, y_test):
    """
    打印训练集和测试集上的模型评估指标:
      1. score() 直接输出准确率
      2. predict() + show_accuracy() 对比原始结果与预测结果
      3. decision_function() 输出样本到各分割平面的距离
    """
    # 分别打印训练集和测试集的准确率
    # score(x_train, y_train): 返回模型在给定数据上的平均准确率
    print('training prediction:%.3f' % (clf.score(x_train, y_train)))
    print('test data prediction:%.3f' % (clf.score(x_test, y_test)))

    # 原始结果与预测结果进行对比
    # predict(): 对样本进行预测，返回样本类别
    show_accuracy(clf.predict(x_train), y_train, 'traing data')
    show_accuracy(clf.predict(x_test), y_test, 'testing data')

    # 计算决策函数的值，表示各样本到各分割平面(超平面)的距离
    # 对于 OVR 三分类: 每行3个值, 分别代表到类别0/1/2超平面的距离
    print('decision_function:\n', clf.decision_function(x_train))


def draw(clf, x, y, x_test):
    """
    可视化 SVM 分类结果。
    绘制分类背景色块、训练样本点和测试样本点。

    参数:
      clf:    训练好的 SVM 分类器
      x:      全部样本特征 (用于确定绘图范围)
      y:      全部样本标签 (用于着色)
      x_test: 测试集特征 (以空心圆标注)
    """
    iris_feature = ['sepal length', 'sepal width', 'petal length', 'petal width']

    # ---- 1. 生成网格采样点 ----
    x1_min, x1_max = x[:, 0].min(), x[:, 0].max()          # 第0列的范围
    x2_min, x2_max = x[:, 1].min(), x[:, 1].max()          # 第1列的范围
    x1, x2 = np.mgrid[x1_min:x1_max:200j, x2_min:x2_max:200j]  # 生成 200×200 网格
    grid_test = np.stack((x1.flat, x2.flat), axis=1)       # 将网格展平为 (40000, 2) 的测试点矩阵
    print('grid_test:\n', grid_test)

    # ---- 2. 计算网格点到决策面的距离 ----
    z = clf.decision_function(grid_test)
    print('the distance to decision plane:\n', z)

    # ---- 3. 预测网格点的分类 ----
    grid_hat = clf.predict(grid_test)                      # 预测分类值, 得到 [0, 0, ..., 2, 2, 2]
    print('grid_hat:\n', grid_hat)
    grid_hat = grid_hat.reshape(x1.shape)                  # 重塑为与 x1 一致的形状 (200, 200)

    # ---- 4. 绘图 ----
    cm_light = mpl.colors.ListedColormap(['#A0FFA0', '#FFA0A0', '#A0A0FF'])
    cm_dark = mpl.colors.ListedColormap(['g', 'b', 'r'])

    plt.pcolormesh(x1, x2, grid_hat, cmap=cm_light)                                  # 背景色块: 分类区域
    plt.scatter(x[:, 0], x[:, 1], c=np.squeeze(y), edgecolor='k', s=50, cmap=cm_dark) # 全部样本点 (实心)
    plt.scatter(x_test[:, 0], x_test[:, 1], s=120, facecolor='none', zorder=10)       # 测试样本点 (空心圆)
    plt.xlabel(iris_feature[0], fontsize=20)
    plt.ylabel(iris_feature[1], fontsize=20)
    plt.xlim(x1_min, x1_max)
    plt.ylim(x2_min, x2_max)
    plt.title('SVM in iris data classification', fontsize=30)
    plt.grid()
    plt.savefig('svm_iris_classification_result.png', dpi=150, bbox_inches='tight')
    print('分类结果图已保存为: svm_iris_classification_result.png')
    plt.close()


# ============================================================================
# Part 2: 主程序
# ============================================================================

def main():
    """
    主函数: 按实验步骤依次执行:
      1) 加载数据（直接从内嵌的 IRIS_CSV 字符串读取）
      2) 数据分割
      3) 构建模型
      4) 训练模型
      5) 评估模型
      6) 可视化
    """
    # ---------- Step 1: 数据准备 ----------
    # 从内嵌的 CSV 字符串读取数据, 结构与原文件完全一致
    data = np.loadtxt(StringIO(IRIS_CSV),
                      dtype=float,
                      delimiter=',',
                      converters={4: iris_type})

    # data 为二维数组, shape=(150, 5)
    print(f"数据形状: {data.shape}")

    # 数据分割 —— 按列切分: 前4列为特征 x, 第5列为标签 y
    x, y = np.split(data, (4,), axis=1)

    # 取前两列特征用于可视化 (花萼长度、花萼宽度)
    # 若要使用全部4列特征，改为: x = x[:, 0:4]
    x = x[:, 0:2]

    # 划分训练集和测试集
    x_train, x_test, y_train, y_test = model_selection.train_test_split(
        x,                  # 样本特征集
        y,                  # 样本标签
        random_state=1,     # 随机数种子 (保证结果可复现)
        test_size=0.3       # 测试样本占比 30%
    )

    # ---------- Step 2: 模型搭建 ----------
    clf = classifier()

    # ---------- Step 3: 模型训练 ----------
    train(clf, x_train, y_train)

    # ---------- Step 4: 模型评估 ----------
    print_accuracy(clf, x_train, y_train, x_test, y_test)

    # ---------- Step 5: 可视化 ----------
    draw(clf, x, y, x_test)


# ============================================================================
# 程序入口
# ============================================================================
if __name__ == '__main__':
    main()
